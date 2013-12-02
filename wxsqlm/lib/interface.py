# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx
import lib.utils.api as api
import requests as req
import json
import threading
import socket


class SqlmapServer(threading.Thread):
    def __init__(self, parent, host, port):
        self.host = host
        self.port = port
        self.parent = parent

        self.server = None
        threading.Thread.__init__(self)
        self.threadEvent = threading.Event()
        self.threadEvent.clear()
        self.server = None

    def run(self):
        try:
            api.server(self.host, self.port)
        except socket.error, e:
            error = str(e)
            msg = error[error.index(']')+1:]
            title = error[:error.index(']')+1]

            if 'Errno 98' in error:
                msg = 'The Server is already running\n\nmessage: ' + msg
            else:
                msg = 'message: ' + msg

            wx.CallAfter(self.parent.OnServer, msg, title)


class SqlmapInterface:
    def __init__(self, apiUrl, headers):
        self.apiUrl = apiUrl
        self.headers = headers
        self.taskID = None

    def req_post(self, urlParam, data):
        return req.post(self.apiUrl+urlParam,
                        json.dumps(data),
                        headers=self.headers).json()

    def req_qet(self, urlParam):
        return req.get(self.apiUrl+urlParam,
                       headers=self.headers).json()


    def scan_start(self, options):
        self.req_post('/scan/'+self.taskID+'/start', options)

    def scan_data(self):
        return self.req_qet('/scan/'+self.taskID+'/data')

    def scan_log(self):
        return self.req_qet('/scan/'+self.taskID+'/log')

    def scan_stop(self):
        self.req_qet('/scan/'+self.taskID+'/stop')

    def scan_status(self):
        return self.req_qet('/scan/'+self.taskID+'/status')

    def option_list(self):
        return self.req_qet('/option/'+self.taskID+'/list')

    def task_new(self):
        self.taskID = self.req_qet('/task/new')['taskid']
        return self.taskID

    def get_taskID(self):
        return self.taskID

    def task_delete(self):
        return self.req_qet('/task/'+self.taskID+'/delete')
