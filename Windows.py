from qgis.PyQt.QtWidgets import  QStackedWidget, QFileDialog, QMainWindow, QHBoxLayout, QComboBox, QVBoxLayout, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QDialog, QSizePolicy
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt, QDate



from .EquiView360 import GLWidget


import json
import os

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["PostGIS", "Geopackage"])
        self.stacked_widget = QStackedWidget()
        self.postgis_widget = QWidget()
        label_host = QLabel("Host:")
        self.lineEdit_host = QLineEdit()
        label_port = QLabel("Port:")
        self.lineEdit_port = QLineEdit()
        label_database = QLabel("Database:")
        self.lineEdit_database = QLineEdit()
        label_username = QLabel("Username:")
        self.lineEdit_username = QLineEdit()
        label_password = QLabel("Password:")
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        label_schema = QLabel("Schema:")
        self.lineEdit_schema = QLineEdit()
        label_table = QLabel("Table:")
        self.lineEdit_table = QLineEdit()
        postgis_grid = QGridLayout()
        postgis_grid.addWidget(label_host, 0, 0)
        postgis_grid.addWidget(self.lineEdit_host, 0, 1)
        postgis_grid.addWidget(label_port, 1, 0)
        postgis_grid.addWidget(self.lineEdit_port, 1, 1)
        postgis_grid.addWidget(label_database, 2, 0)
        postgis_grid.addWidget(self.lineEdit_database, 2, 1)
        postgis_grid.addWidget(label_username, 3, 0)
        postgis_grid.addWidget(self.lineEdit_username, 3, 1)
        postgis_grid.addWidget(label_password, 4, 0)
        postgis_grid.addWidget(self.lineEdit_password, 4, 1)
        postgis_grid.addWidget(label_schema, 5, 0)
        postgis_grid.addWidget(self.lineEdit_schema, 5, 1)
        postgis_grid.addWidget(label_table, 6, 0)
        postgis_grid.addWidget(self.lineEdit_table, 6, 1)
        self.postgis_widget.setLayout(postgis_grid)
        self.geopackage_widget = QWidget()
        label_file = QLabel("Geopackage file:")
        self.lineEdit_file = QLineEdit()
        button_browse = QPushButton("Browse")
        geopackage_grid = QGridLayout()
        geopackage_grid.addWidget(label_file, 0, 0)
        geopackage_grid.addWidget(self.lineEdit_file, 0, 1)
        geopackage_grid.addWidget(button_browse, 0, 2)
        self.geopackage_widget.setLayout(geopackage_grid)
        self.stacked_widget.addWidget(self.postgis_widget)
        self.stacked_widget.addWidget(self.geopackage_widget)
        self.combo_box.currentIndexChanged.connect(self.stacked_widget.setCurrentIndex)
        button_connect = QPushButton("Connect")
        button_cancel = QPushButton("Cancel")
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_connect)
        button_layout.addWidget(button_cancel)
        grid = QGridLayout()
        grid.addWidget(self.combo_box, 0, 0, 1, 2)
        grid.addWidget(self.stacked_widget, 1, 0, 1, 2)
        grid.addLayout(button_layout, 2, 0, 1, 2)
        self.setLayout(grid)
        self.setFixedWidth(400)
        self.setWindowIcon(QIcon(':/plugins/GLViewer/icon.png'))
        self.setWindowTitle("Connection")
        button_connect.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
        button_connect.clicked.connect(self.save_connection)
        button_browse.clicked.connect(self.browse_file)
        try:
            with open("connection_params.json", "r") as f:
                connection_params = json.load(f)
                self.lineEdit_host.setText(connection_params["host"])
                self.lineEdit_port.setText(connection_params["port"])
                self.lineEdit_database.setText(connection_params["database"])
                self.lineEdit_username.setText(connection_params["username"])
                self.lineEdit_schema.setText(connection_params["schema"])
                self.lineEdit_table.setText(connection_params["table"])
                self.lineEdit_file.setText(connection_params["file"])
                self.lineEdit_password.setText(connection_params["password"])
        except FileNotFoundError :
            pass
        except KeyError:
            pass

    def get_connection(self):
        index = self.stacked_widget.currentIndex()
        if index == 0:
            host = self.lineEdit_host.text()
            port = self.lineEdit_port.text()
            database = self.lineEdit_database.text()
            username = self.lineEdit_username.text()
            schema = self.lineEdit_schema.text()
            table = self.lineEdit_table.text()
            password = self.lineEdit_password.text()
            return host, port, database, username, password, schema, table
        elif index == 1:
            file = self.lineEdit_file.text()
            return file

    def save_connection(self):
        index = self.stacked_widget.currentIndex()
        if index == 0:
            host = self.lineEdit_host.text()
            port = self.lineEdit_port.text()
            database = self.lineEdit_database.text()
            username = self.lineEdit_username.text()
            schema = self.lineEdit_schema.text()
            table = self.lineEdit_table.text()
            connection_params = {
                "host": host,
                "port": port,
                "database": database,
                "username": username,
                "schema": schema,
                "table": table,
            }
        elif index == 1:
            file = self.lineEdit_file.text()
            connection_params = {"file": file}
        if os.path.exists("connection_params.json"):
            with open("connection_params.json", "r") as f:
                existing_params = json.load(f)
            existing_params.update(connection_params)
            with open("connection_params.json", "w") as f:
                json.dump(existing_params, f)
        else:
            with open("connection_params.json", "w") as f:
                json.dump(connection_params, f)

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getOpenFileName(self, "Select Geopackage file", "", "Geopackage (*.gpkg);;All Files (*)", options=options)
        if file:
            self.lineEdit_file.setText(file)

