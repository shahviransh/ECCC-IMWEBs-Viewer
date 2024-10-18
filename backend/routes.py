from flask import jsonify, request, send_file
import os
import sys
from services import fetch_data_service, get_files_and_folders, get_table_names, export_data_service, get_columns_and_time_range
from utils import shutdown_server, clear_cache

def register_routes(app, cache):
    @app.route("/api/get_data", methods=["GET"])
    @cache.cached(timeout=300, query_string=True)  # Cache this endpoint for 5 minutes (300 seconds)
    def get_data():
        data = request.args
        response = fetch_data_service(data)
        return jsonify(response)

    @app.route("/api/export_data", methods=["GET"])
    # This endpoint is not cached because the file is generated dynamically
    def export_data():
        data = request.args
        file_path = export_data_service(data)

        return send_file(file_path, as_attachment=True)

    @app.route("/api/get_tables", methods=["GET"])
    @cache.cached(timeout=300, query_string=True)  # Cache this endpoint for 5 minutes (300 seconds)
    def get_tables():
        data = request.args
        db_path = data.get("db_path")

        # Fetch the table names from the database
        tables = get_table_names(db_path)
        return jsonify(tables)

    @app.route("/api/list_files", methods=["GET"])
    @cache.cached(timeout=300, query_string=True)  # Cache this endpoint for 5 minutes (300 seconds)
    def list_files():
        """
        Endpoint to list all files and directories in the specified path.
        """
        data = request.args
        files_and_folders = get_files_and_folders(data)

        return jsonify(files_and_folders)


    @app.route("/api/get_table_details", methods=["GET"])
    @cache.cached(timeout=300, query_string=True)  # Cache this endpoint for 5 minutes (300 seconds)
    def get_table_details():
        """
        Endpoint to get table column names, time start, time end, and ID list.
        """
        data = request.args
        db_path = data.get("db_path")
        table_name = data.get("table_name")
        
        # Fetch the column names, start date, end date, IDs, and date type
        columns, start_date, end_date, ids, date_type = get_columns_and_time_range(db_path, table_name)

        return jsonify(
            {
                "columns": columns,
                "start_date": start_date,
                "end_date": end_date,
                "ids": ids,
                "date_type": date_type,
            }
        )
    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        shutdown_server()
        return 'Server shutting down...'
    @app.route('/clear_cache', methods=['GET'])
    def clear_cache_route():
        clear_cache()
        return 'Cache cleared.'