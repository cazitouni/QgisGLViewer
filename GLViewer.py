from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QAction,  QDialog

from qgis.PyQt.QtGui import QIcon

from .Windows import  PointTool
from .Windows import ConnectionDialog, ColumnSelectionDialog
from .DBHandler import retrieve_columns

from .resources import *
import os
import psycopg2
  
class GLViewer:

    def __init__(self, iface):

        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.params = None
        
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GLViewer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Equirectangular Viewer')

    def tr(self, message):
        return QCoreApplication.translate('GLViewer', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):

        icon_path = ':/plugins/GLViewer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'360° view'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Equirectangular Viewer'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.params is None:
            self.params = self.get_connection(self.iface)
            if self.params is None:
                return 
        cursor = self.params['conn'].cursor()
        schema = self.params['schema']
        table = self.params['table']
        geom = self.params['geom']
        yaw = self.params['yaw']
        link = self.params['link']

        tool = PointTool(self.iface.mapCanvas(), self.iface, cursor, geom, yaw, link, schema, table)
        self.iface.mapCanvas().setMapTool(tool)
    
    def get_connection(self, iface):
        dialog = ConnectionDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            host, port, database, username, password, schema, table = dialog.get_connection()
            try:
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=username,
                    password=password
                )
            except psycopg2.Error:
                iface.messageBar().pushMessage("Unable to connect to the database", level=Qgis.Info)

            columns = retrieve_columns(schema, table, conn.cursor())
            second_dialog = ColumnSelectionDialog(columns)
            result = second_dialog.exec_()
            if result == QDialog.Accepted:
                geom, yaw, link, date = second_dialog.get_columns()
                params = {'conn': conn, "geom":geom, "yaw": yaw, "link":link, "date":date, "schema":schema, "table":table}
                return params
            else:
                pass

        return None