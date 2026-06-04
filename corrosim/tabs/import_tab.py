"""Data Import Tab"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import pandas as pd
import datetime
import numpy as np
from io import StringIO


class ImportTab:
    """Tab for importing and previewing data files"""
    
    def setup(self, parent, db, switch_tab_callback, load_tafel_callback):
        self.parent = parent
        self.db = db
        self.switch_tab = switch_tab_callback
        self.load_tafel_data = load_tafel_callback
        self.current_data = None
        self.current_id = None
        
        # Main layout
        layout = QVBoxLayout(parent)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        title = QLabel("Data Import")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title)
        
        # File Selection
        file_card = QGroupBox("Select Data File")
        fl = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Choose an Excel or CSV file...")
        fl.addWidget(self.file_path, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_file)
        fl.addWidget(browse_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_import)
        fl.addWidget(clear_btn)
        file_card.setLayout(fl)
        layout.addWidget(file_card)
        
        # Content area
        content = QHBoxLayout()
        content.setSpacing(12)
        
        # Preview section
        prev_card = QGroupBox("Data Preview")
        pv = QVBoxLayout()
        
        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("🔍 Load Preview")
        self.preview_btn.clicked.connect(self._load_preview)
        btn_row.addWidget(self.preview_btn)
        btn_row.addStretch()
        self.preview_info = QLabel("")
        self.preview_info.setStyleSheet("color: #10B981; font-weight: 600; font-size: 11px;")
        btn_row.addWidget(self.preview_info)
        pv.addLayout(btn_row)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        scroll.setWidget(self.preview_table)
        pv.addWidget(scroll, 1)
        prev_card.setLayout(pv)
        content.addWidget(prev_card, 2)
        
        # Sample info section
        right = QVBoxLayout()
        right.setSpacing(12)
        
        sample_card = QGroupBox("Sample Information")
        sf = QFormLayout()
        sf.setSpacing(8)
        
        self.sample_name = QLineEdit()
        self.sample_name.setPlaceholderText("e.g., Steel Sample A1")
        sf.addRow("Sample Name:", self.sample_name)
        
        self.test_type = QComboBox()
        self.test_type.addItems(["Potentiodynamic Polarization", "EIS", "Linear Polarization"])
        sf.addRow("Test Type:", self.test_type)
        
        self.import_unit = QComboBox()
        self.import_unit.addItems(["Auto-detect", "Amperes (A)", "milliamperes (mA)", "microamperes (μA)"])
        sf.addRow("Current Unit:", self.import_unit)
        
        sample_card.setLayout(sf)
        right.addWidget(sample_card)
        
        # Stats card
        stats_card = QGroupBox("Quick Stats")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("No data loaded")
        self.stats_label.setStyleSheet("color: #64748B; padding: 12px; font-size: 11px;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        stats_card.setLayout(stats_layout)
        right.addWidget(stats_card)
        
        right.addStretch()
        content.addLayout(right, 1)
        
        layout.addLayout(content, 1)
        
        # Import button
        self.import_btn = QPushButton("📥 Import to Database")
        self.import_btn.setObjectName("primaryBtn")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._import_data)
        layout.addWidget(self.import_btn)
    
    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self.parent, "Select Data File", "",
            "Data Files (*.xlsx *.xls *.csv);;All Files (*)"
        )
        if path:
            self.file_path.setText(path)
    
    def _clear_import(self):
        self.file_path.clear()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.current_data = None
        self.preview_info.setText("")
        self.stats_label.setText("No data loaded")
        self.sample_name.clear()
        self.import_btn.setEnabled(False)
    
    def _load_preview(self):
        path = self.file_path.text()
        if not path:
            QMessageBox.warning(self.parent, "No File", "Please select a file first.")
            return
        
        try:
            if path.endswith(('.xlsx', '.xls')):
                self.current_data = pd.read_excel(path)
            else:
                self.current_data = pd.read_csv(path)
            
            # Clean column names
            self.current_data.columns = [
                str(c).strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
                for c in self.current_data.columns
            ]
            
            rows, cols = len(self.current_data), len(self.current_data.columns)
            
            # Show preview
            preview = self.current_data.head(100)
            self.preview_table.setColumnCount(cols)
            self.preview_table.setRowCount(len(preview))
            self.preview_table.setHorizontalHeaderLabels([str(c) for c in preview.columns])
            
            for i, row in preview.iterrows():
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.preview_table.setItem(i, j, item)
            
            self.preview_table.resizeColumnsToContents()
            
            # Update info
            self.preview_info.setText(f"✓ {rows} rows × {cols} columns")
            
            # Stats
            num_cols = self.current_data.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                stats_text = f"Numerical Columns: {len(num_cols)}\n"
                stats_text += f"Total Rows: {rows}\n"
                stats_text += f"Missing Values: {self.current_data.isnull().sum().sum()}"
                self.stats_label.setText(stats_text)
            
            self.import_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to load file:\n{str(e)}")
    
    def _import_data(self):
        if self.current_data is None:
            return
        
        name = self.sample_name.text().strip()
        if not name:
            name = f"Sample_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            sid = self.db.save(name, self.test_type.currentText(), self.current_data)
            self.current_id = sid
            
            QMessageBox.information(
                self.parent, "✓ Import Successful",
                f"Sample imported successfully!\n\n"
                f"ID: {sid}\nName: {name}\n"
                f"Type: {self.test_type.currentText()}\n"
                f"Records: {len(self.current_data)}"
            )
            
            self._clear_import()
            
            reply = QMessageBox.question(
                self.parent, "Continue",
                "Go to Tafel Analysis?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.switch_tab(1)
                self.load_tafel_data()
                
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Import failed:\n{str(e)}")