class MainWindow(QMainWindow):
    def __init__(self, iface, url, map_manager, direction, angle_degrees, date, x, y, params, gpkg):
        super().__init__()
        self.map_manager = map_manager
        horizontalLayout = QHBoxLayout()
        comboBox1 = QComboBox()
        if date is not None :
            if type(date) == QDate:
                date = date.toString()
            comboBox1.addItem(date)
        date_label = QLabel('Date')
        comboBox1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        horizontalLayout.setStretchFactor(date_label, 0)
        horizontalLayout.addWidget(date_label)
        horizontalLayout.addWidget(comboBox1)
        verticalLayout = QVBoxLayout()
        self.gl_widget = GLWidget(self, iface, url, direction, map_manager, angle_degrees, x, y, params, gpkg)
        self.gl_widget.setCursor(Qt.OpenHandCursor)
        self.gl_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        verticalLayout.addWidget(self.gl_widget)
        verticalLayout.setStretchFactor(self.gl_widget, 1)
        verticalLayout.addLayout(horizontalLayout)
        centralWidget = QWidget()
        centralWidget.setLayout(verticalLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle("Equirectangular 360° Viewer")
        self.setWindowIcon(QIcon(':/plugins/GLViewer/icon.png'))
        self.resize(1080,720)
    def closeEvent(self, event):
        self.map_manager.remove_all_points_from_map()
        super().closeEvent(event)

class ColumnSelectionDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.geom_label = QLabel("Geometry column:")
        self.geom_combo = QComboBox()
        self.yaw_label = QLabel("Direction column:")
        self.yaw_combo = QComboBox()
        self.link_label = QLabel("Link column:")
        self.link_combo = QComboBox()
        self.date_label = QLabel("Date column:")
        self.date_combo = QComboBox()
        self.geom_combo.addItems(columns)
        self.yaw_combo.addItems(columns)
        self.link_combo.addItems(columns)
        self.date_combo.addItems(columns)
        try :
            with open("connection_params.json", "r") as f:
                connection_params = json.load(f)
                default_geom = connection_params["geom"]
                default_yaw = connection_params["yaw"]
                default_link = connection_params["link"]
                default_date = connection_params["date"]
                default_geom_index = self.date_combo.findText(default_geom)
                self.geom_combo.setCurrentIndex(default_geom_index)
                default_yaw_index = self.yaw_combo.findText(default_yaw)
                self.yaw_combo.setCurrentIndex(default_yaw_index)
                default_link_index = self.link_combo.findText(default_link)
                self.link_combo.setCurrentIndex(default_link_index)
                default_date_index = self.date_combo.findText(default_date)
                self.date_combo.setCurrentIndex(default_date_index)
        except Exception :
            pass
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.clicked.connect(self.save_data)
        layout = QVBoxLayout()
        layout.addWidget(self.geom_label)
        layout.addWidget(self.geom_combo)
        layout.addWidget(self.yaw_label)
        layout.addWidget(self.yaw_combo)
        layout.addWidget(self.link_label)
        layout.addWidget(self.link_combo)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_combo)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)
        self.setFixedWidth(400)
        self.setWindowIcon(QIcon(':/plugins/GLViewer/icon.png'))
        self.setWindowTitle("Data selection")

    def save_data(self):
        geom = self.geom_combo.currentText()
        yaw = self.yaw_combo.currentText()
        link = self.link_combo.currentText()
        date = self.date_combo.currentText()
        connection_params = {
            "geom": geom,
            "yaw": yaw,
            "link": link,
            "date": date,
        }
        with open("connection_params.json", "r") as f:
            connection_params = json.load(f)
            connection_params["geom"] = geom
            connection_params["yaw"] = yaw
            connection_params["link"] = link
            connection_params["date"] = date
        with open("connection_params.json", "w") as f:
            json.dump(connection_params, f)

    def get_columns(self):
        geom = self.geom_combo.currentText()
        yaw = self.yaw_combo.currentText()
        link = self.link_combo.currentText()
        date = self.date_combo.currentText()
        return geom, yaw, link, date