import numpy as np
import pandas as pd


class File:
    def __init__(self, data):
        if isinstance(data, pd.Series):
            data = data.values
        if isinstance(data, np.ndarray):
            assert data.shape[0] == 13
            self.name, self.time, self.size, self.type, self.path, self.url = data
        elif isinstance(data, dict):
            keys = data.keys()
            self.attrs = [
                'name',
                'time',
                'size',
                'type',
                'path',
                'url',
            ]
            for attr in self.attrs:
                if attr in keys:
                    setattr(self, attr, data[attr])
        else:
            raise('init func accept only type: ndarray, dict or Series')
    def get(self, attr):
        assert hasattr(self, attr), '引数"%s"か定義することがありません'
        return getattr(self, attr)
    def isDir(self):
        return self.type == "FOLDER"