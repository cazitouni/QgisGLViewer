import json
import os

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .EquiView360 import GLWidget


class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Geopackage", "Panoramax", "PostGIS"])
        self.stacked_widget = QStackedWidget()
        self.postgis_widget = QWidget()
        self.panoramax_widget = QWidget()
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
        self.stacked_widget.addWidget(self.geopackage_widget)
        self.stacked_widget.addWidget(self.panoramax_widget)
        self.stacked_widget.addWidget(self.postgis_widget)
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
        self.setWindowIcon(QIcon(":/plugins/GLViewer/icon.png"))
        self.setWindowTitle("Connection")
        button_connect.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
        button_connect.clicked.connect(self.save_connection)
        button_browse.clicked.connect(self.browse_file)
        try:
            filename = os.path.join(
                QgsApplication.qgisSettingsDirPath(), "connection_params.json"
            )
            with open(filename) as f:
                connection_params = json.load(f)
                self.lineEdit_host.setText(connection_params["host"])
                self.lineEdit_port.setText(connection_params["port"])
                self.lineEdit_database.setText(connection_params["database"])
                self.lineEdit_username.setText(connection_params["username"])
                self.lineEdit_schema.setText(connection_params["schema"])
                self.lineEdit_table.setText(connection_params["table"])
        except FileNotFoundError:
            pass
        except KeyError:
            pass
        try:
            filename = os.path.join(
                QgsApplication.qgisSettingsDirPath(), "connection_params.json"
            )
            with open(filename) as f:
                connection_params = json.load(f)
                self.lineEdit_file.setText(connection_params["file"])
        except FileNotFoundError:
            pass
        except KeyError:
            pass

    def get_connection(self):
        index = self.stacked_widget.currentIndex()
        if index == 0:
            file = self.lineEdit_file.text()
            type = "Geopackage"
            return type, file
        elif index == 1:
            url = "https://api.panoramax.xyz/api"
            type = "Panoramax"
            return type, url
        elif index == 2:
            type = "PostGIS"
            host = self.lineEdit_host.text()
            port = self.lineEdit_port.text()
            database = self.lineEdit_database.text()
            username = self.lineEdit_username.text()
            schema = self.lineEdit_schema.text()
            table = self.lineEdit_table.text()
            password = self.lineEdit_password.text()
            return type, host, port, database, username, password, schema, table

    def save_connection(self):
        index = self.stacked_widget.currentIndex()
        if index == 0:
            file = self.lineEdit_file.text()
            connection_params = {"file": file}
        if index == 1:
            url = "https://api.panoramax.xyz/api"
            connection_params = {"url": url}
        elif index == 2:
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
        filename = os.path.join(
            QgsApplication.qgisSettingsDirPath(), "connection_params.json"
        )
        if os.path.exists(filename):
            with open(filename) as f:
                existing_params = json.load(f)
            existing_params.update(connection_params)
            with open(filename, "w") as f:
                json.dump(existing_params, f)
        else:
            with open(filename, "w") as f:
                json.dump(connection_params, f)

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Geopackage file",
            "",
            "Geopackage (*.gpkg);;All Files (*)",
            options=options,
        )
        if file:
            self.lineEdit_file.setText(file)


