from flask import jsonify, request, send_file
import os
import sys
from services import (
    fetch_data_service,
    get_files_and_folders,
    get_table_names,
    export_data_service,
    get_multi_columns_and_time_range,
    process_geospatial_data,
    export_map_service,
)
from utils import shutdown_server, clear_cache
from validate import (
    validate_get_data_args,
    validate_export_data_args,
    validate_get_tables_args,
    validate_list_files_args,
    validate_get_table_details_args,
    validate_geospatial_args,
    validate_export_map_args,
    validate_serve_tif_args
)


def register_routes(app, cache):
    @app.route("/api/get_data", methods=["GET"])
    @cache.cached(
        timeout=120, query_string=True
    )
    def get_data():
        data = request.args

        # Validate the request arguments
        validation_response = validate_get_data_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        response = fetch_data_service(data)

        return jsonify(response)

    @app.route("/api/export_data", methods=["GET"])
    # This endpoint is not cached because the file is generated dynamically
    def export_data():
        data = request.args

        # Validate the request arguments
        validation_response = validate_export_data_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        file_path = export_data_service(data)

        return send_file(file_path.get("file_path"), as_attachment=True)

    @app.route("/api/get_tables", methods=["GET"])
    @cache.cached(
        timeout=120, query_string=True
    )
    def get_tables():
        data = request.args

        # Validate the request arguments
        validation_response = validate_get_tables_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        # Fetch the table names from the database
        tables = get_table_names(data)

        return jsonify(tables.get("tables"))

    @app.route("/api/list_files", methods=["GET"])
    def list_files():
        """
        Endpoint to list all files and directories in the specified path.
        """
        data = request.args

        # Validate the request arguments
        validation_response = validate_list_files_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        files_and_folders = get_files_and_folders(data)

        return jsonify(files_and_folders.get("files_and_folders"))

    @app.route("/api/get_table_details", methods=["GET"])
    @cache.cached(
        timeout=120, query_string=True
    )  # Cache this endpoint for 2 minutes (120 seconds)
    def get_table_details():
        """
        Endpoint to get table column names, time start, time end, and ID list, date type, and default interval.
        """
        data = request.args

        # Validate the request arguments
        validation_response = validate_get_table_details_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        columns_and_time_range_dict = get_multi_columns_and_time_range(data)

        return jsonify(columns_and_time_range_dict)

    @app.route("/api/geospatial", methods=["GET"])
    @cache.cached(timeout=120, query_string=True)
    def geospatial():
        """
        API endpoint to return GeoJSON/Tiff Image Url, bounds, and center.
        """
        data = request.args

        # Validate the request arguments
        validation_response = validate_geospatial_args(data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        geo_data = process_geospatial_data(data)

        return jsonify(geo_data)

    @app.route("/geotiff/<path:filename>", methods=["GET"])
    def serve_tif(filename):
        """
        Serve the TIF file from the specified path.
        """

        # Validate the file path
        validation_response = validate_serve_tif_args(filename)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        return send_file(filename, mimetype='image/png', as_attachment=True)
    
    @app.route('/api/export_map', methods=['POST'])
    def export_map():
        """
        API endpoint to export the map image.
        """
        image = request.files.get('image')
        form_data = request.form.to_dict()

        # Validate the request arguments
        validation_response = validate_export_map_args(image, form_data)
        if validation_response.get("error", None):
            return jsonify(validation_response)

        image_path = export_map_service(image, form_data)

        return jsonify(image_path)

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
