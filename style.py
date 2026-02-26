STYLE_SHEET = """
QMainWindow {
    background-color: #F8FAFC;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #334155;
}

QFrame#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
    min-width: 200px;
}

QPushButton {
    padding: 10px 15px;
    border-radius: 8px;
    font-weight: 500;
}

QPushButton#SidebarButton {
    background-color: transparent;
    text-align: left;
    border: none;
    color: #64748B;
    margin: 5px 10px;
}

QPushButton#SidebarButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton#SidebarButton[active="true"] {
    background-color: #EEF2FF;
    color: #4F46E5;
}

QPushButton#PrimaryButton {
    background-color: #4F46E5;
    color: white;
    border: none;
}

QPushButton#PrimaryButton:hover {
    background-color: #4338CA;
}

QPushButton#SecondaryButton {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #E2E8F0;
}

QPushButton#SecondaryButton:hover {
    background-color: #F8FAFC;
}

QLineEdit, QComboBox, QTextEdit {
    padding: 8px 12px;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    background-color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #4F46E5;
}

QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
}

QHeaderView::section {
    background-color: #F8FAFC;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: bold;
    color: #475569;
}

QLabel#Title {
    font-size: 24px;
    font-weight: bold;
    color: #1E293B;
    padding: 10px;
}

QLabel#SubTitle {
    font-size: 14px;
    color: #64748B;
    padding: 2px 10px;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 15px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
"""
