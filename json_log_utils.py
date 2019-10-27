#!/usr/bin/env python

import file_utils
import json


class JsonUtil(object):
    def __init__(self):
        self.json_dir = '../json'
        self.fu = file_utils.FileUtil();

    def json_from_log(self, log_filepath):
        list = None
        try:
            # Retrieve log file from a local directory
            file = self.fu.get_local_file(log_filepath)
            if file:
                #
                list = json.loads(file)
        except:
            print('Error making json from log: ' + log_filepath)
        return list

    def get_json_list(self, file_name):
        list = None
        file_path = self.json_dir + file_name
        file = self.fu.get_local_file(file_path)
        if file:
            list = json.loads(file[0])
        return list
