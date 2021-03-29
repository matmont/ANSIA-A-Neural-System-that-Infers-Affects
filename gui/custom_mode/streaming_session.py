import csv
from concurrent.futures import ThreadPoolExecutor

from gui.custom_mode import csv_writer


def streaming_session(enabled_sensors=None, run_signal=None, reads_queue=None, path=None):
    """
    This method reads data from a group of Shimmer devices.

    :param path: location where to save .csv files with data
    :param enabled_sensors: list of enabled sensors of the stream
    :param run_signal: signal to handle thread end
    :param reads_queue: queue to communicate with PlotsScreen
    :return:
    """

    # Thread pool for CSV writing
    pool = ThreadPoolExecutor(10)  # 5 types of Shimmer * 2

    master_timestamp = -1  # timestamp RTC of the first sensor's first packet (for synchronization purposes)
    shifts = {}
    headers = {}

    # Start Streaming to all sensors
    for sensor in enabled_sensors:
        # Retrieve the Header
        headers[sensor.shimmer_type] = sensor.data_packet_header()
        # in that context we will edit the packet, so let's tune the fieldnames of the Header
        headers[sensor.shimmer_type] = headers[sensor.shimmer_type][3:len(headers[sensor.shimmer_type])]
        headers[sensor.shimmer_type].insert(0, "Synced RTC Timestamp")
        # Creating CSV files and printing header and sampling_rate
        filename = path + "/" + sensor.shimmer_type + '.csv'
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers[sensor.shimmer_type])
            writer.writeheader()
            writer.writerow({headers[sensor.shimmer_type][0]: sensor.sampling_rate})

        # start the streaming
        sensor.start_bt_streaming()

    for sensor in enabled_sensors:
        # Let's compute SHIFTS (time difference) between master sensor and the other (for synchronization purposes)
        data = sensor.read_data_packet_bt(calibrated=True)
        # If the master timestamp isn't set yet
        if master_timestamp == -1:
            master_timestamp = data[1]
        if sensor.shimmer_type not in shifts.keys():
            shifts[sensor.shimmer_type] = data[2] - master_timestamp

    # Let's loop while run_signal is set. It will be unset when user will close the plot window
    while run_signal.is_set():
        read = {}
        for sensor in enabled_sensors:
            # Read a group of available packets
            n_of_packets, packets = sensor.read_data_packet_extended(calibrated=True)
            if n_of_packets > 0:
                # For the plot we are interested only at the last packet of the group
                packet = packets[-1].copy()
                # Let's synchronize the timestamp
                synced_timestamp = packet[2] - shifts[sensor.shimmer_type]
                # Engineering the packet
                packet.pop(0)  # removing local timestamp
                packet.pop(0)  # removing timestamp rtc of the first packet
                packet.pop(0)  # removing timestamp rtc of the current packet (not synched)
                packet.insert(0, synced_timestamp)
                # Put the packet into 'read' that's a dict that will go into the queue
                read[sensor.shimmer_type] = packet

                # Send all packets to CSV writer for .csv writing
                pool.submit(csv_writer.csv_writer, sensor.shimmer_type, headers[sensor.shimmer_type],
                            shifts[sensor.shimmer_type], packets, path)
            else:
                read[sensor.shimmer_type] = None

        # Check if is all empty
        all_empty = True
        for key, value in read.items():
            if value:
                all_empty = False

        if not all_empty:
            # This line make sure that in the queue there is only one element with
            # the latest reads
            with reads_queue.mutex:
                reads_queue.queue.clear()
            reads_queue.put(read)

    # Stop streaming
    for sensor in enabled_sensors:
        sensor.stop_bt_streaming()
    pool.shutdown(wait=True)
