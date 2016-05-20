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
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtWebKit

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
		self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("RELOAD_PAGE"), lambda: self.tabs[self.tab_stack.currentIndex()][2].reload())
		self.tabs = [[QtGui.QWidget(), QtGui.QGridLayout()], [QtGui.QWidget(), QtGui.QGridLayout()]]
		self.tab_stack.addTab(self.tabs[0][0], '')
		self.tab_stack.addTab(self.tabs[1][0], '+')
		self.current_links = []
		self.create_widgets()
		QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
		self.visited = []
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
		self.go_button = QtGui.QPushButton(self.window)
		self.go_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/go.png")))
		self.go_button.clicked.connect(self.load_page)
		self.grid.addWidget(self.go_button, 0, 6)
		self.del_button = QtGui.QToolButton(self.tab_stack)
		self.del_button.setText('x')
		self.del_font = self.del_button.font()
		self.del_font.setBold(True)
		self.del_button.setFont(self.del_font)
		self.tab_stack.setCornerWidget(self.del_button)
		self.del_button.clicked.connect(self.remove_tab)
		self.url_field.returnPressed.connect(self.go_button.click)
		self.grid.addWidget(self.tab_stack, 2, 0, 1, 7)
		self.compose_tab(0)
		self.back_button.clicked.connect(lambda: self.tabs[self.tab_stack.currentIndex()][2].back())
		self.forward_button.clicked.connect(lambda: self.tabs[self.tab_stack.currentIndex()][2].forward())
		self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("ADD_TAB"), lambda: self.add_tab(len(self.tabs)-1))
		self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("CHANGE_TAB"), lambda: self.change_tab())
		self.tab_stack.connect(self.tab_stack, QtCore.SIGNAL("REMOVE_TAB"), lambda: self.remove_tab())
	
	def add_tab(self, i):
		if i == len(self.tabs)-1:
			self.tabs.insert(i, [QtGui.QWidget(), QtGui.QGridLayout()])
			self.tab_stack.addTab(self.tabs[-2][0], "New tab")
			self.tab_stack.setCurrentIndex(len(self.tabs)-2)
			self.compose_tab(len(self.tabs)-2)
			self.tab_stack.addTab(self.tabs[-1][0], '+')
			
	def change_tab(self):
		if len(self.tabs) > 2:
			if self.tab_stack.currentIndex() == len(self.tabs)-2:
				self.tab_stack.setCurrentIndex(0)
			else:
				self.tab_stack.setCurrentIndex(self.tab_stack.currentIndex()+1)
		
	def remove_tab(self):
		if len(self.tabs) > 2:
			self.tab_stack.removeTab(self.tab_stack.currentIndex())
			self.tabs[self.tab_stack.currentIndex()][2].page().settings().clearMemoryCaches()
			for QWebElement in self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findAllElements('*').toList():
				if QWebElement.tagName() == "EMBED":
					QWebElement.removeFromDocument()
			self.tabs.pop(self.tab_stack.currentIndex())
			self.current_links.pop(self.tab_stack.currentIndex())
			self.tab_stack.addTab(self.tabs[-1][0], '+')
			self.url_field.setText(self.current_links[self.tab_stack.currentIndex()])
		
	def compose_tab(self, index):
		self.tabs[index].append(QtWebKit.QWebView())
		self.tabs[index][0].setLayout(self.tabs[index][1])
		self.tabs[index][1].addWidget(self.tabs[index][2])
		self.tabs[index][2].connect(self.tabs[index][2], QtCore.SIGNAL("linkClicked(const QUrl&)"), self.update_link)
		self.tabs[index][2].load(QtCore.QUrl("http://www.google.com"))
		self.url_field.setText("http://www.google.com")
		self.tabs[index][2].page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
		self.tabs[self.tab_stack.currentIndex()][2].loadProgress.connect(lambda: self.tab_stack.setTabText(
			self.tab_stack.currentIndex(), 
			"Loading..."
		))
		try:
			self.tabs[self.tab_stack.currentIndex()][2].loadFinished.connect(lambda: self.tab_stack.setTabText(
				self.tab_stack.currentIndex(), 
				self.tabs[self.tab_stack.currentIndex()][2].page().mainFrame().findFirstElement("title").toPlainText()
			))
		except NameError as e:
			pass
		self.current_links.insert(index, self.url_field.text())
		self.tabs[index][2].show()
		
	def load_page(self):
		self.visited.append((lambda s: s if "http://" in s else "http://" + s)(self.url_field.text()))
		self.tabs[self.tab_stack.currentIndex()][2].load(QtCore.QUrl(self.visited[-1]))
		self.current_index = len(self.visited)-1
		self.current_links[self.tab_stack.currentIndex()] = self.url_field.text()
	
	def update_link(self, url):
		self.url_field.setText(url.toString())
		self.current_links[self.tab_stack.currentIndex()] = url.toString()
		self.tabs[self.tab_stack.currentIndex()][2].load(url)
		
if __name__ == '__main__':
   app = App()
