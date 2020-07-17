
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
NoneType = type(None)

class QJsonTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, key, value=None, parent=None, scheme=None):
        self.value = None
        super().__init__(parent)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setKey(key)
        if scheme is None:
            self.scheme = value
        else:
            self.scheme = scheme
        
        self.setValueType(type(self.scheme))
        # 缓存下子节点scheme
        if issubclass(self.value_type, list):
            self.child_scheme = self.scheme[0]
        elif issubclass(self.value_type, dict):
            self.child_scheme = next(iter(value.values()))
        else:
            self.child_scheme = None
        
        self.setValue(value)
    
    def setKey(self, key):
        self.key = key
        self.setText(0, str(key))

    def setValueType(self, v_type):
        self.value_type = v_type
        self.setText(2, str(self.value_type))

    def setValue(self, val):
        try:
            if issubclass(self.value_type, NoneType):
                self.value = val
                self.setText(1, str(self.value))
            elif self.isPrimitive():
                self.value = self.value_type(val)
                self.setText(1, str(self.value))
            else:
                self.value = val

            if DEBUG:
                self.setText(3, str(id(self.value)))
        except ValueError as e:
            print(e)
        
    def setData(self, column: int, role: int, str_val):
        if DEBUG:
            print("override setData:", column, role, str_val, type(str_val))
        if role != Qt.EditRole:
            super().setData(column, role, str_val)
            return

        if column == 0:
            parent = self.parent()
            if parent and issubclass(parent.value_type, dict):
                new_key = str_val
                parent_map = parent.value
                cur_val = parent_map.pop(self.key)
                parent_map[new_key] = cur_val
                self.setKey(new_key)

        elif column == 1:
            # 限制只有基础类型才能编辑
            if not self.isPrimitive():
                return
            self.setValue(str_val)
    
    def isRoot(self):
        return self.parent() == None
    
    def isPrimitive(self):
        if self.value_type is None:
            return False

        if issubclass(self.value_type, list) or issubclass(self.value_type, dict):
            return False
        return True

    def addChild(self):
        if self.isPrimitive():
            return
        
        if issubclass(self.value_type, list):
            p_list = self.value
            child_obj = copy.deepcopy(self.child_scheme)
            p_list.append(child_obj)
            idx = len(p_list)-1
            self._add_child_recursive(idx, child_obj, self, self.child_scheme)
        elif issubclass(self.value_type, dict):
            p_dict = self.value
            child_obj = copy.deepcopy(self.child_scheme)
            key = str(id(child_obj))
            p_dict[key] = child_obj
            self._add_child_recursive(key, child_obj, self, self.child_scheme)
    
    def recursive_json_tree(self, jdata, parent=None, scheme=None):
        if parent is None:
            parent = self

        if isinstance(jdata, dict):
            for key, val in jdata.items():
                self._add_child_recursive(key, val, parent, scheme)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                self._add_child_recursive(i, val, parent, scheme)
        else:
            print("This should never be reached!")

    def _add_child_recursive(self, key, val, parent, scheme):
        if isinstance(val, dict) or isinstance(val, list):
            row_item = QJsonTreeWidgetItem(key, val, parent, scheme)
            self.recursive_json_tree(val, row_item)
        else:
            row_item = QJsonTreeWidgetItem(key, val, parent, scheme)
    
    def removeChild(self, child):
        # 基础类型没有子节点
        if self.isPrimitive():
            return

        idx = self.indexOfChild(child)

        # 列表类型按idx值移除，并重置后续节点key值
        if issubclass(self.value_type, list):
            p_list = self.value
            for i in range(len(p_list)-1, idx, -1):
                child = self.child(i)
                child.setKey(i-1)

            del p_list[idx]
            if DEBUG:
                print("remove list idx:", idx)
        else:
            self.value[child.key] = None
            if DEBUG:
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
        if self.selected_item is None:
            return
        
        self.selected_item.addChild()
        self.selected_item = None

    def do_item_del(self):
        if self.selected_item is None:
            return
        
        parent = self.selected_item.parent()
        if parent is not None:
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
        jpath = Path(jpath)
        with open(jpath) as jfile:
            jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
        
        jscheme_path = jpath.with_suffix('.schem.json')
        jscheme = None
        if jscheme_path.exists():
            with open(jscheme_path) as jschemeFile:
                jscheme = json.load(jschemeFile, object_pairs_hook=collections.OrderedDict)

        self.json_data = jdata
        self.json_view.clear()

        self.root_item = QJsonTreeWidgetItem(jpath, self.json_data)
        self.json_view.addTopLevelItem(self.root_item)
        self.root_item.recursive_json_tree(self.json_data, scheme=jscheme)

        self.root_item.setExpanded(True)
    
    def sizeHint(self):
        return QSize(640, 480)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    json_editor = JsonEditor()
    json_editor.load_json("test.json")

    app.exec_()
