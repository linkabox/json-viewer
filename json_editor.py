
import json
import collections

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ui_res.json_win import Ui_MainWindow

class QJsonTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, key, value=None, parent=None):
        super().__init__(parent)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setKey(key)

        self.defaultVal = value
        self.setValueType(type(value))
        self.setValue(value)
    
    def setKey(self, key):
        self.key = key
        self.setText(0, str(key))
    
    def setValueType(self, v_type):
        self.value_type = v_type
        self.setText(2, str(self.value_type))

    def setValue(self, val):
        self.value = val
        self.setText(1, str(self.value))

    def setData(self, column: int, role: int, value):
        super().setData(column, role, value)
        # print("override setData:", column, role, value, type(value))
    
    def isRoot(self):
        return self.parent() == None
    
    def isPrimitive(self):
        if issubclass(self.value_type, list) or issubclass(self.value_type, dict):
            return False
        return True
    
    def removeChild(self, child):
        # 基础类型没有子节点
        if not self.isRoot() and self.isPrimitive():
            return

        idx = self.indexOfChild(child)

        # 列表类型按idx值移除，并重置后续节点key值
        if issubclass(self.value_type, list):
            p_list = self.value
            for i in range(len(p_list)-1, idx, -1):
                child = self.child(i)
                child.setKey(i-1)

            del p_list[idx]
            print("remove list idx:", idx)
        else:
            self.value[child.key] = None
            print("remove child key:", idx, child.key)

        self.takeChild(idx)
        
    
class JsonEditor(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(JsonEditor, self).__init__(parent=parent)
        self.setupUi(self)

        self.json_view.customContextMenuRequested.connect(self.prepareMenu)
        self.item_add_action = QAction("新增", self.json_view)
        self.item_add_action.triggered.connect(self.do_item_add)
        self.item_del_action = QAction("删除", self.json_view)
        self.item_del_action.triggered.connect(self.do_item_del)
        self.selected_item = None

        self.test_btn.clicked.connect(self.on_click_test)

        self.setWindowTitle("JSON Viewer")
        self.show()

    def do_item_add(self):
        pass

    def do_item_del(self):
        if self.selected_item is None:
            return
        
        parent = self.selected_item.parent()
        parent.removeChild(self.selected_item)
        self.selected_item = None
    
    def prepareMenu(self, pos):
        treeItem = self.json_view.itemAt(pos)
        if treeItem is None:
            return
        print("prepareMenu:", pos, treeItem)
        
        menu = QMenu("ItemAction", self.json_view)
        self.selected_item = treeItem

        menu.addAction(self.item_add_action)
        menu.addAction(self.item_del_action)
        if not menu.isEmpty():
            menu.exec(self.json_view.viewport().mapToGlobal(pos))
    
    def on_click_test(self):
        # self.load_json("address.json")
        with open('dump.json', 'w') as outfile:
            json_str = json.dump(self.json_data, outfile, indent=4)

    def load_json(self, jpath):
        jfile = open(jpath)
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)

        self.json_data = jdata
        self.json_view.clear()

        self.root_item = QJsonTreeWidgetItem(jpath, self.json_data)
        self.json_view.addTopLevelItem(self.root_item)
        self.recursive_json_tree(self.json_data, self.root_item)

        self.root_item.setExpanded(True)
        
    def recursive_json_tree(self, jdata, parent):
        if isinstance(jdata, dict):
            for key, val in jdata.items():
                self.add_tree_row(key, val, parent)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                self.add_tree_row(i, val, parent)
        else:
            print("This should never be reached!")
    
    def add_tree_row(self, key, val, parent):
        if isinstance(val, dict) or isinstance(val, list):
            row_item = QJsonTreeWidgetItem(key, val, parent)
            self.recursive_json_tree(val, row_item)
        else:
            row_item = QJsonTreeWidgetItem(key, val, parent)
    
    def sizeHint(self):
        return QSize(640, 480)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    json_editor = JsonEditor()
    json_editor.load_json("test.json")

    app.exec_()
