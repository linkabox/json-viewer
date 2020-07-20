
import json
import collections
import copy
from pathlib import Path

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ui_res.json_win import Ui_MainWindow

DEBUG = True
    
class JsonEditor(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(JsonEditor, self).__init__(parent=parent)
        self.setupUi(self)
        self.test_btn.clicked.connect(self.on_click_test)

        self.setWindowTitle("JSON Viewer")
        self.show()
    
    def on_click_test(self):
        # self.load_json("address.json")
        with open('dump.json', 'w') as outfile:
            json_str = json.dump(self.json_data, outfile, indent=4)
        print("!!!on_click_test")

    def load_json(self, jpath):
        jpath = Path(jpath)
        with open(jpath) as jfile:
            jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
        
        jscheme_path = jpath.with_suffix('.schem.json')
        jscheme = None
        if jscheme_path.exists():
            with open(jscheme_path) as jschemeFile:
                jscheme = json.load(jschemeFile, object_pairs_hook=collections.OrderedDict)

        self.json_data = jdata
        self.json_view.load_json(jdata, jpath, jscheme)
    
    def sizeHint(self):
        return QSize(640, 480)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    json_editor = JsonEditor()
    json_editor.load_json("test.json")

    app.exec_()
