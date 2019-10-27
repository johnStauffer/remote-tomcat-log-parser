#!/usr/bin/env python

import re
import datetime
import logging as logger
import json
import os


class Parser(object):
    def __init__(self):
        self.log_dir = 'logs/'

    def data_from_line(self, line, is_strings=False):
        # get response status and response time
        response_data = self.get_response_data(line)
        if not response_data:
            return None
        # make hash for line
        data = {}
        # values need to be strings if creating json from data
        if is_strings:
            data['datetime'] = self.get_datetime(line).strftime('%d/%b/%Y:%H:%M:%S')
            data['response'] = self.get_response_status(response_data)
            data['responseTime'] = self.get_response_time(response_data)
        else:
            data['datetime'] = self.get_datetime(line)
            data['response'] = int(self.get_response_status(response_data))
            data['responseTime'] = int(self.get_response_time(response_data))
        # these values will always be strings
        data['host'] = self.get_host(line)
        data['host'] = self.get_host(line)
        data['request'] = self.get_request_string(line)
        data['method'] = self.get_rest_method(line)
        return data

    def lines_to_list(self, file, is_strings=False):
        list = []
        for line in file:
            data_hash = self.data_from_line(line, is_strings)
            if data_hash:
                list.append(data_hash)
        return list

    def log_to_list(self, file_path):
        list = None
        if os.path.exists(file_path):
            file = open(file_path)
            list = self.lines_to_list(file)
        else:
            logger.error('could not open: ' + file_path)
        return list

    def list_to_json(self, list):
        json_list = json.dumps(list)
        return json_list

    def write_list_to_file(self, list, file_name):
        file_path = 'json/%s' % file_name
        fo = open(file_path, 'w')
        fo.write(list)
        fo.close()

    def get_log_file(self, file_name):
        file = None
        try:
            filepath = 'logs/' + file_name
            logger.info('Opening: %s' % filepath)
            # open file and make it readable
            raw_file = open(filepath)
            file = raw_file.readlines()
            # close file after extracting lines
            raw_file.close()
        except Exception as inst:
            logger.error('Could Not Open File: %s' % type(inst))
        return file

    def get_request_string(self, line):
        request = None
        # regex pattern for extracting request string
        request_pattern = '((?<="POST )|(?<="GET )|(?<="PUT ))(.*?)(?=\ )'
        match = re.findall(request_pattern, line)
        if match:
            request = match[0][1]
        return request

    def get_rest_method(self, line):
        method = None
        # regex pattern for extracting request method
        method_pattern = 'POST|PUT|GET'
        # get rest method with regex
        match = re.findall(method_pattern, line)
        if match[0]:
            method = match[0]
        return method

    def get_response_data(self, line):
        response_list = None
        # regex pattern for extracting response and response time
        response_pattern = r'((?<=\ )(201|200|400|404|401)((.*?)(?=\ \")))'
        # get response with regex
        match = re.search(response_pattern, line)
        response = self.string_from_match(match)
        if response:
            # split response string into list and return response code and response time
            response_list = response.split()[0:2]
        return response_list

    def get_response_time(self, response_data):
        response_time = None
        try:
            response_time = response_data[1]
        except Exception:
            pass
        return response_time

    def get_response_status(self, response_data):
        response_status = None
        if response_data:
            response_status = response_data[0]
        return response_status

    def get_host(self, line):
        # regex pattern for extracting host
        host_pattern = r'^(.*?)(?=\ )'
        # get host with regex
        match = re.search(host_pattern, line)
        return self.string_from_match(match)

    def string_from_match(self, match):
        match_str = None
        if match:
            match_str = match.group(0)
        return match_str

    def jsonify_file(self, file_name):
        try:
            # Remove '.log' from filename and replace with '.json'
            json_file_name = file_name[:-4] + '.json' # This will be the new filename
            # Retrieve file
            file = self.get_log_file(file_name)
            # Make a list of access log tuples from lines in file
            list = self.lines_to_list(file, True)
            # Convert list of tuples to json
            json_list = self.list_to_json(list)
            # Make new file and write json into it
            self.write_list_to_file(json_list, json_file_name)
            logger.info('%s parsed to JSON\n' % file_name)
            return True
        except Exception as inst:
            logger.error('Could not convert file to json: %s' % type(inst))
            return False

    def get_log_file_names(self, path):
        log_files = os.listdir(path)
        return log_files

    def process_logs(self, log_names):
        count = 0
        for log in log_names:
            success = self.jsonify_file(log)
            if success:
                count+=1
        return count


    def process_all_logs(self):
        log_list = self.get_log_file_names(self.log_dir)
        for log in log_list:
            self.jsonify_file(log)

    def get_datetime(self, line):
        # regex pattern for extracting datetime
        datetime_pattern = r'(?<=\[)(.*?)(?=\ )'
        # get datetime with regex
        match = re.search(datetime_pattern, line)
        dt = datetime.datetime.strptime(self.string_from_match(match), "%d/%b/%Y:%H:%M:%S")
        return dt
