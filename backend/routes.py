from flask import jsonify, request, send_file
import os
import sys
from services import (
    fetch_data_service,
    get_files_and_folders,
    get_table_names,
    export_data_service,
    get_multi_columns_and_time_range,
    get_dbf_details,
    process_geospatial_data_for_mapbox
)
from utils import shutdown_server, clear_cache


def register_routes(app, cache):
    @app.route("/api/get_data", methods=["GET"])
    @cache.cached(
        timeout=300, query_string=True
    )  # Cache this endpoint for 5 minutes (300 seconds)
    def get_data():
        data = request.args
        response = fetch_data_service(data)

        return jsonify(response)

    @app.route("/api/export_data", methods=["GET"])
    # This endpoint is not cached because the file is generated dynamically
    def export_data():
        data = request.args
        file_path = export_data_service(data)

        return send_file(file_path.get("file_path"), as_attachment=True)

    @app.route("/api/get_tables", methods=["GET"])
    @cache.cached(
        timeout=300, query_string=True
    )  # Cache this endpoint for 5 minutes (300 seconds)
    def get_tables():
        data = request.args

        # Fetch the table names from the database
        tables = get_table_names(data)

        if tables.get("error", None):
            return jsonify(tables)

        return jsonify(tables.get("tables"))

    @app.route("/api/list_files", methods=["GET"])
    @cache.cached(
        timeout=300, query_string=True
    )  # Cache this endpoint for 5 minutes (300 seconds)
    def list_files():
        """
        Endpoint to list all files and directories in the specified path.
        """
        data = request.args
        files_and_folders = get_files_and_folders(data)

        if files_and_folders.get("error", None):
            return jsonify(files_and_folders)

        return jsonify(files_and_folders.get("files_and_folders"))

    @app.route("/api/get_table_details", methods=["GET"])
    @cache.cached(
        timeout=300, query_string=True
    )  # Cache this endpoint for 5 minutes (300 seconds)
    def get_table_details():
        """
        Endpoint to get table column names, time start, time end, and ID list.
        """
        data = request.args

        # Fetch the column names, start date, end date, IDs, date type, and default interval
        columns_and_time_range_dict = get_multi_columns_and_time_range(data)

        if columns_and_time_range_dict.get("error", None):
            return jsonify(columns_and_time_range_dict)

        return jsonify(columns_and_time_range_dict)

    @app.route("/api/get_dbf_details", methods=["GET"])
    @cache.cached(
        timeout=300, query_string=True
    )
    def get_dbf_details():
        """
        Endpoint to get column names and data types from a DBF file.
        """
        data = request.args

        # Fetch the column names and data types from the DBF file
        dbf_details = get_dbf_details(data)

        if dbf_details.get("error", None):
            return jsonify(dbf_details)

        return jsonify(dbf_details)
    
    @app.route("/api/mapbox_shapefile", methods=["POST"])
    @cache.cached(
        timeout=300, query_string=True
    )
    def mapbox_shapefile():
        """
        API endpoint to return GeoJSON, bounds, and layer configurations for Mapbox.
        """
        data = request.json

        mapbox_data = process_geospatial_data_for_mapbox(data)
        
        if mapbox_data.get("error", None):
            return jsonify(mapbox_data)

        return jsonify(mapbox_data)

    @app.route("/health", methods=["GET"])
    def health():
        return "Server is running...", 200

    @app.route("/shutdown", methods=["GET"])
    def shutdown():
        shutdown_server()
        return "Server shutting down...", 200

    @app.route("/clear_cache", methods=["GET"])
    def clear_cache_route():
        clear_cache(cache)
        return "Cache cleared.", 200
