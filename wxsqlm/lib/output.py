# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import sqlmap
import wx
import wx.html

BEGIN = """<!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        """
BODY = """</head>
        <body>"""
END = """</body>
        </html>"""

TAG_LIST = ['title', 'style', 'div', 'ul', 'li', 'details', 'summary', 'table', 'tr', 'th', 'td']

TAG = {}

TEXTAREA = ['\n<textarea readonly>', '</textarea>\n']

def gen_tag(t):
    return ['\n<'+t+'>', '</'+t+'>\n']


class ScanOutput(wx.Dialog):
    def __init__(self, parent, id, taskID, apiUrl, title='Scan Output'):
        wx.Dialog.__init__(self, parent, id, title,
                           style=wx.DEFAULT_DIALOG_STYLE |
                                 wx.MINIMIZE_BOX |
                                 wx.MAXIMIZE_BOX |
                                 wx.CLOSE_BOX |
                                 wx.RESIZE_BORDER)

        self.SetWindowStyle(self.GetWindowStyle() | wx.CLOSE_BOX)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.window = wx.html.HtmlWindow(self)
        self.window.LoadPage(apiUrl+'/scan/'+taskID+'/data')

        sizer.Add(self.window, 1, wx.EXPAND)
        self.Layout()
        self.SetSizer(sizer)


class HtmlGenerator():
    def __init__(self, target, data, log, tree=None, dumps=None):
        self.target = target
        self.data = data
        self.log = log
        self.tree = tree
        self.dumps = dumps
        self.css = ''

        for t in TAG_LIST:
            TAG[t] = gen_tag(t)

        css = sqlmap.modulePath()+'/wxsqlm/css/style.css'

        with open(css, 'r') as inp:
            self.css = inp.read()

    def get_html_output(self):
        output = BEGIN
        output += TAG['title'][0] + self.target + TAG['title'][1]
        output += TAG['style'][0] + self.css + TAG['style'][1]
        output += BODY

        genTree = not self.tree is None
        genDumps = not self.dumps is None

        if genTree or genDumps:
            output += u'\n<div class="treeDump">\n'
            if genTree:
                output += self.gen_tree()
            if genDumps:
                output += u'\n<div class="dump">\n'
                output += TAG['details'][0]
                output += TAG['summary'][0] + 'table dumps' + TAG['summary'][1]
                output += self.gen_dumps()
                output += TAG['details'][1]
                output += TAG['div'][1]
            output += TAG['div'][1]

        output += self.gen_data_log()
        output += END

        return output

    def gen_tree(self):
        tmp = u'\n<div class="tree">\n'

        for db in self.tree.keys():
            tmp += TAG['details'][0]
            tmp += TAG['summary'][0] + 'Database: ' + db + TAG['summary'][1]
            tmp += TAG['ul'][0]

            for tbl in self.tree[db].keys():
                tmp += TAG['li'][0]
                if len(self.tree[db][tbl].keys()):
                    tmp += u'<details open="open">\n'
                else:
                    tmp += TAG['details'][0]
                tmp += TAG['summary'][0] + tbl + TAG['summary'][1]

                cols = self.tree[db][tbl].keys()
                if len(cols) > 0:
                    tmp += TAG['ul'][0]

                    for col in cols:
                        tmp += TAG['li'][0] + col + ', ' + self.tree[db][tbl][col] + TAG['li'][1]

                    tmp += TAG['ul'][1]
                tmp += TAG['details'][1]
                tmp += TAG['li'][1]


            tmp += TAG['ul'][1]
            tmp += TAG['details'][1]

        tmp += TAG['div'][1]

        return tmp

    def gen_dumps(self):
        tmp = u''
        tmp += TAG['ul'][0]

        for tbl in self.dumps.keys():
            tmp += TAG['li'][0]
            tmp += TAG['details'][0]
            tmp += TAG['summary'][0] + tbl + TAG['summary'][1]
            tmp += TAG['table'][0] + TAG['tr'][0]
            for col in self.dumps[tbl]['cols']:
                tmp += TAG['th'][0] + col + TAG['th'][1]

            tmp += TAG['tr'][1]

            for row in self.dumps[tbl]['data']:
                tmp += TAG['tr'][0]
                for item in row:
                    tmp += TAG['td'][0] + item.encode('ascii', 'replace') + TAG['td'][1]
                tmp += TAG['tr'][1]

            tmp += TAG['tr'][1] + TAG['table'][1]
            tmp += TAG['details'][1]
            tmp += TAG['li'][1]

        tmp += TAG['ul'][1]

        return tmp

    def gen_data_log(self):
        tmp = u'\n<div class="results">\n'
        tmp += TAG['details'][0]
        tmp += TAG['summary'][0] + 'information' + TAG['summary'][1]
        tmp += u'\n'+TAG['div'][0]

        for data in self.data['data']:
            try:
                if data['type'] == 0:
                    val = data['value']
                    tmp += u'dbms: ' + val[0]['dbms']+'<br>\n'
                    tmp += u'dbms_version: ' + str(val[0]['dbms_version'])+'<br>\n'
                    tmp += u'parameter: ' + val[0]['parameter']+'<br>\n'
                    tmp += u'payloads:\n'+TAG['ul'][0]
                    for k in val[0]['data'].keys():
                        tmp += TAG['li'][0] + val[0]['data'][k]['payload']+TAG['li'][1]
                    tmp += TAG['ul'][0]
            except Exception, e:
                print e

        tmp += u'\n'+TAG['div'][1]

        if len(self.data['error'])>0:
            tmp += TAG['summary'][0] + 'error output' + TAG['summary'][1]
            tmp += TEXTAREA[0]
            for error in self.data['error']:
                tmp+=str(error)+'\n'
            tmp += TEXTAREA[1]

        tmp += TAG['details'][1]
        tmp += TAG['details'][0]
        tmp += TAG['summary'][0] + 'log' + TAG['summary'][1]
        tmp += TEXTAREA[0]
        for log in self.log:
            tmp += u'[%s] [%s]\n%s\n\n' % (log['time'], log['level'], log['message'])
        tmp += TEXTAREA[1]
        tmp += TAG['details'][1]
        tmp += TAG['div'][1]

        return tmp
