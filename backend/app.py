from flask import Flask, request, jsonify, send_file
import signal
import pandas as pd
import sys
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Apply CORS to the entire app
PATHFILE = sys._MEIPASS if getattr(app, 'frozen', False) else os.path.dirname(os.path.realpath(__file__))


# Helper function to fetch data from the SQLite database
def fetch_data_from_db(
    db_path,
    table_name,
    selected_id=[""],
    columns="All",
    start_date=None,
    end_date=None,
    date_type=None,
):
    """Fetch data from SQLite database with optional ID filtering."""
    conn = sqlite3.connect(os.path.join(PATHFILE, db_path))
    cursor = conn.cursor()

    # Use parameterized queries to avoid SQL injection
    query = f"SELECT * FROM {table_name}"  # Table name is not parameterized
    params = []

    # If a specific ID is provided, filter by that ID
    if selected_id != [""]:
        # Use placeholders for each ID
        placeholders = ",".join(["?"] * len(selected_id))
        query += f" WHERE ID IN ({placeholders})"
        params.extend(selected_id)

    # If columns are specified, fetch only those columns
    if columns != "All":
        column_names = ",".join(columns.split(","))
        query = query.replace("*", column_names)

    # If start and end dates are provided, filter by date range
    if start_date and end_date and date_type == "Month":
        if "WHERE" in query:
            query += f" AND {date_type} >= ? AND {date_type} <= ?"
        else:
            query += f" WHERE {date_type} >= ? AND {date_type} <= ?"
        params.extend([start_date, end_date])
    elif start_date and end_date and date_type in ["Time", "Date"]:
        if "WHERE" in query:
            query += f" AND {date_type} >= ? AND {date_type} <= ?"
        else:
            query += f" WHERE {date_type} >= ? AND {date_type} <= ?"
        params.extend([start_date, end_date])

    # Execute the parameterized query
    df = pd.read_sql_query(query, conn, params=params)
    df = df.map(round_numeric_values)

    conn.close()
    return df


def get_columns_and_time_range(db_path, table_name):
    """Fetch column names and time range from a SQLite database table."""
    conn = sqlite3.connect(os.path.join(PATHFILE, db_path))
    query = f"PRAGMA table_info('{table_name}')"
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [row[1] for row in cursor.fetchall()]

    # Initialize variables
    start_date = end_date = date_type = None

    # Check and query for specific date/time columns
    if "Time" in columns:
        df = pd.read_sql_query(f"SELECT Time FROM {table_name}", conn)
        df["Time"] = pd.to_datetime(df["Time"])
        start_date = df["Time"].min().strftime("%Y-%m-%d")
        end_date = df["Time"].max().strftime("%Y-%m-%d")
        date_type = "Time"
    elif "Date" in columns:
        df = pd.read_sql_query(f"SELECT Date FROM {table_name}", conn)
        df["Date"] = pd.to_datetime(df["Date"])
        start_date = df["Date"].min().strftime("%Y-%m-%d")
        end_date = df["Date"].max().strftime("%Y-%m-%d")
        date_type = "Date"
    elif "Month" in columns:
        df = pd.read_sql_query(f"SELECT Month FROM {table_name}", conn)
        start_date = str(df["Month"].min())
        end_date = str(df["Month"].max())
        date_type = "Month"

    # Get list of IDs if an ID column exists, without querying unnecessary data
    id_column = next((col for col in columns if "ID" in col), None)
    ids = []
    if id_column:
        id_query = f"SELECT DISTINCT {id_column} FROM {table_name}"
        id_df = pd.read_sql_query(id_query, conn)
        ids = id_df[id_column].astype(str).tolist()
    conn.close()

    return columns, start_date, end_date, ids, date_type


# Example function to map date strings to seasons
def get_season_from_date(date_str):
    try:
        month = date_str.month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Autumn"
    except ValueError:
        return "Invalid date"


# Helper function to apply time interval aggregation
def aggregate_data(df, interval, method, date_type):
    """Aggregate data based on the specified interval and method."""
    # Convert the 'date' column to datetime
    df[date_type] = pd.to_datetime(df[date_type])
    df.set_index(date_type, inplace=True)
    resampled_df = None

    if interval == "monthly":
        resampled_df = df.groupby('ID').resample("ME").first()
    elif interval == "seasonally":
        # Custom resampling for seasons
        df.reset_index(inplace=True)
        df["Season"] = df[date_type].apply(lambda x: get_season_from_date(x))
        df.set_index(date_type, inplace=True)
        resampled_df = df
    elif interval == "yearly":
        resampled_df = df.groupby('ID').resample("YE").first()
    else:
        resampled_df = df
    
    resampled_df = resampled_df.drop(columns=['ID']) if 'ID' in resampled_df.index.names else resampled_df
    resampled_df.reset_index(inplace=True)
    
    if interval != "seasonally":
        resampled_df[date_type] = resampled_df[date_type].dt.strftime('%Y-%m') if interval == "monthly" else resampled_df[date_type].dt.strftime('%Y')
    else:
        resampled_df[date_type] = resampled_df[date_type].dt.strftime('%Y-%m-%d')
    stats_df = calculate_statistics(resampled_df, method, date_type)

    return resampled_df, stats_df.map(round_numeric_values)

