#!/usr/bin/env python

__author__ = "John Stauffer"
__version__ = "1.0"
__email__ = "jstauffer001@regis.ed"


from tkinter import *
from tkinter import ttk
from subprocess import call
from file_utils import FileUtil, Connection
import parse_logs as pl
import logging as logger


class Login(ttk.Frame):
    def __init__(self, parent, file_util):
        # ttk.Frame.__init__(self, parent)
        self.parent = Toplevel(parent)
        self.host = '10.3.230.130'
        self.username = None
        self.file_util = file_util
        self.initUI()
        self.logged_in = False

    def initUI(self):
        # Main Window
        self.parent.title("Log Tool")

        # Host Field
        host_frame = ttk.Frame(self.parent)
        host_frame.pack(fill=X)

        host_lbl = Label(host_frame, text='host', width=7)
        host_lbl.pack(side=LEFT, padx=5, pady=5)

        self.host_entry = ttk.Entry(host_frame)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(fill=X, padx=5, expand=YES)

        # Username field
        un_frame = ttk.Fram(self.parent)
        un_frame.pack(fill=X)

        un_lbl = Label(un_frame, text='Username', width=7)
        un_lbl.pack(side=LEFT, padx=5, pady=5)

        self.un_entry = ttk.Entry(un_frame)
        self.un_entry.pack(fill=X, padx=5, expand=YES)

        # Password field
        pw_frame = ttk.Frame(self.parent)
        pw_frame.pack(fill=X)

        pw_lbl = Label(pw_frame, text='Password', width=7)
        pw_lbl.pack(side=LEFT, padx=5, pady=5)

        self.pw_entry = ttk.Entry(pw_frame, show='*')
        self.pw_entry.pack(fill=X, padx=5, expand=YES)

        # Submit button field
        submit_frame = ttk.Frame(self.parent)
        submit_frame.pack(fill=X)

        self.fail_label = Label(submit_frame, text='', width=7, background='#E5E7E9')
        self.fail_label.pack(side=LEFT, padx=5, pady=5)

        submitButton = ttk.Button(submit_frame, text='Submit', command=self.submit)
        submitButton.pack(side=BOTTOM, expand=YES)
        self.centerWindow()

    # USE THIS WHEN MAKING LOGIN WINDOW
    def show(self):
        # Dont register
        self.parent.deiconify()
        # Wait until window is destroyed then return file utility
        self.parent.wait_window()
        fu = self.file_util
        return fu

    def centerWindow(self):
        w = 300
        h = 130
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        self.parent.geometry(dim_str)

    def validate(self, login):
        self.host = login['host']
        self.username = login['username']
        password = login['password']
        response = self.file_util.connect(username=self.username, host=self.host, password=password)
        if response and not self.logged_in:
            logger.info("Successfully Logged in \n\t SSH and FTP connections Initialized")
            self.parent.destroy()
        elif self.logged_in:
            logger.info('Already logged in')
            if self.log_window:
                self.log
            return self.file_util
        else:
            logger.error("Authentication failed, try again")
            self.un_entry.delete(0, 'end')
            self.pw_entry.delete(0, 'end')
            self.fail_label.config(text='Try Again')

    def submit(self):
        login = {}
        login['host'] = self.host_entry.get()
        login['username'] = self.un_entry.get()
        login['password'] = self.pw_entry.get()
        self.validate(login)


