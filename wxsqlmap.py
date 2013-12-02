#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx
import wx.aui as aui
import wx.lib.agw.customtreectrl as ct
import wx.lib.agw.buttonpanel as bp
from wxsqlm.lib.interface import SqlmapInterface
from wxsqlm.lib.interface import SqlmapServer
from wxsqlm.lib.options import Options
from wxsqlm.lib.scan import ScanThread
from wxsqlm.lib.grid import GridTable
from wxsqlm.lib.output import HtmlGenerator
from wxsqlm.lib.output import ScanOutput
from wxsqlm.lib.about import Info
from wxsqlm.lib.config import get_conf
from wxsqlm.lib.images import LOGO_ICON
from wxsqlm.lib.images import TREE_ICONS
from wxsqlm.lib.images import BUTTON_ICONS

import os
from urlparse import urlparse

CONF = get_conf()

SAVE_TYPES = 'HTML file (*.html)|*.html|'

ID_MENU_SAVE = wx.NewId()
ID_MENU_EXIT = wx.NewId()
ID_MENU_NEW_SCAN = wx.NewId()
ID_MENU_OPTIONS = wx.NewId()
ID_MENU_ABOUT = wx.NewId()


class Frame(wx.Frame):

    def __init__(self, parent, id, title, pos=wx.DefaultPosition):
        wx.Frame.__init__(self, parent, id, title, pos)

        self.info = Info(self)
        self.SetTitle(self.info.GetName())
        self.SetIcon(wx.Icon(LOGO_ICON, wx.BITMAP_TYPE_PNG))

        self.apiUrl = 'http://'+CONF['server']['host']+':'+str(CONF['server']['port'])

        self.interface = SqlmapInterface(self.apiUrl, CONF['server']['headers'])
        self.addOptions = None

        self.taskID = None

        self.saved = True
        self.scanThread = None
        self.options = dict()

        self.auiMgr = aui.AuiManager()
        self.auiMgr.SetManagedWindow(self)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        #====================#
        # menus and menu bar #
        #====================#

        self.menuFile = wx.Menu()
        self.menuFile.Append(ID_MENU_SAVE, '&Save\tCtrl-S', 'Save scan results')
        self.menuFile.AppendSeparator()
        self.menuFile.Append(ID_MENU_EXIT, 'E&xit', 'Exit the Application')
        self.menuFile.Enable(ID_MENU_SAVE, False)

        self.menuScan = wx.Menu()
        self.menuScan.Append(ID_MENU_NEW_SCAN, '&New Scan\tCtrl-N', 'Start a new scan.')
        self.menuScan.AppendSeparator()
        self.menuScan.Append(ID_MENU_OPTIONS, '&Options\tCtrl-O', 'Set scan options')
        self.menuScan.Enable(ID_MENU_OPTIONS, False)

        menuHelp = wx.Menu()
        menuHelp.Append(ID_MENU_ABOUT, '&About...')

        self.Bind(wx.EVT_MENU, self.OnSave, id=ID_MENU_SAVE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_MENU_EXIT)
        self.Bind(wx.EVT_MENU, self.OnNewScan, id=ID_MENU_NEW_SCAN)
        self.Bind(wx.EVT_MENU, self.OnOptions, id=ID_MENU_OPTIONS)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_MENU_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(self.menuFile, "&File")
        menuBar.Append(self.menuScan, "&Scan")
        menuBar.Append(menuHelp, "&Help")
        self.SetMenuBar(menuBar)

        #============================#
        # panel top : target, inputs #
        #============================#

        sizerPnlTop = wx.BoxSizer(wx.VERTICAL)
        pnlTop = wx.Panel(self, -1)

        self.sizerPnlTarget = wx.BoxSizer(wx.HORIZONTAL)
        pnlTarget = wx.Panel(pnlTop, -1)

        self.lTarget = wx.StaticText(pnlTarget, -1, label='target-url: ')
        self.tcTarget = wx.TextCtrl(pnlTarget, -1)
        self.tcTarget.Enable(False)
        self.tcTarget.Bind(wx.EVT_TEXT, self.set_tree_target)

        self.sizerPnlTarget.Add(self.lTarget, flag=wx.ALIGN_CENTRE_VERTICAL)
        self.sizerPnlTarget.Add(self.tcTarget, 1, wx.EXPAND)
        pnlTarget.SetSizerAndFit(self.sizerPnlTarget)

        # self.tcTarget.SetValue('http://www.beispiel.com/?id=1')

        #========================================================#
        # panel top: button panel: create buttons bind functions #
        #========================================================#

        sizerPnlButtons = wx.BoxSizer(wx.HORIZONTAL)
        pnlButtons = wx.Panel(pnlTop, -1)

        self.btnPanel = bp.ButtonPanel(pnlButtons, -1,
                                       agwStyle=bp.BP_DEFAULT_STYLE)
        self.btnPanel.GetBPArt().SetMetric(bp.BP_PADDING_SIZE, wx.Size(4, 4))
        self.btnPanel.GetBPArt().SetMetric(bp.BP_MARGINS_SIZE, wx.Size(4, 4))
        self.btnPanel.GetBPArt().GetFont(bp.BP_BUTTONTEXT_FONT)\
                                .SetPointSize(8)

        self.btnStop = bp.ButtonInfo(self.btnPanel, -1,
                                     self.get_icon('stop'),
                                     text='Stop',
                                     shortHelp='Stop the current scan')
        self.btnStop.Enable(False)

        self.btnStart = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('target'),
                                      text='Start',
                                      shortHelp='Start the customized scan')

        self.btnSetOptions = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('options'), text='Options',
                                           shortHelp='Set scan options')

        self.btnGetDBs = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('db'), text='Get DBs',
                                       shortHelp='Enumerate DBMS databases')

        self.btnGetTbls = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('tbl'), text='Get Tables',
                                        shortHelp='Enumerate DBMS database tables')

        self.btnGetCols = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('col'), text='Get Columns',
                                        shortHelp='Enumerate DBMS database table columns')

        self.btnGetData = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('tblDump'), text='Get Data',
                                        shortHelp='Dump DBMS database table entries')

        self.btnOutput = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('view'), text='View Output',
                                       shortHelp='View data output')

        self.btnSave = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('save'), text=' Save ',
                                     shortHelp='save scan results')
        self.btnCloseAll = bp.ButtonInfo(self.btnPanel, -1, self.get_icon('closeTab'), text='Close Tabs',
                                         shortHelp='Close all tabs')
        self.btnCloseAll.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.stop_scan, self.btnStop)
        self.Bind(wx.EVT_BUTTON, self.run_custom, self.btnStart)
        self.Bind(wx.EVT_BUTTON, self.OnOptions, self.btnSetOptions)
        self.Bind(wx.EVT_BUTTON, self.run_get_dbs, self.btnGetDBs)
        self.Bind(wx.EVT_BUTTON, self.run_get_tables, self.btnGetTbls)
        self.Bind(wx.EVT_BUTTON, self.run_get_columns, self.btnGetCols)
        self.Bind(wx.EVT_BUTTON, self.run_get_data, self.btnGetData)
        self.Bind(wx.EVT_BUTTON, self.OnShowOutput, self.btnOutput)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.btnSave)
        self.Bind(wx.EVT_BUTTON, self.OnDeletePages, self.btnCloseAll)

        self.btnPanel.AddButton(self.btnStop)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnStart)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnSetOptions)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnGetDBs)
        self.btnPanel.AddButton(self.btnGetTbls)
        self.btnPanel.AddButton(self.btnGetCols)
        self.btnPanel.AddButton(self.btnGetData)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnOutput)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnSave)
        self.btnPanel.AddSeparator()
        self.btnPanel.AddButton(self.btnCloseAll)
        self.btnPanel.DoLayout()

        self.scanBtns = [self.btnStart,
                         self.btnGetDBs,
                         self.btnGetTbls,
                         self.btnGetCols,
                         self.btnGetData,
                         self.btnOutput,
                         self.btnSave,
                         self.btnSetOptions]

        sizerPnlButtons.Add(self.btnPanel, 1, wx.EXPAND)
        pnlButtons.SetSizerAndFit(sizerPnlButtons)

        self.enable_scan_inputs(False)

        sizerPnlTop.Add(pnlTarget, 0, wx.EXPAND | wx.LEFT | wx.TOP, 2)
        sizerPnlTop.Add(pnlButtons, 0, wx.EXPAND)
        pnlTop.SetSizerAndFit(sizerPnlTop)

        #==============================================#
        # panel center: aui notebook, grid data output #
        #==============================================#

        sizerPnlCenter = wx.BoxSizer(wx.VERTICAL)
        self.pnlCenter = wx.Panel(self, -1)

        self.nb = aui.AuiNotebook(self.pnlCenter, -1,
                                  style=aui.AUI_NB_CLOSE_ON_ALL_TABS |
                                        aui.AUI_NB_WINDOWLIST_BUTTON |
                                        aui.AUI_NB_TAB_SPLIT |
                                        aui.AUI_NB_TAB_MOVE |
                                        aui.AUI_NB_TAB_EXTERNAL_MOVE |
                                        aui.AUI_NB_SCROLL_BUTTONS)

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSED,
                  self.OnPageClosed, self.nb)

        sizerPnlCenter.Add(self.nb, 1, wx.EXPAND)
        self.pnlCenter.SetSizerAndFit(sizerPnlCenter)

        #==========================#
        # panel left: tree control #
        #==========================#

        self.sizerPnlTree = wx.BoxSizer(wx.HORIZONTAL)
        pnlTree = wx.Panel(self, -1)

        self.tree = ct.CustomTreeCtrl(pnlTree, -1,
                                      agwStyle=ct.TR_HAS_BUTTONS |
                                               ct.TR_AUTO_CHECK_PARENT |
                                               ct.TR_AUTO_CHECK_CHILD |
                                               ct.TR_HAS_VARIABLE_ROW_HEIGHT)
        self.Bind(ct.EVT_TREE_ITEM_CHECKED, self.OnCheckTree, self.tree)
        self.sizerPnlTree.Add(self.tree, 1, wx.EXPAND)

        # creating image list and assigning list to tree
        # (target, db, table and column icon)
        il = wx.ImageList(16, 16)

        for k in TREE_ICONS.keys():
            TREE_ICONS[k] = il.Add(TREE_ICONS[k].Scale(16, 16).
                                    ConvertToBitmap())

        self.tree.AssignImageList(il)

        self.treeRoot = self.tree.AddRoot('', image=TREE_ICONS['target'])
        self.treeDBs = None
        self.treeTbls = None
        self.treeData = dict()
        self.set_tree_target(None)
        self.tree.Layout()
        pnlTree.SetSizerAndFit(self.sizerPnlTree)

        #========================#
        # pane bottom: scan logs #
        #========================#

        self.tcLog = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE |
                                                 wx.TE_READONLY)

        #=================================================#
        # adding panels and components to the aui manager #
        #=================================================#

        self.auiMgr.AddPane(pnlTop, aui.AuiPaneInfo().
                            Name('inputs').
                            Top().DockFixed().
                            CaptionVisible(False).
                            PaneBorder(False).
                            CloseButton(False))

        self.auiMgr.AddPane(pnlTree, aui.AuiPaneInfo().
                            Name('tree').Caption('Target Schema').
                            Left().BestSize(wx.Size(160, 500)).
                            PaneBorder(False).
                            MaximizeButton(True).CloseButton(False))

        self.auiMgr.AddPane(self.pnlCenter, aui.AuiPaneInfo().
                            Name('center').Caption('Table Dumps').
                            Center().
                            PaneBorder(False).
                            MaximizeButton(True).CloseButton(False))

        self.auiMgr.AddPane(self.tcLog, aui.AuiPaneInfo().
                            Name('log').Caption('Scan Log').
                            Bottom().BestSize(wx.Size(600, 140)).
                            PaneBorder(False).
                            MaximizeButton(True).CloseButton(False))

        self.CreateStatusBar()
        self.SetStatusText(self.info.GetName())

    def OnServer(self, msg, title):
        dlg = wx.MessageDialog(self,
                               msg,
                               title,
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()

    def OnSave(self, event=None):
        dlg = wx.FileDialog(self,
                            message="Save scan results...",
                            defaultDir=os.getcwd(),
                            defaultFile=self.treeRoot.GetText(),
                            wildcard=SAVE_TYPES,
                            style=wx.SAVE | wx.OVERWRITE_PROMPT)
        resp = dlg.ShowModal()

        if resp == wx.ID_OK:
            wcard = dlg.GetWildcard().split('|')[-2].split('*')[-1]

            f = dlg.GetPath()
            if not f.endswith(wcard) and not f.endswith(wcard.upper()):
                f += wcard

            data = self.interface.scan_data()
            log = self.interface.scan_log()['log']
            html = HtmlGenerator(self.treeRoot.GetText(),
                                 data, log, self.treeData,
                                 self.get_grids())

            with open(f, 'w') as out:
                out.write(html.get_html_output())
            self.saved = True
            self.enable_saving(False)

        dlg.Destroy()
        return resp

    def enable_saving(self, state):
        self.menuFile.Enable(ID_MENU_SAVE, state)
        self.btnSave.Enable(state)
        self.btnPanel.Refresh()

    def OnOptions(self, event):
        self.addOptions.Show()

    def OnShowOutput(self, event):
        output = ScanOutput(self, -1, self.taskID, self.apiUrl)
        output.ShowModal()

    def exit(self):
        self.auiMgr.UnInit()
        self.Destroy()

    def OnExit(self, event):
        self.Close()

    def OnCloseWindow(self, event):
        if self.saved:
            self.exit()
        else:
            save = self.save_scan()

            if save == wx.ID_YES:
                if self.OnSave() == wx.ID_OK:
                    self.exit()
            elif save == wx.ID_NO:
                self.exit()

    def OnNewScan(self, event):
        if self.taskID is None or self.saved:
            self.init_new_scan()
        else:
            save = self.save_scan()

            if save == wx.ID_YES:
                if self.OnSave() == wx.ID_OK:
                    self.init_new_scan()
            elif save == wx.ID_NO:
                self.init_new_scan()

    def save_scan(self):
        return wx.MessageDialog(self, 'Save scan results?',
                                "",
                                wx.CANCEL | wx.NO | wx.YES | wx.ICON_WARNING).ShowModal()

    def init_new_scan(self):
        self.taskID = self.interface.task_new()
        self.enable_scan_inputs(True)
        self.treeData = dict()
        self.tree.DeleteAllItems()
        self.tcLog.SetValue('')
        self.empty_nb()
        self.empty_tree()
        self.tcTarget.Enable(True)
        self.tcTarget.SetValue('')
        self.saved = True
        self.enable_saving(False)
        self.addOptions = Options(-1, CONF['option'])
        self.SetStatusText(self.info.GetName())

    def OnAbout(self, event):
        wx.AboutBox(self.info)

    #
    def OnCheckTree(self, event):
        item = event.GetItem()

        if item.IsChecked():
            parent = self.tree.GetItemParent(item)

            if not parent.IsChecked():
                parent.Check()
                try:
                    grandParent = parent.GetParent()
                    if not grandParent.IsChecked():
                        grandParent.Check()

                except AttributeError:
                    pass
        self.tree.Refresh()

    def OnPageClosed(self, event):
        if self.nb.GetPageCount() == 0:
            self.btnCloseAll.Enable(False)
            self.btnPanel.Refresh()

    def OnDeletePages(self, event):
        dialog = wx.MessageDialog(self,
                                  "Close all tabs?",
                                  "Confirm Closing",
                                  wx.OK | wx.CANCEL | wx.ICON_WARNING)

        response = dialog.ShowModal()
        dialog.Destroy()

        if response == wx.ID_OK:
            self.empty_nb()

    def empty_nb(self):
        for i in range(self.nb.GetPageCount()):
                self.nb.DeletePage(0)
        self.btnCloseAll.Enable(False)
        self.btnPanel.Refresh()

    def get_selected_items(self, items):
        selected = ''

        for item in items:
            if type(item) is list:
                for subitem in item:
                    if subitem.IsChecked():
                        selected += subitem.GetText()+','
            else:
                if item.IsChecked():
                    selected += item.GetText()+','

        return selected[:-1]

    def get_option_url(self):
        return dict(url=self.tcTarget.GetValue())

    def get_option_db(self):
        self.options = self.get_option_url()
        dbs = self.treeRoot.GetChildren()

        if len(dbs) > 0:
            self.options['db'] = self.get_selected_items(dbs)

    def get_option_tbl(self):
        self.get_option_db()
        tbls = [db.GetChildren() for db in self.treeRoot.GetChildren()]

        if len(tbls) > 0:
            self.options['tbl'] = self.get_selected_items(tbls)

    def get_option_dump(self):
        dumpDict = dict()
        for db in self.treeRoot.GetChildren():
            if db.IsChecked():
                dumpDict[db.GetText()] = dict()
                for tbl in db.GetChildren():
                    if tbl.IsChecked():
                        columns = str()
                        for col in tbl.GetChildren():
                            if col.IsChecked():
                                columns += col.GetText()+','
                        dumpDict[db.GetText()][tbl.GetText()] = columns[:-1]

        return dumpDict

    def run_custom(self, event):
        self.options = self.get_option_url()
        self.run_main()

    def run_get_dbs(self, event):
        self.options = self.get_option_url()
        self.options['getDbs'] = True
        self.run_main('schema')

    def run_get_tables(self, event):
        self.get_option_db()
        self.options['getTables'] = True
        self.run_main('schema')

    def run_get_columns(self, event):
        self.get_option_tbl()
        self.options['getColumns'] = True
        self.run_main('schema')

    def run_get_data(self, event):
        self.options = self.get_option_url()
        self.options['dumpTable'] = True
        self.scanThread = ScanThread(self, 'dump')
        self.scanThread.set_dump_dict(self.get_option_dump())
        self.scanThread.start()
        self.enable_run(False)

    def run_main(self, reqScan=None):
        if self.target_is_valid():
            if self.tcTarget.IsEnabled():
                self.tcTarget.Enable(False)

            self.options.update(self.addOptions.get_options())
            self.SetStatusText('started')

            self.scanThread = ScanThread(self, reqScan)
            self.scanThread.start()
            self.enable_run(False)
            # print self.taskID

        else:
            dlg = wx.MessageDialog(self,
                                   'The target url seems to be invalid.',
                                   'Error',
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

    def stop_scan(self, event):
        self.SetStatusText('stopping...')

        if self.scanThread and self.scanThread.isAlive():
            self.scanThread.stop()

        self.enable_run(True)
        self.SetStatusText('stopped')

    def get_interface(self):
        return self.interface

    def get_all_options(self):
        return self.options

    def enable_run(self, state):
        self.btnStop.Enable(not state)
        self.enable_scan_inputs(state)
        self.enable_saving(state)
        if state:
            self.saved = False

        self.btnPanel.Refresh()
        self.auiMgr.Update()

    def enable_scan_inputs(self, state):
        for btn in self.scanBtns:
            btn.Enable(state)

        self.menuScan.Enable(ID_MENU_OPTIONS, state)
        self.btnPanel.Refresh()

    def receive_data(self, data):
        d = data['data']

        if len(d) == 0:
            dlg = wx.MessageDialog(self,
                                   'All tested parameters appear to be not injectable',
                                   'Injection Not Found',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
        else:
            if d[-1]['status'] == 1 and d[-1]['type'] == 0:
                try:
                    val = d[-1]['value']
                    param = val[0]['parameter']
                    place = val[0]['place']
                    msg = place + " parameter '"+param+"' is injectable"
                    dlg = wx.MessageDialog(self,
                                           msg,
                                           'Injection Found',
                                           wx.OK | wx.ICON_WARNING)
                    dlg.ShowModal()

                except:
                    dlg = wx.MessageDialog(self,
                                           d[-1],
                                           'An error is occurred',
                                           wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()

    def get_tree_data(self):
        self.treeData

    def empty_tree(self):
        self.tree.DeleteAllItems()
        self.set_tree_target(None)
        self.treeRoot = self.tree.AddRoot('', image=TREE_ICONS['target'])
        self.set_tree_target(None)

    def update_tree(self, data):
        if not data['status'] == 1:
            return

        if data['type'] == 0:
            log = self.interface.scan_log()['log'][-1]
            icons = {'CRITICAL': wx.ICON_ERROR, 'ERROR': wx.ICON_ERROR, 'WARNING': wx.ICON_WARNING}

            icon = icons[log['level']] if log['level'] in icons else wx.ICON_INFORMATION

            dlg = wx.MessageDialog(self,
                                   log['message'],
                                   log['level'],
                                   wx.OK | icon)
            dlg.ShowModal()
            return

        values = data['value']

        try:
            for db in values.keys():
                if not db in self.treeData.keys():
                    self.treeData[db] = {}
                try:
                    for tbl in values[db].keys():
                        if not tbl in self.treeData[db].keys():
                            self.treeData[db][tbl] = {}
                        for col in values[db][tbl].keys():
                            self.treeData[db][tbl][col] = values[db][tbl][col]

                except AttributeError:
                    for tbl in values[db]:
                        try:
                            self.treeData[db][tbl] = {}
                        except KeyError:
                            self.treeData[db] = {}
                            self.treeData[db][tbl] = {}

        except AttributeError:
            if type(values) is list:
                for db in values:
                    self.treeData[db] = {}
            else:
                dlg = wx.MessageDialog(self,
                                       "Unknown data type returned by scan!\ntype: "+str(type(values))+"\ndata: "+values,
                                       "Error",
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

        self.empty_tree()
        self.add_data_to_tree()

    def add_data_to_tree(self):
        dt = self.treeData

        for db in dt.keys():
            self.add_item_to_tree(db, 'db')
            tbls = dt[db]

            if type(tbls) is dict:
                for tbl in tbls.keys():
                    self.add_item_to_tree(tbl, 'tbl')
                    if type(dt[db][tbl]) is dict:
                        for col in dt[db][tbl].keys():
                            self.add_item_to_tree(col, 'col')

    def add_item_to_tree(self, item, type):
        if type == 'db':
            self.treeDBs = self.tree.AppendItem(self.treeRoot, item,
                                                ct_type=1,
                                                image=TREE_ICONS[type])
            self.tree.SortChildren(self.tree.GetRootItem())
        elif type == 'tbl':
            self.treeTbls = self.tree.AppendItem(self.treeDBs, item,
                                                 ct_type=1,
                                                 image=TREE_ICONS[type])
            self.tree.SortChildren(self.treeDBs)
        elif type == 'col':
            self.tree.AppendItem(self.treeTbls, item,
                                 ct_type=1,
                                 image=TREE_ICONS[type])
            self.tree.SortChildren(self.treeTbls)
        self.tree.ExpandAll()

    def add_grid(self, data, tbl, cols):
        self.nb.InsertPage(0, GridTable(self.pnlCenter, -1, data, cols),
                           tbl, select=True)

        if not self.btnCloseAll.IsEnabled():
            self.btnCloseAll.Enable(True)
            self.btnPanel.Refresh()

    def get_grids(self):
        grids = dict()
        for i in range(self.nb.GetPageCount()):
            grids[self.nb.GetPageText(i)] = self.nb.GetPage(i).get_data()

        return grids if len(grids) > 0 else None

    def add_new_log(self, log):
        self.tcLog.AppendText(log)

    def target_is_valid(self):
        o = urlparse(self.tcTarget.GetValue())
        scheme = len(o.scheme) > 0 and (o.scheme == 'http' or o.scheme == 'https')

        try:
            host = len(o.hostname) > 0
        except:
            return False

        return scheme and host

    def set_tree_target(self, event):
        t = self.tcTarget.GetValue()

        if self.target_is_valid():
            self.tree.SetItemText(self.treeRoot, urlparse(self.tcTarget.GetValue()).hostname)
            self.tree.Show()
            self.tree.SetItemImage(self.treeRoot, TREE_ICONS['target'])
        else:
            self.tree.SetItemText(self.treeRoot, '')

    def get_icon(self, img):
        return wx.Image(BUTTON_ICONS[img],
                        wx.BITMAP_TYPE_PNG).Scale(24, 24).ConvertToBitmap()


class App(wx.App):
    def OnInit(self):
        self.frame = Frame(None, -1, '')
        self.SetTopWindow(self.frame)

        self.apiServer = SqlmapServer(self.frame, CONF['server']['host'], CONF['server']['port'])
        self.apiServer.setDaemon(True)
        self.apiServer.start()

        self.frame.SetSize((800, 600))
        self.frame.auiMgr.Update()
        self.frame.Center()
        self.frame.Show()
        return True


def main():
    app = App(False)    # prevents the redirection of sys.stdout and sys.stderr
    app.MainLoop()


if __name__ == '__main__':
    main()
