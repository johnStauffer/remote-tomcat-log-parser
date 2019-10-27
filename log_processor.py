#!/usr/bin/env python

import datetime
import logging as logger
import os
import re

import file_utils
import parse_logs


class LogProcessor:
    def __init__(self):
        self.fu = file_utils.FileUtil()
        self.parser = parse_logs.Parser()
        self.log_dir = 'logs/'
        logger.basicConfig(filename='application_logs.log', level=logger.INFO)

    def get_access_list(self, file_list, upper_date=None, lower_date=None, request_str=None, request_method=None):
        """
        Convert a list of files containing apache-tomcat access logs into a list of access log entries. Can be
        filtered by request method (ie. POST, GET) and by request string (eg. the rest endpoint)

        :param list[str] file_list: list of files containing apache access logs. The file name should include filepath
            and be formatted as <microservice>_access_log.<YYYY-MM-DD-HH>.log
        :param datetime upper_date: optional parameter for filtering the returned list by datetime
        :param datetime lower_date: optional parameter for filtering the returned list by datetime
        :param str request_str: optional filter parameter for filtering the list by a specific request
        :param str request_method: optional filter parameter for filtering the list by request (eg. POST, GET)
        :rtype: list[str]
        :return: list of access log entries in string form
        """

        logger.info('\nThis may take a minute\n\t retrieving access list')
        # if a datetime range is provided, filter the files by that range
        if upper_date and lower_date:
            file_list = self.filenames_by_datetime(upper_date, lower_date, file_list)
        # get a combined access log list from all files in the list
        access_list = self.make_combined_list(file_list)
        # if a datetime range is provided, filter the access log list by that range
        if upper_date and lower_date:
            access_list = self.date_filter_logs(access_list, upper_date, lower_date)
            print()
        # if a request method and filter string are provided filter the list by request method and request string
        if request_method and request_str:
            access_list = self.filter_list_by_request(request_str, request_method, access_list)
        return access_list

    def filter_list_by_request(self, request_list, request_str, request_method):
        """
        given a list of request filter the list for a specified request string and method
        :param list[] request_list: unfiltered list of requests
        :param str request_str: matching string for list to be filtered by
        :param request_method: mathing method for list to be filtered by
        :rtype:  list[str]
        :return: filtered list of requests
        """
        filtered = []
        # iterate through list of requests
        for request in request_list:
            if request['request']:
                # strip query params off of request string
                sanitized_request = self.sanitize_request(request['request'])
                #
                method = request['method']
                if sanitized_request == request_str and request_method == method:
                    filtered.append(request)
        return filtered

    def map_files_time(self, files):
        """

        :param files:
        :return:
        """
        map = {}
        date_pattern = '(?<=\.)(.*?)(?=\.log)'
        for file in files:
            match = re.search(date_pattern, file)
            if match:
                date_str = match.group()
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%d-%H')
                map[file] = dt
        return map

    def make_combined_list(self, files):
        logger.warning('Making combined list of logs, this may take a while')
        list = []
        # take list of files and combine all access_log entries into a single list
        for file in files:
            filepath = self.log_dir + file
            response_list = self.parser.log_to_list(filepath)
            if response_list:
                list.extend(response_list)
        # sort list by datetime
        sorted_list = sorted(list, key=lambda k: k['datetime'])
        return sorted_list

    def date_filter_logs(self, access_list, upper_date, lower_date):
        logger.warning('Filtering log list by datetime, this may take a while')
        filtered_list = list(filter(lambda log: upper_date >= log['datetime'] >= lower_date, access_list))
        return filtered_list

    def is_in_trunc_daterange(self, compare_date, upper_date, lower_date):
        """
        Determine if date is inside datetime range but give an hour of leeway.

        :param datetime compare_date:
        :param datetime upper_date:
        :param datetime lower_date:
        :rtype: bool
        :return: True, if in daterange, False if outside daterange
        """
        try:
            if upper_date >= compare_date >= lower_date:
                return True
            else:
                return False
        except:
            return False

    def filenames_by_datetime(self, upper_date, lower_date, files):
        """
        Filter a list of accesslogs by datetime

        :param datetime upper_date:
        :param datetime lower_date:
        :param list[str] files:
        :rtype: list[str]
        :return: filtered list
        """
        date_map = self.map_files_time(files)
        filtered_list = []
        for key in date_map:
            key_dt = date_map[key]
            if self.is_in_trunc_daterange(key_dt, upper_date, lower_date):
                filtered_list.append(key)
        return filtered_list

    def sanitize_request(self, request_string):
        """
        given a url, remove query params and return just the request

        :param request_string: url to be sanitized
        :rtype: str
        :return: request without query parameters
        """
        pattern = '^(.*?)(?=(\?|[0-9]))'
        sanitized_request = None
        match = re.search(pattern, request_string)
        if match:
            sanitized_request = match.group(0)
        return sanitized_request


class LogEvaluator(object):
    def __init__(self):
        pass


def string_to_datetime(date_string):
    dt = None
    try:
        dt = datetime.datetime.strptime(date_string, '%d/%b/%Y:%H:%M:%S')
    except Exception as inst:
        print('Could not convert datetime: %s \n Error: %s, %s' % (date_string, type(inst), inst.args))
    return dt


if __name__ == '__main__':
    lp = LogProcessor()
    fu = file_utils.FileUtil()
    files = fu.list_local_files('logs/')
    # print('Please enter datetime (dd/Mon/YYYY:hh:mm:ss')
    lowerdate = string_to_datetime('18/Dec/2016:13:00:00')
    upperdate = string_to_datetime('06/Jan/2017:15:00:00')
    access_list = lp.get_access_list(files, lower_date=lowerdate, upper_date=upperdate)
    print(access_list)


file = os.open('file_path_here')
newlineRegex = ''
for line in file:


