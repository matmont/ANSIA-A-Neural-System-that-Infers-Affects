import datetime
from concurrent.futures import ThreadPoolExecutor

from gui.wesad_mode import process_thread_implementation
from shimmer import util

from shimmer.ppg_to_hr import PPGtoHRAlgorithm

WINDOW_LIMIT = 30  # second
PREDICTION_FREQUENCY = 1  # second


def master_thread_implementation(shimmers=None, run_signal=None, prediction_queue=None, model=None):
    """
    'master_thread_implementation' implements the reads from the Shimmer devices (it is used only
    with the Shimmer3 GSR+).

    :param shimmers: list of Shimmer3 objects
    :param run_signal: Event that control the execution of this thread
    :param prediction_queue: queue that is used to communicate with PredictionPage
    :param model: classifier used for the predictions
    :return:
    """

    # Debug line
    for shimmer in shimmers:
        shimmer.print_object_properties()

    # Pool of workers for processing threads
    processing_pool = ThreadPoolExecutor(1)

    # Synchronization between Shimmer's timestamps
    master_timestamp = -1
    shifts = {}

    # Library that converts PPG to Heart Rate
    PPG2HR = PPGtoHRAlgorithm(sampling_rate=64, number_of_beats_to_average=1, use_last_estimate=1)

    # Start streaming from all sensors
    for shimmer in shimmers:
        shimmer.start_bt_streaming()

    # Synchronization
    for shimmer in shimmers:
        data = shimmer.read_data_packet_bt(calibrated=True)
        if master_timestamp == -1:
            master_timestamp = data[1]
        if shimmer.shimmer_type not in shifts.keys():
            shifts[shimmer.shimmer_type] = data[2] - master_timestamp

    """
        This dict should be like:
        {
            'EDA': [lett1, lett2, lett...], where lettX = [timestampX, valueX]
            'HR': [lett1, lett2, lett...], 
        }
    """
    reads = {'EDA': [], 'HR': []}
    tmp_reads = {'EDA': [], 'HR': []}
    while run_signal.is_set():
        # Here, this thread should read data and check when to make a prediction
        # We want to read 64 packets (1 second) before go ahead with the code execution
        # Note that PREDICTION FREQUENCY is the frequency of prediction expressed in seconds
        # 64 is the sample frequency of the Shimmer3 GSR+
        readden = len(tmp_reads['EDA'])
        while readden < int(PREDICTION_FREQUENCY * 64):
            for shimmer in shimmers:
                n_of_packets, packets = shimmer.read_data_packet_extended(calibrated=True)
                readden += n_of_packets
                if n_of_packets > 0:
                    for packet in packets:
                        # Synchronizing timestamp
                        synced_timestamp = packet[2] - shifts[shimmer.shimmer_type]
                        timestamp = datetime.datetime.fromtimestamp(synced_timestamp).strftime("%H:%M:%S.%f")[:-3]

                        # From here the behaviour is different based on shimmer type
                        if shimmer.shimmer_type == util.SHIMMER_GSRplus:
                            ppg = packet[3]
                            eda = packet[4]
                            hr = PPG2HR.ppg_to_hr(ppg, synced_timestamp * 1000)[0]
                            print("HR: ", hr)
                            tmp_reads['HR'].append([timestamp, hr])
                            tmp_reads['EDA'].append([timestamp, eda])

        # Get the first 64 packets from reads
        how_much = int(PREDICTION_FREQUENCY * 64)
        to_append_HR = tmp_reads['HR'][0:how_much]
        to_append_EDA = tmp_reads['EDA'][0:how_much]
        tmp_reads['HR'] = tmp_reads['HR'][how_much:]
        tmp_reads['EDA'] = tmp_reads['EDA'][how_much:]

        # We want the last 30 second data (WINDOW_LIMIT = 30 and 64 is the sample rate)
        # Here we get rid of the first second data if the are more than 30 seconds of data
        if len(reads['HR']) >= int(64 * WINDOW_LIMIT) and len(reads['EDA']) >= int(64 * WINDOW_LIMIT):
            reads['HR'] = reads['HR'][int(PREDICTION_FREQUENCY * 64):]
            reads['EDA'] = reads['EDA'][int(PREDICTION_FREQUENCY * 64):]
        # Here we append the new 1 second of data
        reads['HR'] = reads['HR'] + to_append_HR
        reads['EDA'] = reads['EDA'] + to_append_EDA

        # Send data to preprocessing before prediction
        processing_pool.submit(process_thread_implementation.process_thread_implementation, reads,
                               prediction_queue,
                               model)
    processing_pool.shutdown(wait=True)

    # Sending stop streaming to all sensors
    for shimmer in shimmers:
        shimmer.stop_bt_streaming()