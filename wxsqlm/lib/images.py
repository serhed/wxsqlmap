# -*- coding: utf-8 -*-

__author__ = 'Mehmet Öztürk'

import wx

IMG_PATH = 'wxsqlm/images/'
IMG_PATH_TREE = IMG_PATH+'tree/'
IMG_PATH_BUTTONS = IMG_PATH+'buttons/'

LOGO_ICON = IMG_PATH+'logo.png'

TREE_ICONS = dict(
    target=wx.Image(IMG_PATH_TREE+'target.png', wx.BITMAP_TYPE_PNG),
    # http://openiconlibrary.sourceforge.net/gallery2/?./Icons/devices/computer-4.png

    db=wx.Image(IMG_PATH_TREE+'db.png', wx.BITMAP_TYPE_PNG),
    # http://www.iconarchive.com/show/colobrush-icons-by-eponas-deeway/system-database-icon.html

    tbl=wx.Image(IMG_PATH_TREE+'tbl.png', wx.BITMAP_TYPE_PNG),
    # http://icones.pro/en/table-4-png-image.html

    col=wx.Image(IMG_PATH_TREE+'col.png', wx.BITMAP_TYPE_PNG))
    # http://www.iconarchive.com/show/farm-fresh-icons-by-fatcow/column-one-icon.html

BUTTON_ICONS = dict(
    target=IMG_PATH_BUTTONS+'target.png',
    # http://openiconlibrary.sourceforge.net/gallery2/?./Icons/devices/computer-4.png

    db=IMG_PATH_BUTTONS+'db.png',

    tbl=IMG_PATH_BUTTONS+'tbl.png',
    # http://icones.pro/en/multiple-table-png-image.html

    tblDump=IMG_PATH_BUTTONS+'tblDump.png',
    # http://www.iconarchive.com/show/farm-fresh-icons-by-fatcow/table-go-icon.html

    col=IMG_PATH_BUTTONS+'col.png',
    # http://www.iconarchive.com/show/farm-fresh-icons-by-fatcow/column-one-icon.html

    save=IMG_PATH_BUTTONS+'save.png',
    # http://www.iconarchive.com/show/toolbar-icons-by-shlyapnikova/save-icon.html

    stop=IMG_PATH_BUTTONS+'stop.png',
    # http://findicons.com/icon/89008/no?width=24

    options=IMG_PATH_BUTTONS+'options.png',
    # http://findicons.com/icon/229801/gnome_system_config?width=24

    view=IMG_PATH_BUTTONS+'view.png',
    # http://www.softicons.com/free-icons/toolbar-icons/24x24-free-button-icons-by-aha-soft/view-green-icon

    closeTab=IMG_PATH_BUTTONS+'closeTab.png')
    # http://www.iconarchive.com/show/oxygen-icons-by-oxygen-icons.org/Actions-tab-close-icon.html