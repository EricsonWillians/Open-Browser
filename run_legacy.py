#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Open Browser
#  
#  Copyright 2016 Ericson Willians (Rederick Deathwill) <EricsonWRP@ERICSONWRP-PC>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import json
import os
import dropbox, configparser
from PyQt4 import QtCore, QtTest, QtGui, QtWebKit


class Serializable:
    def __init__(self):
        self._file = None

    def serialize(self, path, mode, data):
        try:
            with open(path, mode) as outfile:
                self._file = outfile
                self._file.write(json.dumps(data))
        except:
            raise FileNotFoundError()


class Bookmarks(Serializable):
    def __init__(self):
        Serializable.__init__(self)
        if os.path.isfile("bookmarks.json"):
            self.data = self.load("bookmarks.json")
        else:
            self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        for bookmark in self.data:
            yield bookmark

    def get_data(self):
        return self.data

    def write(self, path):
        self.serialize(path, 'w', self.get_data())

    def load(self, path):
        with open(path, 'r') as _file:
            return json.load(_file)


class CQLineEdit(QtGui.QLineEdit):
    def mousePressEvent(self, e):
        self.selectAll()


class CQTabWidget(QtGui.QTabWidget):
    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_F5:
                self.emit(QtCore.SIGNAL("RELOAD_PAGE"))
            elif event.key() == QtCore.Qt.Key_Control:
                self.control_key = True

    def keyReleaseEvent(self, event):
        try:
            if type(event) == QtGui.QKeyEvent:
                if self.control_key == True:
                    if event.key() == QtCore.Qt.Key_T:
                        self.emit(QtCore.SIGNAL("ADD_TAB"))
                    elif event.key() == QtCore.Qt.Key_Tab:
                        self.emit(QtCore.SIGNAL("CHANGE_TAB"))
                    elif event.key() == QtCore.Qt.Key_F4:
                        self.emit(QtCore.SIGNAL("REMOVE_TAB"))
                if event.key() == QtCore.Qt.Key_Control:
                    self.control_key = False
        except AttributeError as e:
            pass


class CQWebView(QtWebKit.QWebView):
    def __init__(self):
        QtWebKit.QWebView.__init__(self)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton:
                    QtTest.QTest.mouseClick(self, QtCore.Qt.MiddleButton, QtCore.Qt.NoModifier, event.pos())
                    return True
        return False