class LogList(ttk.Frame):
    def __init__(self, parent, fileutil=None):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.fu = fileutil
        self.parser = pl.Parser()
        self.log_dir = 'logs/'
        # TODO Finish json in finder
        self.json_dir = 'json/'
        self.init_ui()

    def get_logs(self):
        self.logs = self.fu.list_local_files(self.log_dir)

    def init_ui(self):
        # Set dimensions and center window
        w = 500
        h = 500
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        self.parent.geometry(dim_str)
        self.pack(side=TOP, fill=BOTH, expand=YES)
        # Make frame for title and refresh button
        labelframe = ttk.Frame(self)
        labelframe.pack(fill=X)
        # Label and Refresh Button
        self.label = ttk.Label(labelframe, text='Available Logs', width=10)
        self.refreshBtn = ttk.Button(labelframe, text='Refresh', command=self.refresh_logs)
        self.finderBtn = ttk.Button(labelframe, text='Show in Finder', command=self.show_logs_in_finder)
        self.jsonFinderBtn = ttk.Button(labelframe, text='Show json in Finder', command=self.show_json_in_finder)
        self.label.pack(side=LEFT, padx=3, pady=5)
        self.refreshBtn.pack(side=LEFT, expand=YES)
        self.finderBtn.pack(side=LEFT, expand=YES)
        self.jsonFinderBtn.pack(side=LEFT, expand=YES)
        # Jsonify Button
        btnFrame = ttk.Frame(self)
        btnFrame.pack(fill=X, side=BOTTOM)
        self.json_btn = ttk.Button(btnFrame, text='Convert to json', width=12, command=self.jsonify_files)
        self.json_btn.pack(side=LEFT, pady=5, padx=5, expand=YES)
        # Make frame for list and scrollbar
        listFrame = ttk.Frame(self)
        listFrame.pack(fill=BOTH, expand=YES)
        self.vsb = Scrollbar(listFrame, orient='vertical')
        self.lb = Listbox(listFrame, selectmode=MULTIPLE, yscrollcommand=self.vsb.set)
        self.lb.pack(side=LEFT, fill=BOTH, expand=YES)
        self.vsb.pack(side=RIGHT, fill=Y)
        self.refresh_logs()

    def show_json_in_finder(self):
        call(['open', '-R', self.json_dir])

    def show_logs_in_finder(self):
        call(['open', '-R', self.log_dir])

    def refresh_logs(self):
        # Check that listbox has been initialized
        if self.lb:
            # Retrieve logs and clear old logs from listbox
            self.get_logs()
            self.lb.delete(0, END)
            # Iterate through and insert retrieved logs into listbox
            self.lb_map = {}
            key = 0  # map listbox cursor position to filename
            for log in self.logs:
                self.lb.insert(END, log)
                # add map entry for position and log name
                self.lb_map[key] = log
                # increment key for next iteration
                key += 1

            logger.info('Logs refreshed')
        else:
            logger.warning('Listbox not initialized or no logs to be found')

    def jsonify_files(self):
        selections = self.lb.curselection()
        sel_list = []
        for selection in selections:
            sel_list.append(self.lb_map.get(selection))
        process_count = self.parser.process_logs(sel_list)
        # Make popup
        popup = Toplevel(self.parent)
        w = 270
        h = 75
        # Center window
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        popup.geometry(dim_str)
        # Tell user how many logs were processed
        msg_frame = ttk.Frame(popup)
        msg_frame.pack(fill=BOTH, expand=YES)
        msg_txt = str.format('{} Logs converted to json', process_count)
        msg_label = ttk.Label(msg_frame, text=msg_txt)
        msg_label.pack(side=TOP, pady=5, padx=5)
        # Buttons to close popup of view logs in Finder
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill=BOTH, expand=YES)
        close_btn = ttk.Button(btn_frame, width=10, text='Close', command=popup.destroy)
        json_btn = ttk.Button(btn_frame, width=15, text='Show in Finder', command=self.show_json_in_finder)
        close_btn.pack(side=LEFT, pady=5, padx=5)
        json_btn.pack(side=RIGHT, pady=5, padx=5)


class RemoteRetrieve(ttk.Frame):
    def __init__(self, parent, file_util):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.fu = file_util
        self.initUI()

    def initUI(self):
        w = 300
        h = 75
        # Center window
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        self.parent.geometry(dim_str)
        self.entry_frame = ttk.Entry(self.parent)
        self.entry_frame.pack(fill=X, expand=YES)
        self.mservice_label = ttk.Label(self.entry_frame, width=20, text='Micro-Service')
        self.mservice_entry = ttk.Entry(self.entry_frame, width=50)
        self.mservice_label.pack(side=LEFT, pady=5, padx=5, expand=YES)
        self.mservice_entry.pack(side=RIGHT, pady=5, padx=5, expand=YES)
        # Submit button
        self.submit_frame = ttk.Frame(self.parent)
        self.submit_frame.pack(fill=BOTH, expand=YES)
        self.submit = ttk.Button(self.submit_frame, width=20, text='Submit', command=self.retreive_logs)
        self.submit.pack(side=TOP, expand=YES)

    def retreive_logs(self):
        logs = self.fu.list_files_in_rem_directory('/usr/local/logs/', '^_access_log')
        if len(logs) > 0:
            success = self.fu.retrieve_files(logs, 'logs/')
            if success:
                logger.info('Files successfully retrieved')
        print(logs)
        self.parent.destroy()
        pass


