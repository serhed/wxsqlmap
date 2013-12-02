# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import threading
import wx


class ScanThread(threading.Thread):

    def __init__(self, window, reqScan=None):
        threading.Thread.__init__(self)
        self.window = window
        self.reqScan = reqScan
        self.interface = window.get_interface()
        self.options = window.get_all_options()
        self.taskID = self.interface.get_taskID()
        self.threadEvent = threading.Event()
        self.threadEvent.clear()

        self.scan_method = None
        self.scanMethods = {
            'dump': self.scan_dump, 'schema': self.scan_schema
        }

        if reqScan is None:
            self.scan_method = self.scan_default
        elif reqScan in self.scanMethods:
            self.scan_method = self.scanMethods[reqScan]
        else:
            self.threadEvent.set()

        self.logNew = []
        self.logOld = []
        self.logDiff = []
        self.dumpDict = dict()

    def run(self):
        wx.CallAfter(self.window.SetStatusText, 'running...')
        self.scan_method()
        wx.CallAfter(self.window.enable_run, True)

    def stop(self):
        self.interface.scan_stop()
        self.threadEvent.set()

    def terminated(self):
        return self.interface.scan_status()['status'] == 'terminated'

    def successful(self):
        return self.interface.scan_status()['returncode'] == 0

    def notify(self, success=False):
        wx.CallAfter(self.window.SetStatusText,
                     'completed'+('!' if success else ' incorrect!'))

    def logging(self):
        self.logOld, self.logNew = self.logNew, self.interface.scan_log()['log']
        self.lenNew, self.lenOld = len(self.logNew), len(self.logOld)

        if self.lenNew - self.lenOld > 0:
            self.logDiff = self.logNew[self.lenOld:]

            for log in self.logDiff:
                text = '[%s] [%s]\n%s\n\n' % (log['time'], log['level'], log['message'])
                wx.CallAfter(self.window.add_new_log, text)

    def follow_scan(self):
        while not self.threadEvent.isSet():
            self.logging()
            if self.terminated():
                break
            self.threadEvent.wait(1.0)

    def scan_default(self):
        self.interface.scan_start(self.options)
        self.follow_scan()
        if self.successful():
            wx.CallAfter(self.window.receive_data, self.interface.scan_data())
        self.notify(self.successful())

    def scan_schema(self):
        self.interface.scan_start(self.options)
        self.follow_scan()
        if self.successful():
            wx.CallAfter(self.window.update_tree,
                         self.interface.scan_data()['data'][-1])
        self.notify(self.successful())

    def set_dump_dict(self, dumpDict):
        self.dumpDict = dumpDict

    def scan_dump(self):
        success = True
        for db in self.dumpDict.keys():
            for tbl in self.dumpDict[db].keys():
                self.options['db'] = db
                self.options['tbl'] = tbl
                self.options['col'] = self.dumpDict[db][tbl]

                self.interface.scan_start(self.options)
                self.follow_scan()
                if self.successful():
                    self.append_grid()
                else:
                    success = False
                    wx.CallAfter(self.window.SetStatusText, "Error while dumping table "+tbl)
        self.notify(success)

    def append_grid(self):
        data = []
        scanData = self.interface.scan_data()['data']

        tbl = self.options['tbl']
        cols = []
        # cols = self.options['col'].split(',')

        if scanData:
            scanData = scanData[-1]['value']

            cols = [col for col in scanData.keys() if col != '__infos__']

            for c in cols:
                data.append(scanData[c]['values'])

            data = zip(*data)
            wx.CallAfter(self.window.add_grid, data, tbl, cols)