# Ensure all numeric values are rounded
def round_numeric_values(value):
    if isinstance(value, (float, int)):  # Check if the value is a number
        return round(value, 3)  # Round to 3 decimal places
    return value  # Leave non-numeric values unchanged

# Helper function to calculate statistics
def calculate_statistics(df, statistics, date_type):
    """Calculate specified statistics for numerical data in the DataFrame."""
    stats_df = pd.DataFrame()

    # Store the original DataFrame with all columns
    original_df = df.copy()

    # Select only numerical columns for calculations
    df = df.select_dtypes(include=['number'])
    # Drop the date_type column if it exists
    df = df.drop(columns=[date_type], errors='ignore')

    if "Average" in statistics:
        stats_df["Average"] = df.mean()
    if "Sum" in statistics:
        stats_df["Sum"] = df.sum()
    if "Maximum" in statistics:
        stats_df["Maximum"] = df.max()
        # Use original DataFrame to get the corresponding date_type values for maximums
        # Ignore if date_type is not present in the original DataFrame
        max_date_type = {col: original_df.loc[original_df[col].idxmax(), date_type] for col in df.columns if date_type in original_df.columns}
        stats_df[f"Maximum {date_type}"] = pd.Series(max_date_type)
    if "Minimum" in statistics:
        stats_df["Minimum"] = df.min()
        # Use original DataFrame to get the corresponding date_type values for minimums
        # Ignore if date_type is not present in the original DataFrame
        min_date_type = {col: original_df.loc[original_df[col].idxmin(), date_type] for col in df.columns if date_type in original_df.columns}
        stats_df[f"Minimum {date_type}"] = pd.Series(min_date_type)
    if "Standard Deviation" in statistics:
        stats_df["Standard Deviation"] = df.std()

    # Transpose and format DataFrame
    stats_df = stats_df.T
    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"index": "Statistics"}, inplace=True)

    return stats_df.map(round_numeric_values)

