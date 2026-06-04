"""Sample Comparison Tab"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import pandas as pd

from ..theme import Theme


class ComparisonTab:
    """Tab for comparing multiple samples"""
    
    def setup(self, parent, db):
        self.parent = parent
        self.db = db
        
        layout = QVBoxLayout(parent)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("Sample Comparison")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        layout.addWidget(title)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search samples...")
        self.search_box.textChanged.connect(self._filter_table)
        toolbar.addWidget(self.search_box, 1)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._load_table)
        toolbar.addWidget(refresh_btn)
        
        export_btn = QPushButton("📊 Export Excel")
        export_btn.setStyleSheet(f"background-color: {Theme.SECONDARY}; color: white;")
        export_btn.clicked.connect(self._export_table)
        toolbar.addWidget(export_btn)
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Sample Name", "Type", "Date", 
            "Ecorr (V)", "Icorr (μA/cm²)", "CR (mm/yr)", 
            "βa (mV/dec)", "βc (mV/dec)"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.verticalHeader().setDefaultSectionSize(40)
        layout.addWidget(self.table, 1)
        
        self._load_table()
    
    def _load_table(self):
        try:
            self.all_samples = self.db.get_all()
            self._filter_table()
        except Exception as e:
            print(f"Error loading table: {e}")
    
    def _filter_table(self):
        if not hasattr(self, 'all_samples'):
            return
        
        search = self.search_box.text().lower()
        filtered = [s for s in self.all_samples if search in (s[1] or '').lower()]
        
        self.table.setRowCount(len(filtered))
        
        for i, row in enumerate(filtered):
            data = [
                row[1] or "—",
                row[2] or "—",
                row[3] or "—",
                f"{row[5]:.4f}" if row[5] is not None else "—",
                f"{row[6]:.2f}" if row[6] is not None else "—",
                f"{row[7]:.4f}" if row[7] is not None else "—",
                f"{row[8]:.1f}" if row[8] is not None else "—",
                f"{row[9]:.1f}" if row[9] is not None else "—"
            ]
            
            for j, text in enumerate(data):
                item = QTableWidgetItem(text)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Color code CR column
                if j == 5 and row[7] is not None:
                    cr_val = float(row[7])
                    if cr_val > 1:
                        item.setBackground(QColor("#FEE2E2"))
                        item.setForeground(QColor("#991B1B"))
                    elif cr_val > 0.5:
                        item.setBackground(QColor("#FEF3C7"))
                        item.setForeground(QColor("#92400E"))
                    else:
                        item.setBackground(QColor("#D1FAE5"))
                        item.setForeground(QColor("#065F46"))
                
                self.table.setItem(i, j, item)
        
        self.table.resizeColumnsToContents()
    
    def _export_table(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self.parent, "No Data", "Nothing to export")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self.parent, "Export", "corrosion_data.xlsx", "Excel (*.xlsx)"
        )
        
        if path:
            try:
                data = []
                for r in range(self.table.rowCount()):
                    row_data = {}
                    for c in range(self.table.columnCount()):
                        header = self.table.horizontalHeaderItem(c).text()
                        item = self.table.item(r, c)
                        row_data[header] = item.text() if item else ""
                    data.append(row_data)
                
                pd.DataFrame(data).to_excel(path, index=False)
                QMessageBox.information(self.parent, "Success", f"Exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self.parent, "Error", str(e))