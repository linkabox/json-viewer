
import json
import collections

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ui_res.json_win import Ui_MainWindow


class QJsonTreeItem(object):
    def __init__(self, parent=None):
        self._parent = parent

        self._key = ""
        self._value = ""
        self._type = None
        self._children = list()

    def appendChild(self, item):
        self._children.append(item)
    
    def removeChild(self, child):
        if child in self._children:
            self._children.remove(child)

    def child(self, row):
        return self._children[row]

    def parent(self):
        return self._parent

    def childCount(self):
        return len(self._children)

    def row(self):
        return (
            self._parent._children.index(self)
            if self._parent else 0
        )

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, typ):
        self._type = typ

    def isEditable(self):
        if issubclass(self._type, list) or issubclass(self._type, dict):
            return False
        return True

    def isPrimitive(self):
        if issubclass(self._type, list) or issubclass(self._type, dict):
            return False
        return True
    
    def addIntField(self):
        newItem = QJsonTreeItem(self)
        newItem.key = "New Key"
        newItem.type = type(int)
        newItem.value = 0
        self.appendChild(newItem)

    @classmethod
    def load(self, value, parent=None, sort=True):
        rootItem = QJsonTreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = (
                sorted(value.items())
                if sort else value.items()
            )

            for key, value in items:
                child = self.load(value, rootItem)
                child.key = key
                child.type = type(value)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = self.load(value, rootItem)
                child.key = str(index)
                child.type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = value
            rootItem.type = type(value)

        return rootItem


class QJsonModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(QJsonModel, self).__init__(parent)

        self._rootItem = QJsonTreeItem()
        self._headers = ("key", "value", "type")

    def getRoot(self):
        return self._rootItem

    def load(self, document):
        """Load from dictionary

        Arguments:
            document (dict): JSON-compatible dictionary

        """

        assert isinstance(document, (dict, list, tuple)), (
            "`document` must be of dict, list or tuple, "
            "not %s" % type(document)
        )

        self.beginResetModel()

        self._rootItem = QJsonTreeItem.load(document)
        self._rootItem.type = type(document)

        self.endResetModel()

        return True

    def json(self, root=None):
        """Serialise model as JSON-compliant dictionary

        Arguments:
            root (QJsonTreeItem, optional): Serialise from here
                defaults to the the top-level item

        Returns:
            model as dict

        """

        root = root or self._rootItem
        return self.genJson(root)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

            if index.column() == 2:
                return str(item.type)

        elif role == QtCore.Qt.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)
                print("Edit item type:", item.type)

                # self.dataChanged.emit(index, index, [QtCore.Qt.EditRole])
                self.dataChanged.emit(index, index)

                return True

        return False

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            return self._headers[section]

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        print("=====parent", childItem.key)
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 3

    def flags(self, index):
        flags = super(QJsonModel, self).flags(index)

        if index.column() == 1:
            item = index.internalPointer()
            if item.isEditable():
                return QtCore.Qt.ItemIsEditable | flags
        
        return flags

    def genJson(self, item):
        nchild = item.childCount()

        if item.type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.genJson(ch)
            return document

        elif item.type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.genJson(ch))
            return document

        else:
            return item.value
    
class JsonEditor(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(JsonEditor, self).__init__(parent=parent)
        self.setupUi(self)

        self.model = QJsonModel()
        self.json_view.setModel(self.model)

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
        rootItem = self.model.getRoot()
        rootItem.addIntField()
        self.model.layoutChanged.emit()

    def do_item_del(self):
        if self.selected_item is None:
            return
        
        rootItem = self.model.getRoot()
        rootItem.removeChild(self.selected_item)
        self.selected_item = None
        self.model.layoutChanged.emit()
    
    def prepareMenu(self, pos):
        index = self.json_view.indexAt(pos)
        print("prepareMenu:", pos, index, index.internalPointer())
        if not index.isValid():
            return
        
        menu = QMenu("ItemAction", self.json_view)
        item = index.internalPointer()
        self.selected_item = item
        # if item.isPrimitive():

        menu.addAction(self.item_add_action)
        menu.addAction(self.item_del_action)
        if not menu.isEmpty():
            menu.exec(self.json_view.viewport().mapToGlobal(pos))
    
    def on_click_test(self):
        self.load_json("address.json")

    def load_json(self, jpath):
        jfile = open(jpath)
        jdata = json.load(jfile)
        self.model.load(jdata)
    
    def sizeHint(self):
        return QSize(640, 480)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    json_editor = JsonEditor()
    json_editor.load_json("test.json")

    app.exec_()
