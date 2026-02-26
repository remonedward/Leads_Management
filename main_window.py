import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QFileDialog,
                             QMessageBox, QFrame, QHeaderView, QLineEdit, QDialog,
                             QFormLayout, QTextEdit, QInputDialog, QComboBox, QGroupBox,
                             QMenu, QAction, QDateEdit)
from PyQt5.QtCore import Qt, pyqtSlot, QDate
from db_manager import DatabaseManager
from style import STYLE_SHEET

class AddLeadDialog(QDialog):
    def __init__(self, parent=None, columns=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Lead")
        self.layout = QFormLayout(self)
        self.inputs = {}
        self.columns = columns or []

        if not self.columns:
            self.columns = ["full_name", "phone_number", "email"]

        for col in self.columns:
            if col in ['id', 'import_date', 'source_file', 'external_id']:
                continue
            le = QLineEdit()
            self.layout.addRow(QLabel(f"{col}:"), le)
            self.inputs[col] = le

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self.accept)
        self.layout.addRow(self.save_btn)

    def get_data(self):
        return {col: le.text() for col, le in self.inputs.items()}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("Auto Leads - Automation System by >>REMO_OX<<")
        self.resize(1300, 800)
        self.setStyleSheet(STYLE_SHEET)

        self.selected_lead_id = None
        self.init_ui()
        self.load_leads()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        title_label = QLabel("Auto Leads")
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title_label)

        self.btn_dashboard = self.create_sidebar_btn("Dashboard", 0)
        self.btn_leads = self.create_sidebar_btn("Leads List", 1)
        self.btn_db_explorer = self.create_sidebar_btn("Data Explorer", 2)
        self.btn_reports = self.create_sidebar_btn("Reports", 3)

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_leads)
        sidebar_layout.addWidget(self.btn_db_explorer)
        sidebar_layout.addWidget(self.btn_reports)
        sidebar_layout.addStretch()

        self.btn_exit = QPushButton("Exit App")
        self.btn_exit.setObjectName("SidebarButton")
        self.btn_exit.setStyleSheet("color: #EF4444;")
        self.btn_exit.clicked.connect(self.close)
        sidebar_layout.addWidget(self.btn_exit)

        layout.addWidget(self.sidebar)

        # Content Area
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.init_dashboard_view()
        self.init_leads_view()
        self.init_db_explorer_view()
        self.init_reports_view()

        self.switch_view(0)

    def create_sidebar_btn(self, text, index):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.clicked.connect(lambda: self.switch_view(index))
        return btn

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)
        buttons = [self.btn_dashboard, self.btn_leads, self.btn_db_explorer, self.btn_reports]
        for i, btn in enumerate(buttons):
            btn.setProperty("active", i == index)
            btn.setStyle(btn.style())

        if index == 1:
            self.load_leads()
        elif index == 2:
            self.refresh_table_list()

    def init_dashboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(QLabel("Dashboard", objectName="Title"))
        layout.addWidget(QLabel("Overview of your leads and database status", objectName="SubTitle"))

        stats_layout = QHBoxLayout()
        self.leads_count_card = self.create_stat_card("Total Leads", "0")
        stats_layout.addWidget(self.leads_count_card)
        layout.addLayout(stats_layout)

        tip_box = QGroupBox("Action Shortcut")
        tip_layout = QVBoxLayout(tip_box)
        tip_layout.addWidget(QLabel("1. Go to 'Leads List' to manage leads."))
        tip_layout.addWidget(QLabel("2. Select a lead and use the side panel to add interactions."))
        tip_layout.addWidget(QLabel("3. Edit any field directly in the table. Changes save automatically."))
        tip_layout.addWidget(QLabel("4. Right-click any cell for more options."))
        layout.addWidget(tip_box)

        layout.addStretch()
        self.stack.addWidget(view)

    def create_stat_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 25px;")
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        t_label = QLabel(title)
        t_label.setStyleSheet("color: #64748B; font-size: 16px;")
        layout.addWidget(t_label)
        v_label = QLabel(value)
        v_label.setStyleSheet("color: #1E293B; font-size: 36px; font-weight: bold;")
        v_label.setObjectName("StatValue")
        layout.addWidget(v_label)
        return card

    def init_leads_view(self):
        view = QWidget()
        main_layout = QHBoxLayout(view)
        main_layout.setContentsMargins(30, 30, 30, 30)

        left_layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("Leads Management", objectName="Title"))
        header.addStretch()

        btn_import = QPushButton("Import CSV")
        btn_import.setObjectName("PrimaryButton")
        btn_import.clicked.connect(self.import_csv)
        header.addWidget(btn_import)

        btn_add = QPushButton("Manual Entry")
        btn_add.setObjectName("SecondaryButton")
        btn_add.clicked.connect(self.add_manual_lead)
        header.addWidget(btn_add)

        left_layout.addLayout(header)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search leads by any field...")
        self.search_input.textChanged.connect(self.filter_leads)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)

        self.leads_table = QTableWidget()
        self.leads_table.setAlternatingRowColors(True)
        self.leads_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leads_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.leads_table.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.leads_table, "leads"))
        self.leads_table.itemSelectionChanged.connect(self.on_lead_selection_changed)
        self.leads_table.itemChanged.connect(lambda item: self.on_generic_item_changed(item, "leads"))
        left_layout.addWidget(self.leads_table)

        main_layout.addLayout(left_layout, 7)

        # Interaction Side Panel
        right_panel = QFrame()
        right_panel.setFixedWidth(300)
        # Target only the frame to avoid child inheritance issues
        right_panel.setStyleSheet("QFrame { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; }")
        rp_layout = QVBoxLayout(right_panel)

        rp_layout.addWidget(QLabel("Add Interaction", styleSheet="font-size: 18px; font-weight: bold; margin-bottom: 10px;"))
        self.selected_lead_label = QLabel("No lead selected")
        self.selected_lead_label.setWordWrap(True)
        self.selected_lead_label.setStyleSheet("color: #64748B; margin-bottom: 20px;")
        rp_layout.addWidget(self.selected_lead_label)

        self.interaction_result = QLineEdit()
        self.interaction_result.setPlaceholderText("Result (e.g., Called, Interested)")
        rp_layout.addWidget(QLabel("Result:"))
        rp_layout.addWidget(self.interaction_result)

        self.interaction_notes = QTextEdit()
        self.interaction_notes.setPlaceholderText("Notes...")
        rp_layout.addWidget(QLabel("Notes:"))
        rp_layout.addWidget(self.interaction_notes)

        self.btn_save_interaction = QPushButton("Save Interaction")
        self.btn_save_interaction.setObjectName("PrimaryButton")
        self.btn_save_interaction.clicked.connect(self.save_interaction)
        rp_layout.addWidget(self.btn_save_interaction)

        rp_layout.addStretch()
        main_layout.addWidget(right_panel, 3)

        self.stack.addWidget(view)

    def init_reports_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(40, 40, 40, 40)

        layout.addWidget(QLabel("Interaction Reports", objectName="Title"))
        layout.addWidget(QLabel("Export interactions with lead details based on date range", objectName="SubTitle"))

        filter_box = QGroupBox("Filter and Preview")
        filter_layout = QHBoxLayout(filter_box)

        filter_layout.addWidget(QLabel("From:"))
        self.date_start = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_start.setCalendarPopup(True)
        self.date_start.dateChanged.connect(self.load_report_preview)
        filter_layout.addWidget(self.date_start)

        filter_layout.addWidget(QLabel("To:"))
        self.date_end = QDateEdit(QDate.currentDate())
        self.date_end.setCalendarPopup(True)
        self.date_end.dateChanged.connect(self.load_report_preview)
        filter_layout.addWidget(self.date_end)

        btn_refresh = QPushButton("Show Report")
        btn_refresh.setObjectName("SecondaryButton")
        btn_refresh.clicked.connect(self.load_report_preview)
        filter_layout.addWidget(btn_refresh)

        btn_export = QPushButton("Export to Excel")
        btn_export.setObjectName("PrimaryButton")
        btn_export.clicked.connect(self.export_report_to_excel)
        filter_layout.addWidget(btn_export)

        layout.addWidget(filter_box)

        self.report_preview_table = QTableWidget()
        self.report_preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.report_preview_table)

        layout.addStretch()
        self.stack.addWidget(view)

    def load_report_preview(self):
        start = self.date_start.date().toString("yyyy-MM-dd")
        end = self.date_end.date().toString("yyyy-MM-dd")

        data = self.db.get_interaction_report(start, end)
        if not data:
            self.report_preview_table.setColumnCount(0)
            self.report_preview_table.setRowCount(0)
            return

        columns = list(data[0].keys())
        self.report_preview_table.setColumnCount(len(columns))
        self.report_preview_table.setHorizontalHeaderLabels(columns)
        self.report_preview_table.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                val = str(row[col_name]) if row[col_name] is not None else ""
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.report_preview_table.setItem(row_idx, col_idx, item)

    def export_report_to_excel(self):
        start = self.date_start.date().toString("yyyy-MM-dd")
        end = self.date_end.date().toString("yyyy-MM-dd")

        try:
            report_data = self.db.get_interaction_report(start, end)
            if not report_data:
                QMessageBox.information(self, "No Data", "No interactions found in the selected date range.")
                return

            df = pd.DataFrame(report_data)

            # Clean up duplicate columns from JOIN if any (e.g. 'id' from both tables)
            # We'll rename them for clarity
            # Note: Pandas might have 'id' and 'id_1' if they conflict

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"Interactions_Report_{start}_to_{end}.xlsx", "Excel Files (*.xlsx)")

            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Export Success", f"Report saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export:\n{str(e)}")

    def init_db_explorer_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QHBoxLayout()
        header.addWidget(QLabel("Database Explorer", objectName="Title"))
        header.addStretch()

        btn_add_col = QPushButton("Add New Field")
        btn_add_col.setObjectName("SecondaryButton")
        btn_add_col.clicked.connect(self.add_new_column_explorer)
        header.addWidget(btn_add_col)

        layout.addLayout(header)

        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Table:"))
        self.table_combo = QComboBox()
        self.table_combo.currentTextChanged.connect(self.load_table_data)
        selection_layout.addWidget(self.table_combo)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        self.db_explorer_table = QTableWidget()
        self.db_explorer_table.setAlternatingRowColors(True)
        self.db_explorer_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.db_explorer_table.customContextMenuRequested.connect(lambda pos: self.show_context_menu(pos, self.db_explorer_table, self.table_combo.currentText()))
        self.db_explorer_table.itemChanged.connect(lambda item: self.on_generic_item_changed(item, self.table_combo.currentText()))
        layout.addWidget(self.db_explorer_table)

        self.stack.addWidget(view)

    def on_lead_selection_changed(self):
        selected_items = self.leads_table.selectedItems()
        if not selected_items:
            self.selected_lead_id = None
            self.selected_lead_label.setText("No lead selected")
            return

        row = selected_items[0].row()
        self.selected_lead_id = self.leads_table.item(row, 0).text()

        name = "Unknown"
        for col in ["full_name", "full name", "name"]:
            for c_idx in range(self.leads_table.columnCount()):
                if self.leads_table.horizontalHeaderItem(c_idx).text().lower() == col:
                    name = self.leads_table.item(row, c_idx).text()
                    break

        self.selected_lead_label.setText(f"Selected Lead: {name} (ID: {self.selected_lead_id})")

    def save_interaction(self):
        if not self.selected_lead_id:
            QMessageBox.warning(self, "No Selection", "Please select a lead first.")
            return

        result = self.interaction_result.text()
        notes = self.interaction_notes.toPlainText()

        if not result:
            QMessageBox.warning(self, "Missing Data", "Please enter at least a result.")
            return

        try:
            self.db.add_interaction(int(self.selected_lead_id), {"result": result, "notes": notes})
            QMessageBox.information(self, "Saved", "Interaction saved successfully.")
            self.interaction_result.clear()
            self.interaction_notes.clear()
            if self.table_combo.currentText() == "interactions":
                self.load_table_data("interactions")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save: {e}")

    def show_context_menu(self, pos, table, table_name):
        item = table.itemAt(pos)
        if not item: return

        menu = QMenu()
        clear_action = QAction("Clear Field", self)
        clear_action.triggered.connect(lambda: self.clear_cell(item, table_name))

        delete_row_action = QAction("Delete Row", self)
        delete_row_action.triggered.connect(lambda: self.delete_row(item.row(), table, table_name))

        menu.addAction(clear_action)
        menu.addSeparator()
        menu.addAction(delete_row_action)
        menu.exec_(table.viewport().mapToGlobal(pos))

    def clear_cell(self, item, table_name):
        item.setText("") # This will trigger itemChanged and sync to DB

    def delete_row(self, row, table, table_name):
        record_id = table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete record {record_id} from {table_name}?")
        if confirm == QMessageBox.Yes:
            if self.db.delete_record(table_name, int(record_id)):
                if table_name == "leads":
                    self.load_leads()
                else:
                    self.load_table_data(table_name)

    def on_generic_item_changed(self, item, table_name):
        if not table_name: return
        row = item.row()
        col = item.column()
        col_name = item.tableWidget().horizontalHeaderItem(col).text()

        if col == 0: return # Don't update ID

        record_id_item = item.tableWidget().item(row, 0)
        if not record_id_item: return

        record_id = record_id_item.text()
        new_value = item.text()

        try:
            self.db.update_record(table_name, int(record_id), col_name, new_value)
        except Exception as e:
            print(f"Generic Update failed: {e}")

    def refresh_table_list(self):
        tables = self.db.get_table_names()
        self.table_combo.blockSignals(True)
        self.table_combo.clear()
        self.table_combo.addItems(tables)
        self.table_combo.blockSignals(False)
        self.load_table_data(self.table_combo.currentText())

    def load_table_data(self, table_name):
        if not table_name: return
        self.db_explorer_table.blockSignals(True)

        # Special case: for interactions, show lead details too for better usability
        if table_name.lower() == "interactions":
            data = self.db.get_interaction_report() # No date filter = all
        else:
            data = self.db.get_table_data(table_name)

        if not data:
            self.db_explorer_table.setColumnCount(0)
            self.db_explorer_table.setRowCount(0)
            self.db_explorer_table.blockSignals(False)
            return

        columns = list(data[0].keys())
        self.db_explorer_table.setColumnCount(len(columns))
        self.db_explorer_table.setHorizontalHeaderLabels(columns)
        self.db_explorer_table.setRowCount(len(data))

        for row_idx, row in enumerate(data):
            for col_idx, col_name in enumerate(columns):
                item = QTableWidgetItem(str(row[col_name]) if row[col_name] is not None else "")
                # ID and lead_id columns should be non-editable in explorer for safety
                if col_name.lower() in ['id', 'lead_id']:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.db_explorer_table.setItem(row_idx, col_idx, item)
        self.db_explorer_table.blockSignals(False)

    def add_new_column_explorer(self):
        table = self.table_combo.currentText()
        if not table: return
        col_name, ok = QInputDialog.getText(self, "Add Custom Field", f"Field Name for {table}:")
        if ok and col_name:
            if self.db.add_column(table, col_name):
                QMessageBox.information(self, "Success", f"Field '{col_name}' added to {table}.")
                if table == "leads": self.load_leads()
                self.load_table_data(table)

    def load_leads(self, search_term=None):
        self.leads_table.blockSignals(True)
        if search_term is None and hasattr(self, 'search_input'):
            search_term = self.search_input.text()

        leads = self.db.fetch_all_leads(search_term)

        stat_val = self.leads_count_card.findChild(QLabel, "StatValue")
        if stat_val: stat_val.setText(str(len(leads)))

        if not leads:
            self.leads_table.setColumnCount(0)
            self.leads_table.setRowCount(0)
            self.leads_table.blockSignals(False)
            return

        columns = list(leads[0].keys())
        self.leads_table.setColumnCount(len(columns))
        self.leads_table.setHorizontalHeaderLabels(columns)
        self.leads_table.setRowCount(len(leads))

        for row_idx, lead in enumerate(leads):
            for col_idx, col_name in enumerate(columns):
                val = str(lead[col_name]) if lead[col_name] is not None else ""
                item = QTableWidgetItem(val)
                if col_name.lower() in ['id', 'import_date', 'source_file', 'external_id']:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.leads_table.setItem(row_idx, col_idx, item)
        self.leads_table.blockSignals(False)

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not file_path: return
        try:
            df = pd.read_csv(file_path).fillna('')
            for _, row in df.iterrows():
                data = row.to_dict()
                data['source_file'] = file_path.split('/')[-1]
                self.db.insert_lead(data)
            QMessageBox.information(self, "Import Success", "Leads imported successfully.")
            self.load_leads()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def add_manual_lead(self):
        leads = self.db.fetch_all_leads()
        columns = list(leads[0].keys()) if leads else []
        dialog = AddLeadDialog(self, columns)
        if dialog.exec_():
            data = dialog.get_data()
            data['source_file'] = 'Manual Entry'
            self.db.insert_lead(data)
            self.load_leads()

    def filter_leads(self, text):
        self.load_leads(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
