from .Windows import ConnectionDialog, ColumnSelectionDialog
from .DBHandler import retrieve_columns
from qgis.PyQt.QtWidgets import  QDialog
import psycopg2
from qgis.core import Qgis


def get_connection(iface):
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
        main_window = ColumnSelectionDialog(columns)

        result = main_window.exec_()
        if result == QDialog.Accepted:
            params = {'conn': conn, 'fov': 90}

            return params
        else:
            pass

    return None