class App(QtGui.QApplication):
    def __init__(self):
        QtGui.QApplication.__init__(self, sys.argv)
        self.window = QtGui.QWidget()
        self.window.setGeometry(100, 100, 800, 600)
        self.window.setWindowTitle("Open Browser")
        self.grid = QtGui.QGridLayout()
        self.window.setLayout(self.grid)
        self.tab_stack = CQTabWidget()
        self.tab_stack.setTabShape(QtGui.QTabWidget.TabShape(QtGui.QTabWidget.Triangular))
        self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("currentChanged(int)"), self.add_tab)
        self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("RELOAD_PAGE"),
                               lambda: self.tabs[self.tab_stack.currentIndex()][2].reload())
        self.tabs = [[QtGui.QWidget(), QtGui.QGridLayout()], [QtGui.QWidget(), QtGui.QGridLayout()]]
        self.tab_stack.addTab(self.tabs[0][0], '')
        self.tab_stack.addTab(self.tabs[1][0], '+')
        self.current_links = []
        self.visited = []
        self.bookmarks = Bookmarks()
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.create_widgets()
        self.current_index = 0
        self.window.showMaximized()
        sys.exit(self.exec_())

    def create_widgets(self):
        self.back_button = QtGui.QPushButton(self.window)
        self.back_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/back.png")))
        self.grid.addWidget(self.back_button, 0, 0)
        self.forward_button = QtGui.QPushButton(self.window)
        self.forward_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/forward.png")))
        self.grid.addWidget(self.forward_button, 0, 1)
        self.refresh_button = QtGui.QPushButton(self.window)
        self.refresh_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/refresh.png")))
        self.refresh_button.clicked.connect(lambda: self.tabs[self.tab_stack.currentIndex()][2].reload())
        self.grid.addWidget(self.refresh_button, 0, 2)
        self.google_button = QtGui.QPushButton(self.window)
        self.google_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/google.png")))
        self.google_button.clicked.connect(lambda: [
            self.tabs[self.tab_stack.currentIndex()][2].load(QtCore.QUrl("http://www.google.com")),
            self.url_field.setText("http://www.google.com"),
            self.tab_stack.setTabText(self.tab_stack.currentIndex(), "http://www.google.com")
        ])
        self.grid.addWidget(self.google_button, 0, 3)
        self.url_label = QtGui.QLabel(self.window)
        self.url_label.setText("URL: ")
        self.url_label.setFont(QtGui.QFont("Arial", weight=QtGui.QFont.Bold))
        self.grid.addWidget(self.url_label, 0, 4)
        self.url_field = CQLineEdit(self.window)
        self.url_field.insert("http://")
        self.grid.addWidget(self.url_field, 0, 5)
        self.star_button = QtGui.QPushButton(self.window)
        self.star_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/star.png")))
        self.star_button.clicked.connect(self.bookmark)
        self.grid.addWidget(self.star_button, 0, 7)
        self.go_button = QtGui.QPushButton(self.window)
        self.go_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/go.png")))
        self.go_button.clicked.connect(self.load_page)
        self.grid.addWidget(self.go_button, 0, 8)
        self.bookmarks_window = QtGui.QWidget()
        self.bookmarks_grid = QtGui.QGridLayout()
        self.bookmarks_window.setLayout(self.bookmarks_grid)
        self.bookmarks_window.setWindowTitle("Bookmarks")
        self.bookmarks_window.setFixedSize(400, 600)
        self.bookmarks_window.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("GFX/fav.png")))
        self.bookmarks_list = QtGui.QListWidget()
        self.bookmarks_list.itemClicked.connect(lambda x: self.update_link(self.bookmarks[x.text()]))
        self.bookmarks_grid.addWidget(self.bookmarks_list)
        self.bookmarks_button = QtGui.QPushButton(self.window)
        self.bookmarks_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/fav.png")))
        self.bookmarks_button.clicked.connect(
            lambda: [self.bookmarks_window.show(), self.center_window(self.bookmarks_window),
                     self.bookmarks_window.activateWindow()])
        self.grid.addWidget(self.bookmarks_button, 0, 9)

        self.dropbox_button = QtGui.QPushButton(self.window)
        self.dropbox_button.setIcon(dbxIngration.setIconInButton(None))
        self.dropbox_button.clicked.connect(self.dropdox_click)
        self.grid.addWidget(self.dropbox_button, 0, 10)

        self.del_button = QtGui.QToolButton(self.tab_stack)
        self.del_button.setText('x')
        self.del_font = self.del_button.font()
        self.del_font.setBold(True)
        self.del_button.setFont(self.del_font)
        self.tab_stack.setCornerWidget(self.del_button)
        self.del_button.clicked.connect(self.remove_tab)
        self.url_field.returnPressed.connect(self.go_button.click)
        self.grid.addWidget(self.tab_stack, 2, 0, 1, 11)
        self.compose_tab(0)
        self.back_button.clicked.connect(self.go_back)
        self.forward_button.clicked.connect(self.go_forward)
        self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("ADD_TAB"), lambda: self.add_tab(len(self.tabs) - 1))
        self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("CHANGE_TAB"), lambda: self.change_tab())
        self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("REMOVE_TAB"), lambda: self.remove_tab())
        for x in self.bookmarks.get_data():
            self.bookmarks_list.addItem(x)

    def go_back(self):
        self.tabs[self.tab_stack.currentIndex()][2].back()

    # url update do be implemented...

    def go_forward(self):
        self.tabs[self.tab_stack.currentIndex()][2].forward()

    # url update do be implemented...

    def add_tab(self, i):
        if i == len(self.tabs) - 1:
            self.tabs.insert(i, [QtGui.QWidget(), QtGui.QGridLayout()])
            self.tab_stack.addTab(self.tabs[-2][0], "New tab")
            self.tab_stack.setCurrentIndex(len(self.tabs) - 2)
            self.compose_tab(len(self.tabs) - 2)
            self.tab_stack.addTab(self.tabs[-1][0], '+')

    def change_tab(self):
        if len(self.tabs) > 2:
            if self.tab_stack.currentIndex() == len(self.tabs) - 2:
                self.tab_stack.setCurrentIndex(0)
            else:
                self.tab_stack.setCurrentIndex(self.tab_stack.currentIndex() + 1)

    def remove_tab(self):
        if len(self.tabs) > 2:
            self.tab_stack.removeTab(self.tab_stack.currentIndex())
            self.tabs[self.tab_stack.currentIndex()][2].page().settings().clearMemoryCaches()
            for QWebElement in self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findAllElements(
                    '*').toList():
                if QWebElement.tagName() == "EMBED":
                    QWebElement.removeFromDocument()
            self.tabs.pop(self.tab_stack.currentIndex())
            self.current_links.pop(self.tab_stack.currentIndex())
            self.tab_stack.addTab(self.tabs[-1][0], '+')
            self.url_field.setText(self.current_links[self.tab_stack.currentIndex()])

    def compose_tab(self, index):
        self.tabs[index].append(CQWebView())
        self.tabs[index][0].setLayout(self.tabs[index][1])
        self.tabs[index][1].addWidget(self.tabs[index][2])
        self.tabs[index][2].page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.tabs[index][2].connect(self.tabs[index][2], QtCore.SIGNAL("linkClicked(const QUrl&)"), self.update_link)
        # To be implemented somehow... {
        self.tabs[index][2].connect(self.tabs[index][2], QtCore.SIGNAL("OPEN_IN_NEW_TAB"), lambda: [
            self.add_tab(len(self.tabs) - 1),
            None
        ])
        # }
        self.current_links.insert(index, self.url_field.text())
        self.update_link(QtCore.QUrl("http://www.google.com"))
        try:
            self.tabs[self.tab_stack.currentIndex()][2].loadProgress.connect(lambda: [self.tab_stack.setTabText(
                self.tab_stack.currentIndex(),
                "Loading..."
            ), (lambda x: self.star_button.setIcon(
                QtGui.QIcon(QtGui.QPixmap("GFX/star.png"))) if x not in self.bookmarks else self.star_button.setIcon(
                QtGui.QIcon(QtGui.QPixmap("GFX/removestar.png"))))(
                self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findFirstElement(
                    "title").toPlainText())])
            self.tabs[self.tab_stack.currentIndex()][2].loadFinished.connect(lambda: self.tab_stack.setTabText(
                self.tab_stack.currentIndex(),
                self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findFirstElement("title").toPlainText()
            ))
        except AttributeError as e:
            pass
        self.tabs[index][2].show()

    def load_page(self):
        self.visited.append((lambda s: s if "http" in s else (
        lambda x: x if ' ' not in x and '.' in x else "https://www.google.com/search?q=" + s)("https://" + s))(
            self.url_field.text()))
        self.tabs[self.tab_stack.currentIndex()][2].load(QtCore.QUrl(self.visited[-1]))
        self.current_index = len(self.visited) - 1
        self.current_links[self.tab_stack.currentIndex()] = self.url_field.text()

    def update_link(self, url):
        if type(url) == QtCore.QUrl:
            self.url_field.setText(url.toString())
            self.current_links[self.tab_stack.currentIndex()] = url.toString()
            self.tabs[self.tab_stack.currentIndex()][2].load(url)
        elif type(url) == str:
            self.url_field.setText(url)
            self.current_links[self.tab_stack.currentIndex()] = url
            self.tabs[self.tab_stack.currentIndex()][2].load(QtCore.QUrl(url))
        page_title = self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findFirstElement(
            "title").toPlainText()

    def bookmark(self):
        page_title = self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findFirstElement(
            "title").toPlainText()
        if page_title not in self.bookmarks:
            self.star_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/removestar.png")))
            self.bookmarks[page_title] = self.current_links[self.tab_stack.currentIndex()]
            self.bookmarks_list.addItem(page_title)
        else:
            self.star_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/star.png")))
            self.bookmarks.data.pop(page_title, None)
            self.bookmarks_list.takeItem(
                self.bookmarks_list.row(self.bookmarks_list.findItems(page_title, QtCore.Qt.MatchExactly)[0]))
        self.bookmarks.write("bookmarks.json")
        dbxIngration.uploadFavorites(None)

    def center_window(self, w):
        frame_geometry = w.frameGeometry()
        screen = self.desktop().screenNumber(self.desktop().cursor().pos())
        center_point = self.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        w.move(frame_geometry.topLeft())

    def dropdox_click(self):
        dbx = dbxIngration(None)
        dbx.show()
        self.center_window(dbx)
        dbx.exec_()

