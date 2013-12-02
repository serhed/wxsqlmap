# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx
import wx.lib.filebrowsebutton as fbrows
import sqlmap
import os

LIST = ['this', 'options', 'conf', 'backup' 'topWindow', 'nb', 'btnOk', 'btnCancel', 'gridCount']

DEFAULTS = {
    'cpuThrottle': 5,
    'googlePage': 1,
    'risk': 1,
    'level': 1,
    'timeout': 30,
    'threads': 1,
    'verbose': 1,
    'api': True,
    'torType': u'HTTP',
    'retries': 3,
    'batch': True,
    'timeSec': 5,
    'csvDel': ',',
    'dumpFormat': 'CSV',
    'disableColoring': True,
    'tech': 'BEUSTQ',
    'saFreq': 0,
    'delay': 0,
    }

SIZE = (80, 24)


class Options(wx.Frame):

    def __init__(self, id, CONF):
        self.topWindow = wx.GetApp().TopWindow
        wx.Frame.__init__(self, self.topWindow, id, self.topWindow.GetTitle())
        self.conf = CONF

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.gridCount = 0

        self.nb = wx.Notebook(self, -1)
        self.nb.AddPage(self.p_request(), 'Request | Optimization')
        self.nb.AddPage(self.p_inj_de_tech(),
                        'Injection | Detection | Techniques')
        self.nb.AddPage(self.p_enumeration(), 'Enumeration ...')
        self.nb.AddPage(self.p_access(), 'Access')
        self.nb.AddPage(self.p_general(), 'General')

        for o in self.conf.keys():
            val = self.conf[o]

            if not val is None or val:
                if self.__dict__[o].GetValue() != val:
                    self.__dict__[o].SetValue(val)

        pnlButtons = wx.Panel(self, -1)
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        pnlButtons.SetSizer(sizerButtons)

        self.btnOk = wx.Button(pnlButtons, wx.ID_OK)
        self.btnCancel = wx.Button(pnlButtons, wx.ID_CANCEL)

        self.Bind(wx.EVT_BUTTON, self.OnButton, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnButton, id=wx.ID_CANCEL)

        sizerButtons.Add(self.btnOk)
        sizerButtons.Add(self.btnCancel)

        sizer.Add(self.nb, 1, wx.EXPAND)
        sizer.Add(pnlButtons, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.options = {}
        self.backup = {}

        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        wx.Frame.CenterOnScreen(self)

    def OnButton(self, event):
        if event.GetId() == wx.ID_OK:
            self.init_options()
            self.do_backup()
        else:
            self.Close()

        self.Update()
        self.Show(False)

    def OnCloseWindow(self, event):
        for o in self.backup.keys():
            try:
                self.__dict__[o].SetValue(self.backup[o])

            except Exception, e:
                if type(self.__dict__[o]) == wx.ListBox:
                    for i in self.backup[o]:
                        self.__dict__[o].SetSelection(i)
        self.Show(False)

    def do_backup(self):
        for o in self.__dict__.keys():
            if o not in LIST:
                try:
                    self.backup[o] = self.__dict__[o].GetValue()
                except:
                    if type(self.__dict__[o]) == wx.ListBox:
                        self.backup[o] = self.__dict__[o].GetSelections()

    def init_options(self):
        for o in self.__dict__.keys():
            if o not in LIST:

                self.backup[o] = self.__dict__[o]
                try:
                    val = self.__dict__[o].GetValue()

                    if type(val) == bool:
                        if o in DEFAULTS:
                            self.in_defaults(o, val)
                        else:
                            if val:
                                self.options[o] = val
                            else:
                                self.del_option(o)

                    elif type(val) == unicode:
                        if o in DEFAULTS:
                            self.in_defaults(o, val)
                        else:
                            if len(val) > 0:
                                self.options[o] = val
                            else:
                                self.del_option(o)

                    elif type(val) == int:
                        if o in DEFAULTS:
                            self.in_defaults(o, val)
                        else:
                            if val != 0:
                                self.options[o] = val
                            else:
                                self.del_option(o)

                except AttributeError:
                    if type(self.__dict__[o]) == wx.ListBox:
                        selections = self.__dict__[o].GetSelections()
                        tampers = ''
                        if len(selections) > 0:
                            for s in selections:
                                tampers += 'tamper/'+self.tamper.GetString(s)+','
                            tampers = tampers[:-1]
                            if tampers == 'tamper/':
                                tampers = ''
                            if len(tampers) > 0:
                                tampers = tampers.replace('tamper/,', '')
                                self.options[o] = tampers
                            else:
                                self.del_option(o)

    def in_defaults(self, o, val):
        if DEFAULTS[o]!= val:
            self.options[o] = val
        else:
            self.del_option(o)

    def del_option(self, o):
        try:
            del self.options[o]
        except KeyError:
            pass

    def get_options(self):
        return self.options

    def set_label(self, sizer, pnl, lbl, ctrl):
        text = wx.StaticText(pnl, -1, label=lbl)
        sizer.Add(text, (self.gridCount, 1), flag=wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(ctrl, (self.gridCount, 2), (1, 16), wx.EXPAND | wx.LEFT, 4)
        self.gridCount += 1

    def set_horizontal(self, comp1, comp2):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(comp1, flag=wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(comp2)
        return sizer

    def set_vertical(self, comp1, comp2):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(comp1, 0, wx.EXPAND)
        sizer.Add(comp2, 0, wx.EXPAND)
        return sizer

    def p_request(self):
        panel = wx.Panel(self.nb, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        sizerLeft = wx.GridBagSizer()
        sizerRight = wx.GridBagSizer()
        sizerTop = wx.BoxSizer(wx.HORIZONTAL)

        self.data = wx.TextCtrl(panel, -1, size=SIZE)
        self.data.SetToolTip(wx.ToolTip('Data string to be sent through POST'))
        self.set_label(sizerLeft, panel, 'data', self.data)

        self.pDel = wx.TextCtrl(panel, -1, size=SIZE)
        self.pDel.SetToolTip(wx.ToolTip('Character used for splitting parameter values'))
        self.set_label(sizerLeft, panel, 'param-del', self.pDel)

        self.cookie = wx.TextCtrl(panel, -1, size=SIZE)
        self.cookie.SetToolTip(wx.ToolTip('HTTP Cookie header'))
        self.set_label(sizerLeft, panel, 'cookie', self.cookie)

        self.loadCookies = wx.TextCtrl(panel, -1, size=SIZE)
        self.loadCookies.SetToolTip(wx.ToolTip('File containing cookies in Netscape/wget format'))
        self.set_label(sizerLeft, panel, 'load-cookies', self.loadCookies)

        self.dropSetCookie = wx.CheckBox(panel, -1, 'drop-set-cookie')
        self.dropSetCookie.SetToolTip(wx.ToolTip('Ignore Set-Cookie header from response'))
        sizerLeft.Add(self.dropSetCookie, (self.gridCount, 1))

        self.randomAgent = wx.CheckBox(panel, -1, 'random-agent')
        self.randomAgent.SetToolTip(wx.ToolTip('Use randomly selected HTTP User-Agent header'))
        sizerLeft.Add(self.randomAgent, (self.gridCount, 2))
        self.gridCount += 1

        self.agent = wx.TextCtrl(panel, -1, size=SIZE)
        self.agent.SetToolTip(wx.ToolTip('HTTP User-Agent header'))
        self.set_label(sizerLeft, panel, 'user-agent', self.agent)

        self.host = wx.TextCtrl(panel, -1, size=SIZE)
        self.host.SetToolTip(wx.ToolTip('HTTP Host header'))
        self.set_label(sizerLeft, panel, 'host', self.host)

        self.referer = wx.TextCtrl(panel, -1, size=SIZE)
        self.referer.SetToolTip(wx.ToolTip('HTTP Referer header'))
        self.set_label(sizerLeft, panel, 'referer', self.referer)

        self.headers = wx.TextCtrl(panel, -1, size=SIZE)
        self.headers.SetToolTip(wx.ToolTip('Extra headers (e.g. "Accept-Language: fr\nETag: 123")'))
        self.set_label(sizerLeft, panel, 'headers', self.headers)

        self.aType = wx.ComboBox(panel, -1, '', (0, 0), wx.DefaultSize,
                                 ['Basic', 'Digest', 'NTLM', ''], wx.CB_READONLY)
        self.aType.SetToolTip(wx.ToolTip('HTTP authentication type (Basic, Digest or NTLM)'))
        self.set_label(sizerLeft, panel, 'auth-type', self.aType)

        self.aCred = wx.TextCtrl(panel, -1, size=SIZE)
        self.aCred.SetToolTip(wx.ToolTip('HTTP authentication credentials (name:password)'))
        self.set_label(sizerLeft, panel, 'auth-cred', self.aCred)

        self.aCert = wx.TextCtrl(panel, -1, size=SIZE)
        self.aCert.SetToolTip(wx.ToolTip('HTTP authentication certificate (key_file,cert_file)'))
        self.set_label(sizerLeft, panel, 'auth-cert', self.aCert)

        self.skipUrlEncode = wx.CheckBox(panel, -1, 'skip-urlencode')
        self.skipUrlEncode.SetToolTip(wx.ToolTip('Skip URL encoding of payload data'))

        self.forceSSL = wx.CheckBox(panel, -1, 'force-ssl')
        self.forceSSL.SetToolTip(wx.ToolTip('Force usage of SSL/HTTPS'))

        self.hpp = wx.CheckBox(panel, -1, 'hpp')
        self.hpp.SetToolTip(wx.ToolTip('Use HTTP parameter pollution'))

        self.delay = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.delay.SetRange(0, 65535)
        self.delay.SetToolTip(wx.ToolTip('Delay in seconds between each HTTP request'))
        self.set_label(sizerLeft, panel, 'delay', self.delay)

        self.timeout = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.timeout.SetRange(0, 65535)
        self.timeout.SetValue(30)
        self.timeout.SetToolTip(wx.ToolTip('Delay in seconds between each HTTP request'))
        self.set_label(sizerLeft, panel, 'timeout', self.timeout)

        self.gridCount = 0

        self.retries = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.retries.SetRange(0, 65535)
        self.retries.SetValue(3)
        self.retries.SetToolTip(wx.ToolTip('Retries when the connection timeouts (default 3)'))
        self.set_label(sizerRight, panel, 'retries', self.retries)


        self.rParam = wx.TextCtrl(panel, -1, size=SIZE)
        self.rParam.SetToolTip(wx.ToolTip('Randomly change value for given parameter(s)'))
        self.set_label(sizerRight, panel, 'randomize', self.rParam)

        self.safUrl = wx.TextCtrl(panel, -1, size=SIZE)
        self.safUrl.SetToolTip(wx.ToolTip('URL address to visit frequently during testing'))
        self.set_label(sizerRight, panel, 'safe-url', self.safUrl)

        self.saFreq = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.saFreq.SetRange(0, 65535)
        self.saFreq.SetToolTip(wx.ToolTip('Test requests between two visits to a given safe URL'))
        self.set_label(sizerRight, panel, 'safe-freq', self.saFreq)

        self.evalCode = wx.TextCtrl(panel, -1, size=SIZE)
        self.evalCode.SetToolTip(wx.ToolTip('Evaluate provided Python code before the request '
                                            '(e.g. "import hashlib;id2=hashlib.md5(id).hexdigest()")'))
        self.set_label(sizerRight, panel, 'eval', self.evalCode)


        sizerTop.Add(sizerLeft, 0, wx.EXPAND)
        sizerTop.Add(sizerRight, 0, wx.EXPAND | wx.LEFT, 4)

        boxProxy = wx.StaticBox(panel, -1, 'Proxy')
        sizerBox = wx.StaticBoxSizer(boxProxy, wx.VERTICAL)

        tmp, self.gridCount = self.gridCount, 0

        sizerProxy = wx.GridBagSizer()

        self.ignoreProxy = wx.CheckBox(panel, -1, 'ignore-proxy')
        self.ignoreProxy.SetToolTip(wx.ToolTip('Ignore system default HTTP proxy'))
        sizerProxy.Add(self.ignoreProxy, (self.gridCount, 1))
        self.gridCount += 1

        self.proxy = wx.TextCtrl(panel, -1, size=SIZE)
        self.proxy.SetToolTip(wx.ToolTip('Use a HTTP proxy to connect to the target URL'))
        self.set_label(sizerProxy, panel, 'proxy', self.proxy)

        self.pCred = wx.TextCtrl(panel, -1, size=SIZE)
        self.pCred.SetToolTip(wx.ToolTip('HTTP proxy authentication credentials (name:password)'))
        self.set_label(sizerProxy, panel, 'proxy-cred', self.pCred)

        self.tor = wx.CheckBox(panel, -1, 'tor')
        self.tor.SetToolTip(wx.ToolTip('Use Tor anonymity network'))
        sizerProxy.Add(self.tor, (self.gridCount, 1))

        self.checkTor = wx.CheckBox(panel, -1, 'check-tor')
        self.checkTor.SetToolTip(wx.ToolTip('Check to see if Tor is used properly'))
        sizerProxy.Add(self.checkTor, (self.gridCount, 2))
        self.gridCount += 1

        self.torPort = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.torPort.SetToolTip(wx.ToolTip('Set Tor proxy port other than default'))
        self.torPort.SetRange(0, 65535)
        self.set_label(sizerProxy, panel, 'tor-port', self.torPort)

        self.torType = wx.ComboBox(panel, -1, 'HTTP', (0, 0), wx.DefaultSize,
                                   ['HTTP', 'SOCKS4', 'SOCKS5', ''], wx.CB_READONLY)
        self.torType.SetToolTip(wx.ToolTip('Set Tor proxy type (HTTP (default), SOCKS4 or SOCKS5)'))
        self.set_label(sizerProxy, panel, 'tor-type', self.torType)


        sizerBox.Add(sizerProxy)

        sizerRight.Add(sizerBox, (tmp, 1), (1, 15), wx.EXPAND)
        tmp += 1
        sizerRight.Add(self.skipUrlEncode, (tmp, 1))
        tmp += 1
        sizerRight.Add(self.forceSSL, (tmp, 1))
        tmp += 1
        sizerRight.Add(self.hpp, (tmp, 1))

        sizer.Add(sizerTop)
        sizer.Add(self.box_optimization(panel))

        return panel

    def box_optimization(self, panel):
        box = wx.StaticBox(panel, -1, 'Optimization')
        sizerBox = wx.StaticBoxSizer(box)

        sizerOpt = wx.GridBagSizer()
        self.gridCount = 0

        self.optimize = wx.CheckBox(panel, -1, 'optimize')
        self.optimize.SetToolTip(wx.ToolTip('Turn on all optimization switches'))
        sizerOpt.Add(self.optimize, (self.gridCount, 0))

        self.predictOutput = wx.CheckBox(panel, -1, 'predict-output')
        self.predictOutput.SetToolTip(wx.ToolTip('Predict common queries output'))
        sizerOpt.Add(self.predictOutput, (self.gridCount, 1))
        self.gridCount += 1

        self.keepAlive = wx.CheckBox(panel, -1, 'keep-alive')
        self.keepAlive.SetToolTip(wx.ToolTip('Use persistent HTTP(s) connections'))
        sizerOpt.Add(self.keepAlive, (self.gridCount, 0))

        self.nullConnection = wx.CheckBox(panel, -1, 'null-connection')
        self.nullConnection.SetToolTip(wx.ToolTip('Retrieve page length without actual HTTP response body'))
        sizerOpt.Add(self.nullConnection, (self.gridCount, 1))
        self.gridCount += 1

        lthreads = wx.StaticText(panel, -1, label='threads')
        self.threads = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.threads.SetRange(1, 10)
        self.threads.SetToolTip(wx.ToolTip('Max number of concurrent HTTP(s) requests (default 1)'))
        sizerOpt.Add(lthreads, (self.gridCount, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        sizerOpt.Add(self.threads, (self.gridCount, 1))

        sizerBox.Add(sizerOpt)
        return sizerBox

    def p_inj_de_tech(self):
        panel = wx.Panel(self.nb, -1)
        sizer = wx.GridSizer(2, 2)

        sizer.Add(self.box_injection(panel), 0, wx.EXPAND)
        sizer.Add(self.box_detection(panel), 0, wx.EXPAND | wx.LEFT, 4)
        sizer.Add(self.box_tampers(panel), 0, wx.EXPAND)

        sizer.Add(self.box_techniques(panel), 0, wx.EXPAND | wx.LEFT, 4)
        panel.SetSizer(sizer)
        return panel

    def box_injection(self, panel):
        box = wx.StaticBox(panel, -1, 'Injection')

        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizerInjection = wx.GridBagSizer()

        self.gridCount = 0

        self.testParameter = wx.TextCtrl(panel, -1, size=SIZE)
        self.testParameter.SetToolTip(wx.ToolTip('Testable parameter(s)'))
        self.set_label(sizerInjection, panel, 'p', self.testParameter)

        self.skip = wx.TextCtrl(panel, -1, size=SIZE)
        self.skip.SetToolTip(wx.ToolTip('Skip testing for given parameter(s)'))
        self.set_label(sizerInjection, panel,  'skip', self.skip)

        self.dbms = wx.ComboBox(panel, -1, '', (0, 0), wx.DefaultSize,
                                ['MySQL', 'Oracle', 'PostgreSQL', 'Microsoft SQL Server',
                                 'Microsoft Access', 'SQLite', 'Firebird', 'Sybase',
                                 'SAP MaxDB', 'DB2', ''])
        self.dbms.SetToolTip(wx.ToolTip('Force back-end DBMS to this value'))
        self.set_label(sizerInjection, panel,  'dbms', self.dbms)

        self.dbmsCred = wx.TextCtrl(panel, -1, size=SIZE)
        self.dbmsCred.SetToolTip(wx.ToolTip('DBMS authentication credentials (user:password)'))
        self.set_label(sizerInjection, panel,  'dbms-cred', self.dbmsCred)

        self.os = wx.TextCtrl(panel, -1, size=SIZE)
        self.os.SetToolTip(wx.ToolTip('Force back-end DBMS operating system to this value'))
        self.set_label(sizerInjection, panel,  'os', self.os)

        self.prefix = wx.TextCtrl(panel, -1, size=SIZE)
        self.prefix.SetToolTip(wx.ToolTip('Injection payload prefix string'))
        self.set_label(sizerInjection, panel,  'prefix', self.prefix)

        self.suffix = wx.TextCtrl(panel, -1, size=SIZE)
        self.suffix.SetToolTip(wx.ToolTip('Injection payload suffix string'))
        self.set_label(sizerInjection, panel,  'suffix', self.suffix)

        self.invalidBignum = wx.CheckBox(panel, -1, 'invalid-bignum')
        self.invalidBignum.SetToolTip(wx.ToolTip('Use big numbers for invalidating values'))
        sizerInjection.Add(self.invalidBignum, (self.gridCount, 1))

        self.invalidLogical = wx.CheckBox(panel, -1, 'invalid-logical')
        self.invalidLogical.SetToolTip(wx.ToolTip('Use big numbers for invalidating values'))
        sizerInjection.Add(self.invalidLogical, (self.gridCount, 2))
        self.gridCount += 1

        self.noCast = wx.CheckBox(panel, -1, 'no-cast')
        self.noCast.SetToolTip(wx.ToolTip('Turn off payload casting mechanism'))
        sizerInjection.Add(self.noCast, (self.gridCount, 1))

        self.noEscape = wx.CheckBox(panel, -1, 'no-escape')
        self.noEscape.SetToolTip(wx.ToolTip('Turn off string escaping mechanism'))
        sizerInjection.Add(self.noEscape, (self.gridCount, 2))

        sizerBox.Add(sizerInjection, 1, wx.EXPAND)

        return sizerBox

    def box_tampers(self, panel):
        box = wx.StaticBox(panel, -1, 'Tampers')
        sizer = wx.StaticBoxSizer(box)

        tampers = os.listdir(sqlmap.modulePath()+'/tamper')
        tampers.insert(0, '')

        try:
            tampers.remove('__init__.py')
        except ValueError:
            pass

        self.tamper = wx.ListBox(panel, -1, (0, 0), (0, 0), tampers, wx.LB_EXTENDED)

        sizer.Add(self.tamper, 1, wx.EXPAND)
        return sizer

    def box_detection(self, panel):
        box = wx.StaticBox(panel, -1, 'Detection')
        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizerDetection = wx.GridBagSizer()

        self.gridCount = 0

        self.level = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.level.SetRange(1, 5)
        self.level.SetToolTip(wx.ToolTip('Level of tests to perform (1-5, default 1)'))
        self.set_label(sizerDetection, panel,  'level', self.level)

        self.risk = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.risk.SetRange(0, 3)
        self.risk.SetValue(1)
        self.risk.SetToolTip(wx.ToolTip('Risk of tests to perform (0-3, default 1)'))
        self.set_label(sizerDetection, panel,  'risk', self.risk)

        self.string = wx.TextCtrl(panel, -1, size=SIZE)
        self.string.SetToolTip(wx.ToolTip('String to match when query is evaluated to True'))
        self.set_label(sizerDetection, panel,  'string', self.string)

        self.notString = wx.TextCtrl(panel, -1, size=SIZE)
        self.notString.SetToolTip(wx.ToolTip('String to match when query is evaluated to False'))
        self.set_label(sizerDetection, panel,  'not-string', self.notString)

        self.regexp = wx.TextCtrl(panel, -1, size=SIZE)
        self.regexp.SetToolTip(wx.ToolTip('Regexp to match when query is evaluated to True'))
        self.set_label(sizerDetection, panel,  'regexp', self.regexp)

        self.code = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.code.SetRange(0, 1000)
        self.code.SetToolTip(wx.ToolTip('HTTP code to match when query is evaluated to True'))
        self.set_label(sizerDetection, panel,  'code', self.code)

        self.textOnly = wx.CheckBox(panel, -1, 'text-only')
        self.textOnly.SetToolTip(wx.ToolTip('Compare pages based only on the textual content'))
        sizerDetection.Add(self.textOnly, (self.gridCount, 1))

        self.titles = wx.CheckBox(panel, -1, 'titles')
        self.titles.SetToolTip(wx.ToolTip('Compare pages based only on their titles'))
        sizerDetection.Add(self.titles, (self.gridCount, 2))
        self.gridCount += 1

        self.beep = wx.CheckBox(panel, -1, 'beep')
        self.beep.SetToolTip(wx.ToolTip('Make a beep sound when SQL injection is found'))
        sizerDetection.Add(self.beep, (self.gridCount, 1))

        sizerBox.Add(sizerDetection, 1, wx.EXPAND)
        return sizerBox

    def box_techniques(self, panel):
        box = wx.StaticBox(panel, -1, 'Techniques')

        sizerBox = wx.StaticBoxSizer(box)
        sizerTechniques = wx.GridBagSizer()

        self.gridCount = 0

        techs = 'BEUSTQ'
        techlist = 'B E U S T Q'.split(' ')
        techlist.extend([techs])

        self.tech = wx.ComboBox(panel, -1, techs, (0, 0), wx.DefaultSize,
                                techlist)
        self.tech.SetToolTip(wx.ToolTip('SQL injection techniques to use (default "BEUSTQ\n'
                                        'B: Boolean-based blind\n'
                                        'E: Error-basedU: Union query-based\n'
                                        'S: Stacked queries\n'
                                        'T: Time-based blind\n'
                                        'Q: Inline queries")'))
        self.set_label(sizerTechniques, panel,  'technique', self.tech)

        self.timeSec = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.timeSec.SetValue(5)
        self.timeSec.SetRange(0, 1000)
        self.timeSec.SetToolTip(wx.ToolTip('Seconds to delay the DBMS response (default 5)'))
        self.set_label(sizerTechniques, panel,  'time-sec', self.timeSec)

        self.uCols = wx.TextCtrl(panel, -1, size=SIZE)
        self.uCols.SetToolTip(wx.ToolTip('Range of columns to test for UNION query SQL injection'))
        self.set_label(sizerTechniques, panel,  'union-cols', self.uCols)

        self.uChar = wx.TextCtrl(panel, -1, size=SIZE)
        self.uChar.SetToolTip(wx.ToolTip('Character to use for bruteforcing number of columns'))
        self.set_label(sizerTechniques, panel,  'union-char', self.uChar)

        self.uFrom = wx.TextCtrl(panel, -1, size=SIZE)
        self.uFrom.SetToolTip(wx.ToolTip('Table to use in FROM part of UNION query SQL injection'))
        self.set_label(sizerTechniques, panel,  'union-from', self.uFrom)

        self.dnsName = wx.TextCtrl(panel, -1, size=SIZE)
        self.dnsName.SetToolTip(wx.ToolTip('Domain name used for DNS exfiltration attack'))
        self.set_label(sizerTechniques, panel,  'dns-domain', self.dnsName)

        self.secondOrder = wx.TextCtrl(panel, -1, size=SIZE)
        self.secondOrder.SetToolTip(wx.ToolTip('Resulting page URL searched for second-order response'))
        self.set_label(sizerTechniques, panel,  'second-order', self.secondOrder)


        sizerBox.Add(sizerTechniques, 1, wx.EXPAND)
        return sizerBox

    def box_fingerprint(self, panel):
        box = wx.StaticBox(panel, -1, 'Fingerprint')
        sizerBox = wx.StaticBoxSizer(box)

        self.extensiveFp = wx.CheckBox(panel, -1, 'fingerprint')
        self.extensiveFp.SetToolTip(wx.ToolTip('Perform an extensive DBMS version fingerprint'))

        sizerBox.Add(self.extensiveFp)

        return sizerBox

    def p_enumeration(self):
        panel = wx.Panel(self.nb, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizerRight = wx.BoxSizer(wx.VERTICAL)
        sizerRight.Add(self.box_brute_force(panel), 0, wx.EXPAND | wx.LEFT, 4)
        sizerRight.Add(self.box_fingerprint(panel), 0, wx.EXPAND | wx.LEFT, 4)

        sizer.Add(self.box_enum(panel), 0, wx.EXPAND)
        sizer.Add(sizerRight, 0, wx.EXPAND)

        panel.SetSizer(sizer)
        return panel

    def box_enum(self, panel):
        box = wx.StaticBox(panel, -1, 'Enumeration')
        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizerEnum = wx.GridBagSizer()
        self.gridCount = 0

        self.query = wx.TextCtrl(panel, -1, size=SIZE)
        self.query.SetToolTip(wx.ToolTip('SQL statement to be executed'))
        self.set_label(sizerEnum, panel,  'sql-query', self.query)

        self.limitStart = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.limitStart.SetRange(0, 100000)
        self.limitStart.SetToolTip(wx.ToolTip('First query output entry to retrieve'))
        self.set_label(sizerEnum, panel,  'start', self.limitStart)

        self.limitStop = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.limitStop.SetRange(0, 100000)
        self.limitStop.SetToolTip(wx.ToolTip('Last query output entry to retrieve'))
        self.set_label(sizerEnum, panel,  'stop', self.limitStop)

        self.firstChar = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.firstChar.SetRange(0, 100000)
        self.firstChar.SetToolTip(wx.ToolTip('First query output word character to retrieve'))
        self.set_label(sizerEnum, panel,  'first', self.firstChar)

        self.lastChar = wx.SpinCtrl(panel, -1, '', (0, 0), size=SIZE)
        self.lastChar.SetRange(0, 100000)
        self.lastChar.SetToolTip(wx.ToolTip('Last query output word character to retrieve'))
        self.set_label(sizerEnum, panel,  'last', self.lastChar)

        self.sqlFile = fbrows.FileBrowseButton(panel, -1)
        self.sqlFile.SetLabel('sql-file')
        self.sqlFile.SetToolTip(wx.ToolTip('Execute SQL statements from given file'))

        self.getCurrentUser = wx.CheckBox(panel, -1, 'current-user')
        self.getCurrentUser.SetToolTip(wx.ToolTip('Retrieve DBMS current user'))
        sizerEnum.Add(self.getCurrentUser, (self.gridCount, 2))
        self.gridCount += 1

        self.getCurrentDb = wx.CheckBox(panel, -1, 'current-db')
        self.getCurrentDb.SetToolTip(wx.ToolTip('Retrieve DBMS current database'))
        sizerEnum.Add(self.getCurrentDb, (self.gridCount, 2))
        self.gridCount += 1

        self.getHostname = wx.CheckBox(panel, -1, 'hostname')
        self.getHostname.SetToolTip(wx.ToolTip('Retrieve DBMS server hostname'))
        sizerEnum.Add(self.getHostname, (self.gridCount, 2))
        self.gridCount += 1

        self.isDba = wx.CheckBox(panel, -1, 'is-dba')
        self.isDba.SetToolTip(wx.ToolTip('Detect if the DBMS current user is DBA'))
        sizerEnum.Add(self.isDba, (self.gridCount, 2))
        self.gridCount += 1

        self.getUsers = wx.CheckBox(panel, -1, 'users')
        self.getUsers.SetToolTip(wx.ToolTip('Enumerate DBMS users'))
        sizerEnum.Add(self.getUsers, (self.gridCount, 2))
        self.gridCount += 1

        self.getPasswordHashes = wx.CheckBox(panel, -1, 'passwords')
        self.getPasswordHashes.SetToolTip(wx.ToolTip('Enumerate DBMS users password hashes'))
        sizerEnum.Add(self.getPasswordHashes, (self.gridCount, 2))
        self.gridCount += 1

        self.getPrivileges = wx.CheckBox(panel, -1, 'privileges')
        self.getPrivileges.SetToolTip(wx.ToolTip('Enumerate DBMS users privileges'))
        sizerEnum.Add(self.getPrivileges, (self.gridCount, 2))
        self.gridCount += 1

        self.getRoles = wx.CheckBox(panel, -1, 'roles')
        self.getRoles.SetToolTip(wx.ToolTip('Enumerate DBMS users roles'))
        sizerEnum.Add(self.getRoles, (self.gridCount, 2))
        self.gridCount += 1

        sizerBox.Add(self.sqlFile, 0, wx.EXPAND)
        sizerBox.Add(sizerEnum, 0, wx.EXPAND)
        return sizerBox

    def box_brute_force(self, panel):
        box = wx.StaticBox(panel, -1, 'Brute force')
        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizerBrute = wx.GridBagSizer()
        self.gridCount = 0

        self.commonTables = wx.CheckBox(panel, -1, 'common-tables')
        self.commonTables.SetToolTip(wx.ToolTip('Check existence of common columns'))
        sizerBrute.Add(self.commonTables, (self.gridCount, 1))

        self.gridCount += 1
        self.commonColumns = wx.CheckBox(panel, -1, 'common-columns')
        self.commonColumns.SetToolTip(wx.ToolTip('Check existence of common columns'))
        sizerBrute.Add(self.commonColumns, (self.gridCount, 1))

        sizerBox.Add(sizerBrute, 0, wx.EXPAND)
        return sizerBox

    def p_access(self):
        panel = wx.Panel(self.nb, -1)
        sizer = wx.GridSizer(2, 2)

        sizer.Add(self.box_file_sys_access(panel), 1, wx.EXPAND)
        sizer.Add(self.box_os_access(panel), 0, wx.EXPAND | wx.LEFT, 4)
        sizer.Add(self.box_win_reg_access(panel), 0, wx.EXPAND)

        panel.SetSizer(sizer)
        return panel

    def box_file_sys_access(self, panel):
        box = wx.StaticBox(panel, -1, 'File system access')
        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizerFile = wx.GridBagSizer()

        self.gridCount = 0

        self.rFile = wx.TextCtrl(panel, -1, size=SIZE)
        self.rFile.SetToolTip(wx.ToolTip('Read a file from the back-end DBMS file system'))
        self.set_label(sizerFile, panel, 'file-read', self.rFile)

        self.wFile = fbrows.FileBrowseButton(panel, -1)
        self.wFile.SetLabel('file-write')
        self.wFile.SetToolTip(wx.ToolTip('Write a local file on the back-end DBMS file system'))

        self.dFile = wx.TextCtrl(panel, -1, size=SIZE)
        self.dFile.SetToolTip(wx.ToolTip('Back-end DBMS absolute filepath to write to'))
        self.set_label(sizerFile, panel,  'file-dest', self.dFile)


        sizerBox.Add(self.wFile, 0, wx.EXPAND)
        sizerBox.Add(sizerFile, 0, wx.EXPAND)
        return sizerBox

    def box_os_access(self, panel):
        box = wx.StaticBox(panel, -1, 'Operating system access')
        sizerBox = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizerOs = wx.GridBagSizer()
        self.gridCount = 0

        self.tmpPath = wx.TextCtrl(panel, -1, size=SIZE)
        self.tmpPath.SetToolTip(wx.ToolTip('Remote absolute path of temporary files directory'))
        self.set_label(sizerOs, panel,  'tmp-path', self.tmpPath)

        self.osCmd = wx.TextCtrl(panel, -1, size=SIZE)
        self.osCmd.SetToolTip(wx.ToolTip('Execute an operating system command'))
        self.set_label(sizerOs, panel,  'os-cmd', self.osCmd)

        self.msfPath = fbrows.DirBrowseButton(panel, -1)
        self.msfPath.SetLabel('msf-path')
        self.msfPath.SetToolTip(wx.ToolTip('Local path where Metasploit Framework is installed'))

        self.osShell = wx.CheckBox(panel, -1, 'os-shell')
        self.osShell.SetToolTip(wx.ToolTip('Prompt for an interactive operating system shell'))
        sizerOs.Add(self.osShell, (self.gridCount, 2))
        self.gridCount += 1

        self.osPwn = wx.CheckBox(panel, -1, 'os-pwn')
        self.osPwn.SetToolTip(wx.ToolTip('Prompt for an out-of-band shell, meterpreter or VNC'))
        sizerOs.Add(self.osPwn, (self.gridCount, 2))
        self.gridCount += 1

        self.osSmb = wx.CheckBox(panel, -1, 'os-smbrelay')
        self.osSmb.SetToolTip(wx.ToolTip('One click prompt for an OOB shell, meterpreter or VNC'))
        sizerOs.Add(self.osSmb, (self.gridCount, 2))
        self.gridCount += 1

        self.osBof = wx.CheckBox(panel, -1, 'os-bof')
        self.osBof.SetToolTip(wx.ToolTip('Stored procedure buffer overflow exploitation'))
        sizerOs.Add(self.osBof, (self.gridCount, 2))
        self.gridCount += 1
        
        self.privEsc = wx.CheckBox(panel, -1, 'priv-esc')
        self.privEsc.SetToolTip(wx.ToolTip('Database process\' user privilege escalation'))
        sizerOs.Add(self.privEsc, (self.gridCount, 2))

        sizerBox.Add(self.msfPath, 0, wx.EXPAND)
        sizerBox.Add(sizerOs, 1, wx.EXPAND)
        return sizerBox

    def box_win_reg_access(self, panel):
        box = wx.StaticBox(panel, -1, 'Windows registry access')
        sizerBox = wx.StaticBoxSizer(box)
        sizerWin = wx.GridBagSizer()
        self.gridCount = 0

        self.regKey = wx.TextCtrl(panel, -1, size=SIZE)
        self.regKey.SetToolTip(wx.ToolTip('Windows registry key'))
        self.set_label(sizerWin, panel,  'reg-key', self.regKey)

        self.regVal = wx.TextCtrl(panel, -1, size=SIZE)
        self.regVal.SetToolTip(wx.ToolTip('Windows registry key value'))
        self.set_label(sizerWin, panel,  'reg-val', self.regVal)

        self.regData = wx.TextCtrl(panel, -1, size=SIZE)
        self.regData.SetToolTip(wx.ToolTip('Windows registry key value data'))
        self.set_label(sizerWin, panel,  'reg-data', self.regData)

        self.regType = wx.TextCtrl(panel, -1, size=SIZE)
        self.regType.SetToolTip(wx.ToolTip('Windows registry key value type'))
        self.set_label(sizerWin, panel,  'reg-type', self.regType)

        self.regRead = wx.CheckBox(panel, -1, 'reg-read')
        self.regRead.SetToolTip(wx.ToolTip('Read a Windows registry key value'))
        sizerWin.Add(self.regRead, (self.gridCount, 2))
        self.gridCount += 1

        self.regAdd = wx.CheckBox(panel, -1, 'reg-add')
        self.regAdd.SetToolTip(wx.ToolTip('Write a Windows registry key value data'))
        sizerWin.Add(self.regAdd, (self.gridCount, 2))
        self.gridCount += 1

        self.regDel = wx.CheckBox(panel, -1, 'reg-del')
        self.regDel.SetToolTip(wx.ToolTip('Delete a Windows registry key value'))
        sizerWin.Add(self.regDel, (self.gridCount, 2))

        sizerBox.Add(sizerWin, 1, wx.EXPAND)
        return sizerBox

    def p_general(self):
        panel = wx.Panel(self.nb, -1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizerGrid = wx.GridBagSizer()
        self.gridCount = 0

        # sizerCrawl = wx.BoxSizer(wx.HORIZONTAL)

        self.crawlDepth = wx.SpinCtrl(panel, -1, '', (0, 0), size=(180, 24))
        self.crawlDepth.SetRange(0, 65535)
        self.crawlDepth.SetToolTip(wx.ToolTip('Crawl the website starting from the target URL'))

        self.set_label(sizerGrid, panel, 'crawlDepth', self.crawlDepth)

        self.verbose = wx.SpinCtrl(panel, -1, '', (0, 0), size=(180, 24))
        self.verbose.SetRange(0, 6)
        self.verbose.SetValue(1)
        self.verbose.SetToolTip(wx.ToolTip('0: Show only Python tracebacks, error and critical messages.\n'
                                           '1: Show also information and warning messages.\n'
                                           '2: Show also debug messages.\n'
                                           '3: Show also payloads injected.\n'
                                           '4: Show also HTTP requests.\n'
                                           '5: Show also HTTP responses headers.\n'
                                           '6: Show also HTTP responses page content.\n'))

        self.set_label(sizerGrid, panel, 'verbose', self.verbose)

        sizer.Add(sizerGrid)
        panel.SetSizer(sizer)
        return panel