import pandas as pd
import numpy as np
import tempfile
import tarfile
import os

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve


def _extract(src_file, dst_dir='.'):
    cur_dir = os.getcwd()
    os.chdir(dst_dir)
    file = tarfile.open(src_file, 'r:gz')
    file.extractall()
    file.close()
    os.chdir(cur_dir)


def _cached_dataset_load(url, dataset_name, train_file, test_file):
    dir_path = os.path.join('datasets', dataset_name)
    train_path = os.path.join(dir_path, train_file)
    test_path = os.path.join(dir_path, test_file)
    if not (os.path.exists(train_path) and os.path.exists(test_path)):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_descriptor, file_path = tempfile.mkstemp()
        os.close(file_descriptor)
        urlretrieve(url, file_path)
        _extract(file_path, dir_path)
        os.remove(file_path)
    return pd.read_csv(train_path), pd.read_csv(test_path)


def titanic():
    url = 'https://storage.mds.yandex.net/get-devtools-opensource/233854/titanic.tar.gz'
    dataset_name, train_file, test_file = 'titanic', 'train.csv', 'test.csv'
    return _cached_dataset_load(url, dataset_name, train_file, test_file)


def amazon():
    url = 'https://storage.mds.yandex.net/get-devtools-opensource/250854/amazon.tar.gz'
    dataset_name, train_file, test_file = 'amazon', 'train.csv', 'test.csv'
    return _cached_dataset_load(url, dataset_name, train_file, test_file)