class HostUtilities(ttk.Frame):
    def __init__(self, parent, file_utility):
        self.parent = parent
        self.fu = file_utility
        self.initUI()

    def initUI(self):
        w = 300
        h = 75
        # Center screen
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        self.parent.geometry(dim_str)
        mainFrame = ttk.Frame(self)
        mainFrame.pack(fill=BOTH, expand=YES)

        self.retrieveLogsLbl = ttk.Label(mainFrame, text='Retrieve Access Logs')
        # TODO make retrieve window method
        self.retrieveLogsBtn = ttk.Button(mainFrame, text='Get Logs', width=10, command=self.retrieve_logs)
        self.retrieveLogsLbl.grid(row=0, pady=5, padx=5, column=0, sticky=W)
        self.retrieveLogsBtn.grid(row=0, pady=5, padx=5, column=1, sticky=W)



    def retrieve_logs(self):
        self.retrieve_window = Toplevel(self.parent)
        self.retrieve = RemoteRetrieve(self.retrieve_window, self.fu)


class ActionMenu(ttk.Frame):
    def __init__(self, parent):
        """
        initialize action menu
        :param parent:
        :param file_util file_util:
        """
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.fu = FileUtil()
        self.logged_in = False
        self.initUI()

    def initUI(self):
        self.pack(fill=BOTH, expand=YES)

        # Dimensions for window
        w = 405
        h = 150
        # Find screen dimensions
        scr_width = self.parent.winfo_screenwidth()
        scr_height = self.parent.winfo_screenheight()
        # Coordinates to place window
        x = (scr_width - w) / 2
        y = (scr_height - h) / 2
        # Format string for dimensions
        dim_str = ('%dx%d+%d+%d' % (w, h, x, y))
        self.parent.geometry(dim_str)

        mainFrame = ttk.Frame(self)
        mainFrame.pack(fill=BOTH, expand=YES)
        # Login
        self.logged_lbl = ttk.Label(mainFrame)
        logged_in = self.fu
        self.loginBTN = ttk.Button(mainFrame, text='Login', width=10, command=self.login)
        self.logged_lbl.grid(row=0, pady=5, padx=5, column=0, sticky=W)
        self.loginBTN.grid(row=0, pady=5, padx=5, column=1, sticky=W)
        # Show downloaded logs
        logsLbl = ttk.Label(mainFrame, text='View Locally Downloaded Logs')
        self.logsBtn = ttk.Button(mainFrame, text='View Logs', width=10, command=self.show_logs)
        logsLbl.grid(row=1, padx=5, pady=5, column=0, sticky=W)
        self.logsBtn.grid(row=1, padx=5, pady=5, column=1, sticky=W)
        # Show host utility
        hostUtilLbl = ttk.Label(mainFrame, text='Host Utilities')
        self.hostUtilBtn = ttk.Button(mainFrame, text='Utils', state=DISABLED, width=10, command=self.show_host_utils)
        hostUtilLbl.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.hostUtilBtn.grid(row=2, column=1, padx=5, pady=5, sticky=W)

    def check_logged_in(self):
        if self.fu:
            self.logged_in = self.fu.is_logged_in()
            lbl_text = 'Logged in to %s' % (self.fu.host)
            self.logged_lbl.config(text=lbl_text)
            self.loginBTN.pack_forget()
            self.hostUtilBtn.config(state=ACTIVE)
            return True
        else:
            self.logged_in = False
            self.logged_lbl.config(text='Not Logged in')

    def login(self):
        self.fu = Login(self.parent, self.fu).show()
        self.check_logged_in()

    def show_logs(self):
        self.log_window = Toplevel(self.parent)
        self.app = LogList(self.log_window, self.fu)

    def show_host_utils(self):
        self.hostUtil = Toplevel(self.parent)
        self.app = HostUtilities(parent=self.hostUtil, file_utility=self.fu)



def main():
    root = Tk()

    app = ActionMenu(root)
    root.mainloop()


if __name__ == '__main__':
    main()
