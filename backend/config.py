import os
import sys

class Config:
    PATHFILE = os.getenv('DB_PATH', sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.realpath(__file__)))
    EXPORT_PATH = os.getenv('EXPORT_PATH', 'dataExport')
    LOOKUP = "Jenette_Creek_Watershed\Database\lookup.db3"