class MainWindow(QMainWindow):
    instances = []

    def __init__(
        self,
        iface,
        url,
        pointReal,
        map_manager,
        direction,
        angle_degrees,
        x,
        y,
        params,
        gpkg,
        dates,
        date_index,
    ):
        super().__init__(iface.mainWindow())
        MainWindow.instances.append(self)
        self.iface = iface
        self.url = url
        self.pointReal = pointReal
        self.map_manager = map_manager
        self.direction = direction
        self.angle_degrees = angle_degrees
        self.x = x
        self.y = y
        self.params = params
        self.gpkg = gpkg
        self.gl_widget2 = None
        horizontalLayout = QHBoxLayout()
        self.horizontalLayout2 = QHBoxLayout()
        self.comboBox1 = QComboBox()
        if dates is not None:
            for date in dates:
                self.comboBox1.addItem(date)
        date_label = QLabel("Date")
        if date_index:
            self.comboBox1.setCurrentIndex(date_index)
        self.comboBox1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        horizontalLayout.setStretchFactor(date_label, 0)
        horizontalLayout.addWidget(date_label)
        horizontalLayout.addWidget(self.comboBox1)
        self.setFocus()
        gap_label = QLabel("Gap")
        self.gap_spinbox = QSpinBox()
        self.gap_spinbox.setMinimum(1)
        self.gap_spinbox.setMaximum(50)
        try:
            filename = os.path.join(
                QgsApplication.qgisSettingsDirPath(), "connection_params.json"
            )
            with open(filename) as f:
                connection_params = json.load(f)
                default_gap = connection_params["gap"]
                self.gap_spinbox.setValue(int(default_gap))
        except Exception:
            default_gap = 5
            self.gap_spinbox.setValue(default_gap)
        self.gap_spinbox.valueChanged.connect(
            lambda value: map_manager.modify_line_length(value)
        )
        self.show_button = QPushButton("Comparative view")
        self.show_button.clicked.connect(self.show_second_view)
        self.cross_button = QPushButton("Cross position")
        self.cross_button.clicked.connect(map_manager.check_for_crossing_lines)
        horizontalLayout.setStretchFactor(gap_label, 0)
        horizontalLayout.addWidget(self.show_button)
        horizontalLayout.addWidget(self.cross_button)
        horizontalLayout.addWidget(gap_label)
        horizontalLayout.addWidget(self.gap_spinbox)
        self.gap_spinbox.setFocusPolicy(Qt.NoFocus)
        self.verticalLayout = QVBoxLayout()
        self.map_manager.add_point_to_map(self.pointReal, self.angle_degrees, 1)
        self.gl_widget = GLWidget(
            self,
            iface,
            url,
            direction,
            map_manager,
            angle_degrees,
            x,
            y,
            params,
            gpkg,
            1,
        )
        self.gl_widget.setCursor(Qt.OpenHandCursor)
        self.gl_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalLayout2.addWidget(self.gl_widget)
        self.horizontalLayout2.setStretchFactor(self.gl_widget, 1)
        self.verticalLayout.addLayout(self.horizontalLayout2)
        self.verticalLayout.addLayout(horizontalLayout)
        map_manager.modify_line_length(default_gap)
        centralWidget = QWidget()
        centralWidget.setLayout(self.verticalLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle("Equirectangular 360° Viewer")
        self.setWindowIcon(QIcon(":/plugins/GLViewer/icon.png"))
        self.resize(1080, 720)

    def closeEvent(self, event):
        self.map_manager.remove_all_points_from_map()
        self.save_data()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.gl_widget.show_crosshair = not self.gl_widget.show_crosshair
            self.gl_widget.update()
            if self.gl_widget2 is not None:
                self.gl_widget2.show_crosshair = not self.gl_widget2.show_crosshair
                self.gl_widget2.update()

    def show_second_view(self):
        self.setCursor(Qt.WaitCursor)
        if self.gl_widget2 is None:
            self.comboBox1.setEnabled(False)
            self.gl_widget2 = GLWidget(
                self,
                self.iface,
                self.url,
                self.direction,
                self.map_manager,
                self.angle_degrees,
                self.x,
                self.y,
                self.params,
                self.gpkg,
                2,
            )
            self.horizontalLayout2.addWidget(self.gl_widget)
            self.horizontalLayout2.setStretchFactor(self.gl_widget, 1)
            self.horizontalLayout2.addWidget(self.gl_widget2)
            self.horizontalLayout2.setStretchFactor(self.gl_widget2, 1)
            self.verticalLayout.addLayout(self.horizontalLayout2)
            self.gl_widget2.show()
            self.gl_widget2.setCursor(Qt.OpenHandCursor)
            self.map_manager.add_point_to_map(self.pointReal, self.angle_degrees, 2)

        else:
            if self.gl_widget2.isVisible():
                self.comboBox1.setEnabled(True)
                self.gl_widget2.hide()
                self.gl_widget2 = None
                self.map_manager.remove_second_instance_points()
        self.unsetCursor()

    def save_data(self):
        gap = self.gap_spinbox.value()
        filename = os.path.join(
            QgsApplication.qgisSettingsDirPath(), "connection_params.json"
        )
        connection_params = {
            "gap": gap,
        }
        with open(filename) as f:
            connection_params = json.load(f)
            connection_params["gap"] = gap
        with open(filename, "w") as f:
            json.dump(connection_params, f)


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
        try:
            filename = os.path.join(
                QgsApplication.qgisSettingsDirPath(), "connection_params.json"
            )
            with open(filename) as f:
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
        except Exception:
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
        self.setWindowIcon(QIcon(":/plugins/GLViewer/icon.png"))
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
        filename = os.path.join(
            QgsApplication.qgisSettingsDirPath(), "connection_params.json"
        )
        with open(filename) as f:
            connection_params = json.load(f)
            connection_params["geom"] = geom
            connection_params["yaw"] = yaw
            connection_params["link"] = link
            connection_params["date"] = date
        with open(filename, "w") as f:
            json.dump(connection_params, f)

    def get_columns(self):
        geom = self.geom_combo.currentText()
        yaw = self.yaw_combo.currentText()
        link = self.link_combo.currentText()
        date = self.date_combo.currentText()
        return geom, yaw, link, date
