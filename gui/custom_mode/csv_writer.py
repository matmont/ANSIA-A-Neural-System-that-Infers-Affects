import csv
import datetime


def csv_writer(shimmer_type=None, header=None, shift=None, packets=None, filename=None):
    """
    'csv_writer' appends the reads from a group of packets to a .csv file located
    in 'filename/shimmer_type.csv'.

    :param shimmer_type: the type of the Shimmer from which packets are from
    :param header: the header of the packets
    :param shift: the amount of shift time, computed during synchronization
    :param packets: packets to append into the .csv file
    :param filename: folder where .csv file is located
    """
    path = filename + "/" + shimmer_type + '.csv'
    with open(path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        for packet in packets:
            synced_timestamp = packet[2] - shift
            packet.pop(0)
            packet.pop(0)
            packet.pop(0)
            packet.insert(0, datetime.datetime.fromtimestamp(synced_timestamp).strftime("%H:%M:%S.%f")[:-3])
            info = {}
            for i in range(len(header)):
                info[header[i]] = packet[i]

            writer.writerow(info)
