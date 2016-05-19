#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PySim
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

class App(QtGui.QApplication):
	
	def __init__(self):
		QtGui.QApplication.__init__(self, sys.argv)
		self.window = QtGui.QWidget()
		self.window.setGeometry(100, 100, 800, 600)
		self.window.setWindowTitle("PySim")
		self.grid = QtGui.QGridLayout()
		self.window.setLayout(self.grid)
		self.create_widgets()
		QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
		self.visited = []
		self.current_index = 0
		self.window.showMaximized()
		sys.exit(self.exec_())
		
	def load_page(self):
		self.visited.append((lambda s: s if "http://" in s else "http://" + s)(self.url_field.text()))
		self.web.load(QtCore.QUrl(self.visited[-1]))
		self.current_index = len(self.visited)-1
		
	def go_back(self):
		if self.visited:
			if self.current_index > 0:
				self.current_index = self.current_index-1
			self.web.back()
		
	def go_forward(self):
		if self.visited:
			if self.current_index < len(self.visited)-1:
				self.current_index = self.current_index+1
			self.web.forward()
	
	def update_link(self, url):
		self.url_field.setText(url.toString())
		self.web.load(url)
		
	def create_widgets(self):
		self.url_label = QtGui.QLabel(self.window)
		self.url_label.setText("URL: ")
		self.grid.addWidget(self.url_label, 0, 2)
		self.url_field = CQLineEdit(self.window)
		self.url_field.insert("http://")
		self.grid.addWidget(self.url_field, 0, 3)
		self.go_button = QtGui.QPushButton(self.window)
		self.go_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/go.png")))
		self.go_button.clicked.connect(self.load_page)
		self.grid.addWidget(self.go_button, 0, 4)
		self.url_field.returnPressed.connect(self.go_button.click)
		self.web = QtWebKit.QWebView()
		self.web.connect(self.web, QtCore.SIGNAL("linkClicked(const QUrl&)"), self.update_link)
		self.web.load(QtCore.QUrl("http://www.google.com"))
		self.web.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
		self.grid.addWidget(self.web, 1, 0, 1, 5)
		self.back_button = QtGui.QPushButton(self.window)
		self.back_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/back.png")))
		self.back_button.clicked.connect(self.web.back)
		self.grid.addWidget(self.back_button, 0, 0)
		self.forward_button = QtGui.QPushButton(self.window)
		self.forward_button.setIcon(QtGui.QIcon(QtGui.QPixmap("GFX/forward.png")))
		self.forward_button.clicked.connect(self.web.forward)
		self.grid.addWidget(self.forward_button, 0, 1)
		
		self.web.show()
	
if __name__ == '__main__':
   app = App()
