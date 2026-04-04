"""
Dropbox integration for syncing bookmarks.

This module provides optional Dropbox integration for backing up
and syncing bookmarks across devices.

Note: Requires the 'dropbox' extra dependency:
    pip install open-browser[dropbox]
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTabWidget,
)

if TYPE_CHECKING:
    from dropbox import Dropbox
    from dropbox.files import WriteMode

logger = logging.getLogger(__name__)


class DropboxIntegration(QDialog):
    """
    Dialog for configuring Dropbox integration.
    
    Allows users to authenticate with Dropbox and sync bookmarks.
    """
    
    auth_completed = pyqtSignal()
    
    def __init__(self, parent=None) -> None:
        """Initialize the Dropbox integration dialog."""
        super().__init__(parent)
        self.setWindowTitle("Dropbox Integration")
        self.setMinimumSize(500, 400)
        
        self._auth_flow = None
        self._access_token: str | None = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "<h3>Dropbox Integration</h3>"
            "<p>Connect your Dropbox account to sync bookmarks across devices.</p>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Tab widget for auth flow
        self._tab_widget = QTabWidget(self)
        layout.addWidget(self._tab_widget)
        
        # Auth tab
        auth_widget = self._create_auth_widget()
        self._tab_widget.addTab(auth_widget, "Authentication")
        
        # Status tab
        status_widget = self._create_status_widget()
        self._tab_widget.addTab(status_widget, "Status")
        
        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    
    def _create_auth_widget(self) -> QDialog:
        """Create the authentication widget."""
        widget = QDialog(self)
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel(
            "<p>1. Click 'Authorize' to open Dropbox in a new tab<br>"
            "2. Log in and grant permission<br>"
            "3. Copy the authorization code<br>"
            "4. Paste it below and click 'Connect'</p>"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Code input
        code_layout = QHBoxLayout()
        code_label = QLabel("Authorization Code:")
        self._code_input = QLineEdit()
        self._code_input.setPlaceholderText("Paste code here...")
        code_layout.addWidget(code_label)
        code_layout.addWidget(self._code_input)
        layout.addLayout(code_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self._authorize_button = QPushButton("Open Dropbox", self)
        self._authorize_button.clicked.connect(self._start_auth)
        
        self._connect_button = QPushButton("Connect", self)
        self._connect_button.clicked.connect(self._finish_auth)
        
        button_layout.addWidget(self._authorize_button)
        button_layout.addWidget(self._connect_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _create_status_widget(self) -> QDialog:
        """Create the status widget."""
        widget = QDialog(self)
        layout = QVBoxLayout(widget)
        
        self._status_label = QLabel("Not connected to Dropbox")
        self._status_label.setStyleSheet("color: #d32f2f;")
        layout.addWidget(self._status_label)
        
        self._sync_button = QPushButton("Sync Now", self)
        self._sync_button.setEnabled(False)
        self._sync_button.clicked.connect(self._sync_bookmarks)
        layout.addWidget(self._sync_button)
        
        self._disconnect_button = QPushButton("Disconnect", self)
        self._disconnect_button.setEnabled(False)
        self._disconnect_button.clicked.connect(self._disconnect)
        layout.addWidget(self._disconnect_button)
        
        layout.addStretch()
        return widget
    
    def _start_auth(self) -> None:
        """Start the OAuth flow."""
        try:
            import dropbox
            from dropbox import DropboxOAuth2FlowNoRedirect
            
            # App credentials (should be stored securely in production)
            APP_KEY = "q6qqzbly9qycrot"
            APP_SECRET = "dmds9v8n328wzan"
            
            self._auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
            authorize_url = self._auth_flow.start()
            
            # Open in default browser
            import webbrowser
            webbrowser.open(authorize_url)
            
            logger.info("Opened Dropbox authorization URL")
            
        except ImportError:
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "Dropbox integration requires the 'dropbox' package.\n"
                "Install it with: pip install dropbox"
            )
        except Exception as e:
            logger.error(f"Failed to start auth flow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start auth: {e}")
    
    def _finish_auth(self) -> None:
        """Complete the OAuth flow."""
        if not self._auth_flow:
            QMessageBox.warning(
                self,
                "Error",
                "Please click 'Open Dropbox' first"
            )
            return
        
        code = self._code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Please enter the authorization code")
            return
        
        try:
            access_token, user_id = self._auth_flow.finish(code)
            self._access_token = access_token
            
            # Save token to config
            self._save_token(access_token)
            
            self._update_status(True)
            self.auth_completed.emit()
            
            QMessageBox.information(
                self,
                "Success",
                "Successfully connected to Dropbox!"
            )
            
            logger.info("Dropbox authentication completed")
            
        except Exception as e:
            logger.error(f"Auth failed: {e}")
            QMessageBox.critical(self, "Error", f"Authentication failed: {e}")
    
    def _save_token(self, token: str) -> None:
        """Save the access token to config."""
        from open_browser.storage import ConfigManager
        
        config_manager = ConfigManager()
        # Store in config (in production, use secure storage)
        config_manager.config.dropbox_token = token
        config_manager.save()
    
    def _load_token(self) -> str | None:
        """Load the access token from config."""
        from open_browser.storage import ConfigManager
        
        config_manager = ConfigManager()
        return getattr(config_manager.config, "dropbox_token", None)
    
    def _update_status(self, connected: bool) -> None:
        """Update the status display."""
        if connected:
            self._status_label.setText("Connected to Dropbox")
            self._status_label.setStyleSheet("color: #388e3c;")
            self._sync_button.setEnabled(True)
            self._disconnect_button.setEnabled(True)
        else:
            self._status_label.setText("Not connected to Dropbox")
            self._status_label.setStyleSheet("color: #d32f2f;")
            self._sync_button.setEnabled(False)
            self._disconnect_button.setEnabled(False)
    
    def _sync_bookmarks(self) -> None:
        """Sync bookmarks with Dropbox."""
        token = self._load_token()
        if not token:
            QMessageBox.warning(self, "Error", "Not connected to Dropbox")
            return
        
        try:
            import dropbox
            from dropbox.files import WriteMode
            
            dbx = dropbox.Dropbox(token)
            
            # Upload bookmarks file
            from open_browser.storage import BookmarksManager
            
            bookmarks_path = BookmarksManager()._storage.file_path
            
            with open(bookmarks_path, "rb") as f:
                dbx.files_upload(
                    f.read(),
                    "/Apps/Open Browser/bookmarks.json",
                    mode=WriteMode.overwrite
                )
            
            QMessageBox.information(
                self,
                "Success",
                "Bookmarks synced to Dropbox!"
            )
            
            logger.info("Bookmarks synced to Dropbox")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            QMessageBox.critical(self, "Error", f"Sync failed: {e}")
    
    def _disconnect(self) -> None:
        """Disconnect from Dropbox."""
        self._access_token = None
        self._save_token("")
        self._update_status(False)
        logger.info("Disconnected from Dropbox")


def is_dropbox_available() -> bool:
    """Check if Dropbox integration is available."""
    try:
        import dropbox
        return True
    except ImportError:
        return False