class dbxIngration(QtGui.QWidget):

    def __init__(self, parent=None):
        super(dbxIngration, self).__init__(parent)
        self.dbx_tabWidget = QtGui.QTabWidget(self)
        self.createWidgets()

    def createWidgets(self):
        self.dbx_grid = QtGui.QGridLayout()
        self.dbx_code_label = QtGui.QLabel('Enter the code here: ')
        self.dbx_code_label.setFont(QtGui.QFont("Arial", weight=QtGui.QFont.Bold))
        self.dbx_getCode = QtGui.QLineEdit()
        self.dbx_grid.addWidget(self.dbx_code_label,0,1)
        self.dbx_grid.addWidget(self.dbx_getCode,0,2)
        self.dbx_save_button = QtGui.QPushButton('Save')
        self.dbx_save_button.setFixedWidth(90)
        self.dbx_save_button.clicked.connect(self.createAppFolder)
        self.dbx_grid.addWidget(self.dbx_save_button,0,3)
        self.dbx_grid.addWidget(self.dbx_tabWidget,3,1,1,3)
        self.generateCode()
        self.setLayout(self.dbx_grid)

    def loadUrl(self, url):
        view = QtWebKit.QWebView()
        view.connect(view, QtCore.SIGNAL('loadFinished(bool)'), self.loadFinished)
        view.connect(view, QtCore.SIGNAL('linkClicked(const QUrl&)'), self.linkClicked)
        view.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.dbx_tabWidget.setCurrentIndex(self.dbx_tabWidget.addTab(view, 'loading...'))
        view.load(url)

    def loadFinished(self, ok):
        index = self.dbx_tabWidget.indexOf(self.sender())
        self.dbx_tabWidget.setTabText(index, self.sender().url().host())

    def linkClicked(self, url):
        self.loadUrl(url)

    def generateCode(self):
        app_key = 'q6qqzbly9qycrot'
        app_secret_key = 'dmds9v8n328wzan'
        self.flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret_key)
        autorize_url = self.flow.start()
        self.loadUrl(QtCore.QUrl(autorize_url))

    def createAppFolder(self):
        s = '''[DROPBOX]
        access token =
        '''
        if os.path.exists('config.ini') is False:
            open('config.ini','w').write(s)

        access_token, user_id = self.flow.finish(self.dbx_getCode.text())
        configp = configparser.ConfigParser()
        configp.read('config.ini')
        configp['DROPBOX']['access token'] = access_token

        with open('config.ini', 'w') as configfile:
            configp.write(configfile)

        QtGui.QMessageBox.about(self.dbx_tabWidget, "Open Brower - Alert", "Code successfully saved!")

        self.close()

    def uploadFavorites(self):

        if os.path.exists('config.ini') is True:
            configb = configparser.ConfigParser()
            configb.read('config.ini')
            token = configb['DROPBOX']['access token']

            if token == '':
                pass
            else:
                dbx = dropbox.Dropbox(token)

                file_to = '/Favorites/bookmarks.json'

                with open('bookmarks.json', 'rb') as f:
                    dbx.files_upload(f, file_to, mode=dropbox.files.WriteMode.overwrite)

    def setIconInButton(self):
        if os.path.exists('config.ini') is True:
            configb = configparser.ConfigParser()
            configb.read('config.ini')

            token = configb['DROPBOX']['access token']

            if token == '':
                return QtGui.QIcon(QtGui.QPixmap("GFX/dropbox.png"))
            else:
                return QtGui.QIcon(QtGui.QPixmap("GFX/dropbox_conn.png"))
        else:
            return QtGui.QIcon(QtGui.QPixmap("GFX/dropbox.png"))



if __name__ == '__main__':
    app = App()
