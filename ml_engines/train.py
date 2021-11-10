'''
====================================
 :mod:`train` {Extract data from DB and conduct pre-processing
Use modeling modules to train data}
====================================
'''

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import const.const_path as cpath
import seaborn as sns
from keras_preprocessing import sequence
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import ml_engines.build_model as build_model
from tensorflow.keras.models import load_model

__all__ = ['train']

def multivariate_data(dataset, target, start_idx, end_idx, history_size, target_size, step, single_step=False):
    data = []
    label = []
    start_idx = start_idx + history_size
    if end_idx is None:
        end_idx = len(dataset) - target_size
    for i in range(start_idx, end_idx):
        indices = range(i - history_size, i, step)
        data.append(dataset[indices])
        if single_step:
            label.append(target[i + target_size])
        else:
            label.append(target[i:i+target_size])
    return np.array(data), np.array(label)

def norm(x, t):
        return (x - t['mean']) / t['std']

def train(prediction):
    '''
    :return: keras model
    '''
    # Data preprocessing
    path = cpath.path
    fn = open(path["train_data_path"], 'rt', encoding='ISO-8859-1')
    total_data = pd.read_csv(fn)
    total_data = total_data.drop(columns=['country', 'country_code', 'date'])
    print(total_data)
    # if prediction == "download":
    #     total_data = total_data.drop(columns=['country', 'country_code', 'date', 'upload_kbps'])
    # else:
    #     total_data = total_data.drop(columns=['country', 'country_code', 'date', 'download_kbps'])

    # Train Test split
    train_dataset = total_data.sample(frac=0.8, random_state=0)
    test_dataset = total_data.drop(train_dataset.index)
    sns.pairplot(train_dataset[["download_kbps", "upload_kbps", "total_tests", "distance_miles"]], diag_kind="kde")
    plt.show()
    train_stats = train_dataset.describe()
    if prediction == "download":
        train_stats.pop("download_kbps")
        train_labels = train_dataset.pop('download_kbps')
        test_labels = test_dataset.pop('download_kbps')
    elif prediction == "upload":
        train_stats.pop("upload_kbps")
        train_labels = train_dataset.pop('upload_kbps')
        test_labels = test_dataset.pop('upload_kbps')
    train_stats = train_stats.transpose()
    normed_train_data = norm(train_dataset, train_stats)
    normed_test_data = norm(test_dataset, train_stats)
    train_len = len(train_dataset.keys())

    # Model Training
    model = build_model.model_regression(train_dataset, train_labels, train_len, prediction)
    loss, mae, mse = model.evaluate(test_dataset, test_labels, verbose=2)
    print("average error rate of testset: {:5.2f}".format(mae))
    example_batch = test_dataset[:10]
    print(example_batch)
    example_result = model.predict(example_batch)
    print(example_result)

train('upload')

def predict(data, predict):
    path = cpath.path
    if predict == 'upload':
        loaded_model = load_model(path["upload_model_path"])
    else:
        loaded_model = load_model(path["download_model_path"])

    pred_result = loaded_model.predict(data).flatten()
    return pred_result

    # def bm():
    #     model = keras.Sequential([
    #         layers.Dense(64, activation='relu', input_shape=[len(train_dataset.keys())]),
    #         layers.Dense(64, activation='relu'),
    #         layers.Dense(1)
    #     ])
    #
    #     optimizer = tf.keras.optimizers.RMSprop(0.001)
    #
    #     model.compile(loss='mse',
    #                   optimizer=optimizer,
    #                   metrics=['mae', 'mse'])
    #     return model
    #
    # # example_batch = normed_train_data[:10]
    # # example_result = model.predict(example_batch)
    #
    # class PrintDot(keras.callbacks.Callback):
    #     def on_epoch_end(self, epoch, logs):
    #         if epoch % 100 == 0: print('')
    #         print('.', end='')
    #
    # EPOCHS = 20
    #
    # model = bm()
    #
    # early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
    #
    # history = model.fit(normed_train_data, train_labels, epochs=EPOCHS,
    #                     validation_split=0.2, verbose=0, callbacks=[early_stop, PrintDot()])
    #
    # loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    #
    # print("테스트 세트의 평균 절대 오차: {:5.2f} MPG".format(mae))


    # example_batch = normed_train_data[:10]
    # example_result = model.predict(example_batch)
    #
    # loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    # test_predictions = model.predict(normed_test_data).flatten()

    # plt.scatter(test_labels, test_predictions)
    # plt.xlabel('True Values [download_kbps]')
    # plt.ylabel('Predictions [download_kbps]')
    # plt.axis('equal')
    # plt.axis('square')
    # plt.xlim([0, plt.xlim()[1]])
    # plt.ylim([0, plt.ylim()[1]])
    # _ = plt.plot([-100, 100], [-100, 100])
    # plt.show()
    #
    # error = test_predictions - test_labels
    # plt.hist(error, bins=25)
    # plt.xlabel("Prediction Error [MPG]")
    # _ = plt.ylabel("Count")
    # plt.show()
    # train_split = len(total_data.index)
    # get_download = total_data.drop(columns=['upload_kbps'])
    # get_upload = total_data.drop(columns=['download_kbps'])
    # get_download = get_download.values
    # gd_mean = get_download[:train_split].mean()
    # gd_std = get_download[:train_split].std(axis=0)
    # get_download = (get_download - gd_mean) / gd_std
    # print(get_download)
    # print(get_download.shape)
    # x_train, y_train = multivariate_data(get_download, get_download[:,1], 0, train_split, 720, 72, 6, single_step=True)
    # x_val, y_val = multivariate_data(get_download, get_download[:,1], 0, train_split, 720, 72, 6, single_step=True)
    # total_data['X'] = total_data.apply(lambda r: [r['total_tests']] + [r['distance_miles']], axis=1)
    # total_data['Y'] = total_data.apply(lambda r: [r['download_kbps']] + [r['upload_kbps']], axis=1)




# which model to use prediction -> download, upload

train('download')