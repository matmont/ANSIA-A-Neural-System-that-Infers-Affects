import pickle
import warnings
import neurokit2 as nk
import numpy as np
from scipy.signal import filtfilt, butter


def warn(*args, **kwargs):
    pass


warnings.warn = warn


def downsampling_mean(data, start_freq, end_freq):
    """
    This method resamples a data from the frequency 'start_freq' to 'end_freq' with the "mean" method.

    :param data: data to resample
    :param start_freq: start frequency
    :param end_freq: end frequency
    :return: resampled data
    """
    if start_freq < end_freq:
        print("You should use this function to downsample a timeseries...")
        return None
    else:
        n_to_collapse = int(start_freq / end_freq)
        counter = 0
        s = 0
        new_data = []
        for i in range(len(data)):
            s += data[i]
            counter += 1
            if counter == n_to_collapse:
                new_data.append(s / n_to_collapse)
                s = 0
                counter = 0

        return np.array(new_data)


def downsampling_last(data, start_freq, end_freq):
    """
    This method resamples a data from the frequency 'start_freq' to 'end_freq' with the "last" method.

    :param data: data to resample
    :param start_freq: start frequency
    :param end_freq: end frequency
    :return: resampled data
    """
    if start_freq < end_freq:
        print("You should use this function to downsample a timeseries...")
        return None
    else:
        n_to_collapse = int(start_freq / end_freq)
        new_data = []
        for i in range(len(data)):
            if i % n_to_collapse == 0:
                new_data.append(data[i])

        return np.array(new_data)


# This function computes the coefficient of the IIR filter
def butter_lowpass(cutoff, fs, order=5):
    """
    This function computes the coefficient of the IIR low pass filter of cutoff 'cutoff' for a signal that has
    frequency 'fs' and with order (of the filter) 'order'.

    :param cutoff: cutoff frequency of the lowpass filter
    :param fs: frequency of the signal to filter
    :param order: order of the filter
    :return: coefficients b and a of the IIR filter
    """
    nyq = 0.5 * fs
    normalized_cutoff = cutoff / nyq
    b, a = butter(order, normalized_cutoff, btype='low', analog=False, output='ba')
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    """
    This function create an IIR low pass filter and applies it to the signal.

    :param data: signal to filter
    :param cutoff: cutoff frequency of the filter
    :param fs: frequency of the signal to filter
    :param order: order of the filter
    :return: filtered data
    """
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data, axis=0)
    return y


def process_thread_implementation(data=None, prediction_queue=None, model=None):
    """
    This thread take data from the 'master_thread_implementation' and applies to them the processing for the
    Machine Learning training.

    :param data: data from the 'master_thread_implementation'
    :param prediction_queue: queue linked to PredictionPage
    :param model: Machine Learning classifier
    """
    timestamps = []
    hr = []
    eda = []

    # Remember that EDA and HR are at the same frequency, so here they have the same length
    for i in range(len(data['HR'])):
        hr.append(data['HR'][i][1])
        eda.append(data['EDA'][i][1])
        timestamps.append(data['EDA'][i][0])

    # Filtering EDA
    eda = butter_lowpass_filter(eda, 1, 64, order=4)
    # Applying NeuroKit2 on EDA
    signal, process = nk.eda_process(eda, sampling_rate=64)
    scr = signal['EDA_Phasic'].to_numpy()
    scr = scr.reshape((scr.shape[0], 1))
    scl = signal['EDA_Tonic'].to_numpy()
    scl = scl.reshape((scl.shape[0], 1))

    hr = np.array(hr).reshape((len(hr), 1))

    # Now we have to resample the signals to 4 Hz
    hr = downsampling_mean(hr, 64, 4)
    scr = downsampling_mean(scr, 64, 4)
    scl = downsampling_mean(scl, 64, 4)
    timestamps = downsampling_last(timestamps, 64, 4)

    # Let's standardize the data.
    means = []
    stds = []
    # If we have 30 seconds of data (30 seconds * 4 Hz)
    if len(scr) >= 4 * 30:
        try:
            # Let's see if the mean and stds are already computed and use them
            f = open("statistics.pkl", 'rb')
            statistics = pickle.load(f)
            means = statistics['means']
            stds = statistics['stds']
            f.close()
        except FileNotFoundError:
            # If this is the first time that a 'process_thread' have 30 seconds of data we have to
            # compute std and mean and use them for every data of the future
            statistics = {}
            means = np.array([np.mean(scr), np.mean(scl), np.mean(hr)])
            stds = np.array([np.std(scr), np.std(scl), np.std(hr)])
            statistics['means'] = means
            statistics['stds'] = stds
            f = open("statistics.pkl", 'wb')
            pickle.dump(statistics, f)
            f.close()

    # Now we should concatenate belong axis 1 to create the X
    # this is the order of the features (depends by the training process)
    X = np.concatenate((scr, scl, hr), axis=1)
    if X.shape[0] >= 4 * 30:
        X = (X - means) / stds
        print("Mean of X: ", np.mean(X))
        print("Std of X: ", np.std(X))

    X = X.reshape((1, X.shape[0], X.shape[1]))

    predictions = model.predict(X)
    predictions = predictions.reshape((-1,))
    predictions = list(predictions)
    timestamps = list(timestamps)
    # We take only the last second of predictions
    if len(predictions) >= 4:
        predictions = predictions[-4:]
        timestamps = timestamps[-4:]

    prediction_queue.put([timestamps, predictions])
