#!/usr/bin/env python

import paramiko as pk
import re
import os


class Connection():
    def connect(self, host, username, password):
        """Create a connection to a specified remote host

        :param str host: ip for remote host
        :param str username: remote host username
        :param str password: remote host password
        :rtype SSHClient:
        :return: a new client for remote host or None if connection/authentication fails
        """
        try:
            # Create ssh client
            ssh = pk.SSHClient();
            # Override requirement for ssh key
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(
                pk.AutoAddPolicy())
            # Create ssh connection
            ssh.connect(hostname=host, username=username, password=password)
            client = ssh
            return client
        # TODO handle exceptions at a higher level than logging
        except Exception as inst:
            print(type(inst))
            print('Authentication Failed for host: %s username: %s' % (self.host, self.username))
            return None


class FileUtil(object):
    def __init__(self):
        self.host = '10.3.230.130'
        self.username = ''
        self.client = None
        self.logged_in = False
        self.ftp = None

    def connect(self, host, username, password):
        """ Check if client connection has already been initialized

        :param str host: ip for remote host
        :param str username: remote host username
        :param str password: remote host password
        :rtype bool: return True if connected to remote host, False otherwise
        """
        if not self.client and not self.logged_in:
            # Connect
            self.client = Connection().connect(host=host, username=username, password=password)
            # Check is connected successfully, will return None if unsuccessful
            if self.client:
                # Initialize ftp
                self.ftp = self.__inti_ftp(self.client)
                # Set loggged in flag
                self.logged_in = True
        return self.logged_in

    def __inti_ftp(self, ssh):
        ftp = None
        try:
            # create ftp from ssh connection
            ftp = ssh.open_sftp()
        except Exception as inst:
            print('Initialization of FTP Failed: %s %s' % (type(inst), inst))
        return ftp

    def list_files_in_rem_directory(self, file_path, regex=None, iteration=0):
        """
        Using remote connection, return a list of files in a directory on the remote host. List of files returned
        can be filtered with the optional regex parameter.

        :param str file_path:
        :param str regex:
        :param int iteration:
        :return: list
        """
        command = 'ls %s' % file_path
        files = []
        if regex:
            command = command + ' | grep %s' % regex
        try:
            return_str = None
            # check for client
            if self.client:
                stdin, stdout, stderr = self.client.exec_command(command)
                while not stdout.channel.exit_status_ready():
                    # Print stdout data when ready
                    if stdout.channel.recv_ready():
                        # Retrieve the first 1024 bytes
                        return_str = stdout.channel.recv(1024)
                        while stdout.channel.recv_ready():
                            # Retrieve the next 1024 bytes
                            return_str += stdout.channel.recv(1024)
                if return_str:
                    # split string from stdout into a list
                    byte_files = return_str.splitlines()
                    # Convert each list item from byte form into strings and add directory path
                    for file in byte_files:
                        str_file = file_path + file.decode('utf-8')
                        files.append(str_file)
                    print('File names retrieved on iteration {}/30'.format((iteration + 1)))
                # Sometimes multiple attempts are needed
                elif iteration < 30:
                    self.list_files_in_rem_directory(file_path, regex, iteration + 1)
        except Exception as inst:
            print('Error retrieving file names from directory: %s \n\tError: %s' % (file_path, type(inst)))
        return files

    def list_local_files(self, directory):
        """
        List files inside a local directory

        :param directory: container path of files to be listed
        :return: list of files in the directory
        """
        files = os.listdir(directory)
        return files

    def get_local_file(self, file_path):
        """
        retrieve a file from a local directory and make it into a usable form

        :param file_path: path of file to be retrieved
        :return: a list of lines contained in the file
        :rtype list[str]:
        """

        file = None
        try:
            raw_file = open(file_path)
            file = raw_file.readlines()
            raw_file.close()
        except Exception as inst:
            print('Could not open %s: %s' % (file_path, type(inst)))
            return inst
        return file

    def retrieve_file(self, remote_file_path, local_destination):
        """
        retrieve a file from a remote directory and store it locally

        :param remote_file_path: path to file stored remotely
        :param local_destination: path and filename for retrieved file to be stored. ie: /usr/local/test.txt
        :return: if the file is retrieved and stored successfully return True, else False
        """
        try:
            if (self.ftp):
                self.ftp.get(remote_file_path, local_destination)
                print('Successfully retrieved %s from %s' % (remote_file_path, self.host))
                return True
            else:
                print('Ftp not yet initialized. Please create remote connection')
                return False
        except Exception as inst:
            print('Error retrieving file names from directory: %s\n\tError: %s' % (remote_file_path, type(inst)))

    def filename_from_path(self, filepath):
        """
        given a filepath, only return the file name

        :param filepath: complete filepath for file
        :rtype str:
        :return: filename
        """

        #Regex pattern to strip filename from filepath
        regex_pattern = '([^\/]*$)'
        match_str = None
        #Regex search to get filename from path
        match = re.search(regex_pattern, filepath)
        #If match is found, make the match into a string
        if match:
            match_str = match.group()
        return match_str

    def retrieve_files(self, remote_file_list, local_destination):
        """
        given a list of file paths, retrieve them from a remote host

        :param list[str] remote_file_list: list of filepaths to be retrieved
        :param local_destination: directory for retrieved files to be stored in
        :return: true if successful, else false
        """
        files_retrieved = 0
        #Check that there is connection for the remote host
        if (self.ftp):
            for file in remote_file_list:
                try:
                    filename = self.filename_from_path(file)
                    # directory file will be stored in while maintaining the same name
                    destination_path = local_destination + filename
                    # retrieve file and store it in the directory above
                    self.retrieve_file(file, destination_path)
                    files_retrieved += 1
                except Exception as inst:
                    print('Could not retrieve: %s \n\tError : %s' % (file, type(inst)))
            print('File retrieval complete. {} files retrieved'.format(files_retrieved))
            return True
        else:
            print('Ftp not yet initialized. Please create remote connection')
            return False

    def is_logged_in(self):
        """
        Check if the ssh client has been initialized
        :rtype: bool
        :return: True if logged in, otherwise false
        """
        return self.logged_in

    def __del__(self):
        if self.client:
            self.client.close()
            print('SSH and FTP clients closed')
