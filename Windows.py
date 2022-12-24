from qgis.PyQt.QtWidgets import QAction, QDesktopWidget, QMainWindow, QHBoxLayout, QComboBox, QVBoxLayout, QWidget, QFileDialog, QGridLayout, QPushButton, QLabel, QLineEdit, QDialog
from qgis.PyQt.QtGui import QIcon
from qgis.core import Qgis
from qgis.gui import QgsMapTool

from .EquiView360 import GLWidget
from .DBHandler import connector

import json

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        button_connect = QPushButton("Connect")
        button_cancel = QPushButton("Cancel")

        button_layout = QHBoxLayout()
        button_layout.addWidget(button_connect)
        button_layout.addWidget(button_cancel)


        grid = QGridLayout()
        grid.addWidget(label_host, 0, 0)
        grid.addWidget(self.lineEdit_host, 0, 1)
        grid.addWidget(label_port, 1, 0)
        grid.addWidget(self.lineEdit_port, 1, 1)
        grid.addWidget(label_database, 2, 0)
        grid.addWidget(self.lineEdit_database, 2, 1)
        grid.addWidget(label_username, 3, 0)
        grid.addWidget(self.lineEdit_username, 3, 1)
        grid.addWidget(label_password, 4, 0)
        grid.addWidget(self.lineEdit_password, 4, 1)
        grid.addWidget(label_schema, 5, 0)
        grid.addWidget(self.lineEdit_schema, 5, 1)
        grid.addWidget(label_table, 6, 0)
        grid.addWidget(self.lineEdit_table, 6, 1)
        grid.addLayout(button_layout, 7, 0, 1, 2)


        self.setLayout(grid)

        button_connect.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
        button_connect.clicked.connect(self.save_connection)
        try:
            with open("connection_params.json", "r") as f:
                connection_params = json.load(f)
                self.lineEdit_host.setText(connection_params["host"])
                self.lineEdit_port.setText(connection_params["port"])
                self.lineEdit_database.setText(connection_params["database"])
                self.lineEdit_username.setText(connection_params["username"])
                self.lineEdit_schema.setText(connection_params["schema"])
                self.lineEdit_table.setText(connection_params["table"])
        except FileNotFoundError:
            pass

    def get_connection(self):
        """
        Get the connection parameters entered by the user.
        Returns:
            A tuple containing the host, port, database, username, and password.
        """
        host = self.lineEdit_host.text()
        port = self.lineEdit_port.text()
        database = self.lineEdit_database.text()
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        schema = self.lineEdit_schema.text()
        table = self.lineEdit_table.text()
        return host, port, database, username, password, schema, table

    def save_connection(self):
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
        with open("connection_params.json", "w") as f:
            json.dump(connection_params, f)
    def accept(self):
        if not all([self.lineEdit_host.text(), self.lineEdit_port.text(), self.lineEdit_database.text(), self.lineEdit_username.text(), self.lineEdit_password.text(), self.lineEdit_schema.text(), self.lineEdit_table.text()]):
            # Display an error message or do something else to indicate to the user that all fields are required
            pass
        else:
            super().accept()

class MainWindow(QMainWindow):
    def __init__(self, iface, url):
        super().__init__()

        # Create the horizontal layout for the list widgets
        horizontalLayout = QHBoxLayout()
        comboBox1 = QComboBox()
        comboBox2 = QComboBox()
        comboBox3 = QComboBox()
        horizontalLayout.addWidget(comboBox1)
        horizontalLayout.addWidget(comboBox2)
        horizontalLayout.addWidget(comboBox3)

        # Create the vertical layout for the GLWidget and list widgets
        verticalLayout = QVBoxLayout()
        self.gl_widget = GLWidget(self, iface, url)
        verticalLayout.addWidget(self.gl_widget)
        verticalLayout.addLayout(horizontalLayout)

        # Set the main window's central widget and layout
        centralWidget = QWidget()
        centralWidget.setLayout(verticalLayout)
        self.setCentralWidget(centralWidget)

        # Set the window properties
        self.setWindowTitle("Equirectangular 360° Viewer")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(0, 0, 1080, 720)

class PointTool(QgsMapTool):  

    def __init__(self, canvas, iface, cursor):
        QgsMapTool.__init__(self, canvas)
        self.iface = iface
        self.canvas = canvas
        self.cursor = cursor

    def canvasPressEvent(self, event):
        t = event.pos().x()
        w = event.pos().y()
        point = self.canvas.getCoordinateTransform().toMapCoordinates(t, w)
        url = connector(point.x(), point.y(), self.cursor)
        if url != 0 :
            self.dlg = MainWindow(self.iface, url)
            screen = QDesktopWidget().screenGeometry()
            size = self.dlg.geometry()
            x = (screen.width() - size.width()) / 2
            y = (screen.height() - size.height()) / 2
            self.dlg.move(x, y)
            self.dlg.show()
            self.iface.mapCanvas().unsetMapTool(self)
        else : 
            self.iface.messageBar().pushMessage("No image for this coordinates", level=Qgis.Info)

class ColumnSelectionDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        
        # Create a label and combo box for each column
        self.yaw_label = QLabel("Direction column:")
        self.yaw_combo = QComboBox()
        self.link_label = QLabel("Link column:")
        self.link_combo = QComboBox()
        self.date_label = QLabel("Date column:")
        self.date_combo = QComboBox()
        self.fov_label = QLabel("FOV column:")
        self.fov_combo = QComboBox()
        
        # Populate the combo boxes with the available columns
        self.yaw_combo.addItems(columns)
        self.link_combo.addItems(columns)
        self.date_combo.addItems(columns)
        self.fov_combo.addItems(columns)
        
        # Create a button to accept the selected columns
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        # Create a vertical layout to hold the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.yaw_label)
        layout.addWidget(self.yaw_combo)
        layout.addWidget(self.link_label)
        layout.addWidget(self.link_combo)
        layout.addWidget(self.date_label)
        layout.addWidget(self.date_combo)
        layout.addWidget(self.fov_label)
        layout.addWidget(self.fov_combo)
        layout.addWidget(self.ok_button)
        
        # Set the layout of the dialog
        self.setLayout(layout)