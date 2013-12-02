# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx
from wx.lib.wordwrap import wordwrap
import sqlmap

class Info(wx.AboutDialogInfo):

    def __init__(self, window):
        wx.AboutDialogInfo.__init__(self)
        self.Name = 'wxSqlmap'
        self.Version = '0.1'
        self.Copyright = 'Copyright 2013 Mehmet Öztürk'
        self.Description = wordwrap(self.Name +
                                    ' is a graphical user interface for '
                                    'the penetration testing tool sqlmap.\n\n'
                                    'The Developer assumes no liability and is not '
                                    'responsible for any misuse or damage caused by this program.\n\n'
                                    'Please read the disclaimer of sqlmap. ',
                                    350, wx.ClientDC(window))
        self.Developers = ['Mehmet Öztürk']

        with open(sqlmap.modulePath()+'/wxsqlm/gpl.txt', 'r') as r:
            licenseText = r.read()

        self.Licence = wordwrap(licenseText, 500, wx.ClientDC(window))