@app.route("/api/list_files", methods=["GET"])
def list_files():
    """
    Endpoint to list all files and directories in the specified path.
    """
    folder_path = request.args.get("folder_path", "Jenette_Creek_Watershed")
    base_folder = folder_path
    base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    folder_path = os.path.join(base_path, folder_path)  # Absolute path Get absolute path relative to app.py
    allowed_base_path = os.path.abspath(os.path.join(base_path, base_folder))  # Absolute base folder path

    # Validate that the requested path is within the allowed base directory
    if not folder_path.startswith(allowed_base_path):
        return abort(400, "Invalid folder path")

    try:
        files_and_folders = []
        root = os.path.abspath(base_folder)  # Absolute path to the base folder

        for dirpath, dirs, files in os.walk(folder_path):
            # Construct the relative path from the base folder
            rel_dir = os.path.relpath(dirpath, root)

            # Append directories
            for fdir in dirs:
                dir_rel_path = os.path.join(rel_dir, fdir)
                # Ensure the relative path starts with the base folder name
                dir_rel_path = dir_rel_path[dir_rel_path.find(base_folder):]
                files_and_folders.append(
                    {
                        "type": "folder",
                        "name": dir_rel_path,
                    }
                )
            # Append files
            for name in files:
                file_rel_path = os.path.join(rel_dir, name)
                # Ensure the relative path starts with the base folder name
                file_rel_path = file_rel_path[file_rel_path.find(base_folder):]
                files_and_folders.append(
                    {
                        "type": "database" if file_rel_path.endswith(".db3") else "file",
                        "name": file_rel_path,
                    }
                )

        return jsonify(files_and_folders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_tables", methods=["GET"])
def get_tables():
    """
    Endpoint to get all table names from the specified database.
    """
    data = request.args
    db_path = data.get("db_path")

    if not db_path:
        return jsonify({"error": "Database path is required."}), 400

    try:
        # Connect to database and fetch table names
        conn = sqlite3.connect(os.path.join(PATHFILE, db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        return jsonify(tables)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_table_details", methods=["GET"])
def get_table_details():
    """
    Endpoint to get table column names, time start, time end, and ID list.
    """
    data = request.args
    db_path = data.get("db_path")
    
    table_name = data.get("table_name")

    if not all([db_path, table_name]):
        return jsonify({"error": "Database path and table name are required."}), 400

    try:
        # Fetch only the columns names and time start and time end
        columns, start_date, end_date, ids, date_type = get_columns_and_time_range(
            db_path, table_name
        )

        return jsonify(
            {
                "columns": columns,
                "start_date": start_date,
                "end_date": end_date,
                "ids": ids,
                "date_type": date_type,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function to save data to CSV or text formats
def save_to_file(dataframe1, dataframe2, filename, file_format, export_path, options):
    """Save two DataFrames to the specified file format sequentially."""
    # Set the file path
    file_path = os.path.join(PATHFILE, export_path) if not os.path.exists(export_path) else export_path
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = os.path.join(file_path, filename)
    
    # Write first dataframe
    if file_format == "csv":
        with open(file_path, 'w', newline='') as f:
            if options['data']:
                dataframe1.to_csv(f, index=False)
            if options['stats'] and dataframe2 is not None:
                f.write("\n")  # Optional: Add a blank line or custom separator between the tables
                dataframe2.to_csv(f, index=False)
    elif file_format == "text":
        with open(file_path, 'w') as f:
            if options['data']:
                dataframe1.to_csv(f, index=False, sep=" ")
            if options['stats'] and dataframe2 is not None:
                f.write("\n")  # Optional: Add a blank line or custom separator between the tables
                dataframe2.to_csv(f, index=False, sep=" ")

    return file_path


@app.route("/api/get_data", methods=["GET"])
def get_data():
    """
    Endpoint to get data from the specified database and table.
    """
    data = request.args
    db_path = data.get("db_path")  # Path to the SQLite database
    table_name = data.get("table_name")  # Table name to fetch data from
    columns = data.get("columns", "All")  # Columns to fetch data from
    columns = columns.replace("Statistics,", "")
    selected_id = data.get("id", [])  # ID to filter data, if provided
    selected_id = selected_id.split(",") if selected_id != [""] else selected_id
    start_date = data.get("start_date")  # Start date for filtering
    end_date = data.get("end_date")  # End date for filtering
    date_type = data.get("date_type", None)  # Date column type
    interval = data.get(
        "interval", "daily"
    )  # Export interval (daily, monthly, seasonal, yearly)
    method = data.get(
        "method", ["Equal"]
    )  # Aggregation method (Equal, Average, Sum, Max, Min)
    method = method.split(",") if method != ["Equal"] else method
    statistics = data.get("statistics", ["None"])  # List of statistics to calculate
    statistics = statistics.split(",") if statistics != ["None"] else statistics
    stats_df = None

    if not all([db_path, table_name]):
        return jsonify({"error": "Database path and table name are required."}), 400

    try:
        # Fetch data from the database
        df = fetch_data_from_db(
            db_path, table_name, selected_id, columns, start_date, end_date, date_type
        )
        columns = columns.split(",") if columns != "All" else columns
        df = df.get(columns, df) if columns != "All" else df

        # Aggregate data based on interval and method
        if "Equal" not in method and date_type in ['Time', 'Date'] and interval != "daily":
            df, stats_df = aggregate_data(df, interval, method, date_type)
        # Calculate statistics if specified
        elif "None" not in statistics:
            stats_df = calculate_statistics(df, statistics, date_type)


        return_dict = {"data": df.to_dict(orient="records"), "stats": stats_df.to_dict(orient="records") if stats_df is not None else [], "statsColumns": stats_df.columns.tolist() if stats_df is not None else []}

        # Return the processed data as JSON
        return jsonify(return_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export_data", methods=["GET"])
def export_data():
    """
    Endpoint to export the requested data to a specified file format.
    """
    data = request.args
    db_path = data.get("db_path")
    table_name = data.get("table_name")
    columns = data.get("columns", "All")
    columns = columns.replace("Statistics,", "")
    selected_id = data.get("id", [])
    selected_id = selected_id.split(",") if selected_id != [""] else selected_id
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    date_type = data.get("date_type", None)
    interval = data.get("interval", "daily")
    method = data.get("method", ["Equal"])
    method = method.split(",") if method != ["Equal"] else method
    statistics = data.get("statistics", ["None"])
    statistics = statistics.split(",") if statistics != ["None"] else statistics
    output_dest = data.get("export_path", "dataExport")
    output_name = data.get(
        "export_filename", f"exported_data_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    output_type = data.get("export_format", "csv")
    # Handle options nested structure
    options = {
        "data": data.get("options[data]", "true") == "true",
        "stats": data.get("options[stats]", "true") == "true",
    }
    stats_df = None
    if not all([db_path, table_name]):
        return jsonify({"error": "Database path and table name are required."}), 400

    try:
        # Fetch and process data
        df = fetch_data_from_db(
            db_path, table_name, selected_id, columns, start_date, end_date, date_type
        )
        columns = columns.split(",") if columns != "All" else columns
        df = df.get(columns, df) if columns != "All" else df

        if "Equal" not in method and date_type in ['Time', 'Date'] and interval != "daily":
            df, stats_df = aggregate_data(df, interval, method, date_type)
        elif "None" not in statistics:
            stats_df = calculate_statistics(df, statistics, date_type)

        # Save the processed data to file
        file_path = save_to_file(
            df, stats_df, output_name + "." + output_type, output_type, output_dest, options
        )

        # Send the file to the client
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def shutdown_server():
    os.kill(os.getpid(), signal.SIGINT)

@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == "__main__":
    app.run(debug=True)