# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx.grid


class GridTableBase(wx.grid.PyGridTableBase):
    def __init__(self, data, cols):
        wx.grid.PyGridTableBase.__init__(self)

        self.cols = cols
        self.data = data

    def GetColLabelValue(self, col):
        return self.cols[col]

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.cols)

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, val):
        self.data[row][col] = val


class GridTable(wx.grid.Grid):
    def __init__(self, parent, id, data, cols):
        wx.grid.Grid.__init__(self, parent, id)

        self.dict = {'cols': cols, 'data': data}

        self.SetTable(GridTableBase(data, cols))
        self.SetRowLabelSize(48)
        self.AutoSizeRows()
        self.SetColLabelSize(24)

    def get_data(self):
        return self.dict
