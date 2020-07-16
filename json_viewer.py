#!/usr/bin/env python3

__author__ = "Ashwin Nanjappa"

# GUI viewer to view JSON data as tree.
# Ubuntu packages needed:
# python3-pyqt5

# Std
import argparse
import collections
import json
import sys

# External
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class JsonTreeItem:

    def __init__(self):
        self.text_list = []
        self.titem_list = []

    def append(self, text_list, titem):
        for text in text_list:
            self.text_list.append(text)
            self.titem_list.append(titem)

    # Return model indices that match string
    def find(self, find_str):

        titem_list = []
        for i, s in enumerate(self.text_list):
            if find_str in s:
                titem_list.append(self.titem_list[i])

        return titem_list


class JsonView(QtWidgets.QWidget):

    def __init__(self):
        super(JsonView, self).__init__()

        self.find_box = None
        self.tree_widget = None
        self.text_to_titem = JsonTreeItem()
        self.find_str = ""
        self.found_titem_list = []
        self.found_idx = 0

        # Find UI

        find_layout = self.make_find_ui()

        # Tree

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        # self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        root_item = QtWidgets.QTreeWidgetItem(["Root"])

        self.tree_widget.addTopLevelItem(root_item)
        root_item.setExpanded(True)
        self.tree_root = root_item

        # Add table to layout

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree_widget)

        # Group box

        gbox = QtWidgets.QGroupBox("JsonEditor")
        gbox.setLayout(layout)

        layout2 = QtWidgets.QVBoxLayout()
        layout2.addLayout(find_layout)
        layout2.addWidget(gbox)

        self.setLayout(layout2)

    def make_find_ui(self):

        # Text box
        self.find_box = QtWidgets.QLineEdit()
        self.find_box.returnPressed.connect(self.find_button_clicked)

        # Find Button
        find_button = QtWidgets.QPushButton("Find")
        find_button.clicked.connect(self.find_button_clicked)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.find_box)
        layout.addWidget(find_button)

        return layout

    def find_button_clicked(self):

        find_str = self.find_box.text()

        # Very common for use to click Find on empty string
        if find_str == "":
            return

        # New search string
        if find_str != self.find_str:
            self.find_str = find_str
            self.found_titem_list = self.text_to_titem.find(self.find_str)
            self.found_idx = 0
        else:
            item_num = len(self.found_titem_list)
            self.found_idx = (self.found_idx + 1) % item_num

        self.tree_widget.setCurrentItem(self.found_titem_list[self.found_idx])

    def update_view(self, fpath):
        jfile = open(fpath)
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)

        self.tree_widget.clear()
        self.recurse_jdata(jdata)

    def recurse_jdata(self, jdata, tree_parent=None):

        if isinstance(jdata, dict):
            for key, val in jdata.items():
                self.tree_add_row(key, val, tree_parent)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                key = str(i)
                self.tree_add_row(key, val, tree_parent)
        else:
            print("This should never be reached!")

    def tree_add_row(self, key, val, tree_parent):

        text_list = []

        if isinstance(val, dict) or isinstance(val, list):
            text_list.append(key)
            node_name = "%s%s" % (key, str(type(val)))
            row_item = QtWidgets.QTreeWidgetItem([node_name])
            self.recurse_jdata(val, row_item)
        else:
            text_list.append(key)
            text_list.append(str(val))
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)])

        if tree_parent is None:
            self.tree_widget.addTopLevelItem(row_item)
        else:
            tree_parent.addChild(row_item)

        row_item.setExpanded(True)
        row_item.setFlags(row_item.flags() | Qt.ItemIsEditable)
        self.text_to_titem.append(text_list, row_item)


class JsonEditor(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(JsonEditor, self).__init__(parent=parent)
        self.setupUi(self)

        fpath = "test.json"  # sys.argv[1]
        json_view = JsonView()
        json_view.update_view(fpath)

        self.setCentralWidget(json_view)
        self.setWindowTitle("JSON Viewer")
        self.show()

    def sizeHint(self):
        return QSize(640, 480)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()


def main():
    qt_app = QtWidgets.QApplication(sys.argv)
    json_editor = JsonEditor()
    sys.exit(qt_app.exec_())


if "__main__" == __name__:
    main()
