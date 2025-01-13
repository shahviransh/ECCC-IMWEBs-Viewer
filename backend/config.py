import os
import sys


class Config:
    PATHFILE = (
        sys._MEIPASS
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.realpath(__file__))
    )
    conda_prefix = os.environ.get("CONDA_PREFIX")
    PROJ_LIB = (
        os.path.join(sys._MEIPASS, "Library/share/proj")
        if getattr(sys, "frozen", False)
        else os.path.join(conda_prefix, "Library/share/proj")
    )
    GDAL_DATA = (
        os.path.join(sys._MEIPASS, "Library/share/gdal")
        if getattr(sys, "frozen", False)
        else os.path.join(conda_prefix, "Library/share/gdal")
    )
    EXPORT_PATH = os.getenv("EXPORT_PATH", "dataExport")
    LOOKUP = "Jenette_Creek_Watershed/Database/lookup.db3"
