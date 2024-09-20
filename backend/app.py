from flask import Flask, request, jsonify, send_file
import pandas as pd
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Apply CORS to the entire app
PATHFILE = os.path.dirname(os.path.realpath(__file__))


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
    query = f"SELECT * FROM {table_name}"

    # If a specific ID is provided, filter by that ID
    if selected_id != [""]:
        # For multiple ids
        query += f" WHERE ID IN ({','.join(selected_id)})"

    # If columns are specified, fetch only those columns
    if columns != "All":
        query = query.replace("*", columns)

    # If start and end dates are provided, filter by date range
    if start_date and end_date and date_type == "Month":
        if "WHERE" in query:
            query += f" AND {date_type} >= {start_date} AND {date_type} <= {end_date}"
        else:
            query += f" WHERE {date_type} >= {start_date} AND {date_type} <= {end_date}"
    elif start_date and end_date and date_type in ["Time", "Date"]:
        if "WHERE" in query:
            query += f" AND {date_type} >= '{start_date}' AND {date_type} <= '{end_date}'"
        else:
            query += f" WHERE {date_type} >= '{start_date}' AND {date_type} <= '{end_date}'"

    df = pd.read_sql_query(query, conn)

    conn.close()
    return df


# Example function to map date strings to seasons
def get_season_from_date(date_str):
    month = datetime.strptime(date_str, "%Y-%m-%d").month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"


# Helper function to apply time interval aggregation
def aggregate_data(df, interval, method):
    """Aggregate data based on the specified interval and method."""
    # Convert the 'date' column to datetime
    try:
        df["Time"] = pd.to_datetime(df["Time"])
        df.set_index('Time', inplace=True)
    except Exception as e:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index('Date', inplace=True)
    resampled_df = None
    print(df)

    if interval == "daily":
        resampled_df = df
    elif interval == "monthly":
        resampled_df = df.groupby('ID').resample("ME").first()
    elif interval == "seasonal":
        # Custom resampling for seasons
        try:
            df["Season"] = df["Time"].apply(lambda x: get_season_from_date(str(x)))
        except Exception as e:
            df["Season"] = df["Date"].apply(lambda x: get_season_from_date(str(x)))
        resampled_df = df.groupby("Season")
    elif interval == "yearly":
        resampled_df = df.groupby('ID').resample("YE").first()
    else:
        resampled_df = df
    
    resampled_df = resampled_df.drop(columns=['ID']) if 'ID' in df.index.names else resampled_df
    resampled_df.reset_index(inplace=True)
    print(resampled_df)
    stats_df = calculate_statistics(resampled_df, method)

    return resampled_df, stats_df


# Helper function to calculate statistics
def calculate_statistics(df, statistics):
    """Calculate specified statistics for numerical data in the DataFrame."""
    stats_df = pd.DataFrame()
    df = df.select_dtypes(include=['number'])
    if "Average" in statistics:
        stats_df["Average"] = df.mean()
    if "Sum" in statistics:
        stats_df["Sum"] = df.sum()
    if "Maximum" in statistics:
        stats_df["Maximum"] = df.max()
    if "Minimum" in statistics:
        stats_df["Minimum"] = df.min()
    if "Standard Deviation" in statistics:
        stats_df["Standard Deviation"] = df.std()

    stats_df = stats_df.T
    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"index": "Statistics"}, inplace=True)

    return stats_df


@app.route("/api/list_files", methods=["GET"])
def list_files():
    """
    Endpoint to list all files and directories in the specified path.
    """
    folder_path = request.args.get("folder_path", "Jenette_Creek_Watershed")
    base_folder = folder_path
    folder_path = os.path.join(
        os.path.dirname(__file__), folder_path
    )  # Get absolute path relative to app.py

    try:
        files_and_folders = []
        root = os.path.abspath(base_folder)  # Absolute path to the base folder

        for dirpath, dirs, files in os.walk(folder_path):
            # Construct the relative path from the base folder
            rel_dir = os.path.relpath(dirpath, root)
            # for fdir in dirs:
            #     rel_dir = os.path.join(rel_dir, fdir)
            #     rel_dir = rel_dir[rel_dir.find(base_folder):]
            #     files_and_folders.append(
            #         {
            #             "type": "folder",
            #             "name": rel_dir,
            #         }
            #     )  # Add base folder to the path
            for name in files:
                if name.endswith(".db3"):
                    # Ensure the relative path starts with the base folder name
                    rel_dir = os.path.join(rel_dir, name)
                    rel_dir = rel_dir[rel_dir.find(base_folder):]
                    files_and_folders.append(
                        {
                            "type": "file",
                            "name": rel_dir,
                        }  # Add base folder to the path
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
        # Fetch data using the existing helper function
        df = fetch_data_from_db(db_path, table_name)

        # Get column names
        columns = df.columns.tolist()
        date_type = None

        # Get time start and end if there is a date column
        if "Time" in columns:
            df["Time"] = pd.to_datetime(df["Time"])
            start_date = df["Time"].min().strftime("%Y-%m-%d")
            end_date = df["Time"].max().strftime("%Y-%m-%d")
            date_type = "Time"
        elif "Date" in columns:
            df["Date"] = pd.to_datetime(df["Date"])
            start_date = df["Date"].min().strftime("%Y-%m-%d")
            end_date = df["Date"].max().strftime("%Y-%m-%d")
            date_type = "Date"
        elif "Month" in columns:
            start_date = str(df["Month"].min())
            end_date = str(df["Month"].max())
            date_type = "Month"
        else:
            start_date = None
            end_date = None
            date_type = None

        # Get list of IDs if an ID column exists
        id_column = "".join([col for col in columns if "ID" in col])
        id_column = id_column if id_column != "" else None
        ids = df[id_column].unique().tolist() if id_column else []
        ids = [str(i) for i in ids]

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


# Helper function to save data to CSV or other formats
def save_to_file(dataframe, filename, file_format, export_path):
    """Save DataFrame to the specified file format."""
    file_path = os.path.join(export_path, filename)
    file_path = os.path.join(PATHFILE, file_path)
    if file_format == "csv":
        dataframe.to_csv(file_path, index=False)
    elif file_format == "text":
        dataframe.to_csv(file_path, index=False, sep=" ")
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
        if "Equal" not in method and date_type in ['Time', 'Date']:
            df, stats_df = aggregate_data(df, interval, method)
            df["Statistics"] = 'Data'
            df = df[["Statistics"] + columns]
            df = pd.concat([df, stats_df], axis=0)
            df.fillna({date_type:0}, inplace=True)
        # Calculate statistics if specified
        elif "None" not in statistics:
            stats_df = calculate_statistics(df, statistics)
            df["Statistics"] = 'Data'
            df = df[["Statistics"] + columns]
            df = pd.concat([df, stats_df], axis=0)
        # Return the processed data as JSON
        return jsonify(df.to_dict(orient="records"))

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
    statistics = data.get("statistics", ["None"])
    statistics = statistics.split(",") if statistics != ["None"] else statistics
    output_dest = data.get("export_path", "dataExport")
    output_name = data.get(
        "export_filename", f"exported_data_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    output_type = data.get("export_format", "csv")

    if not all([db_path, table_name]):
        return jsonify({"error": "Database path and table name are required."}), 400

    try:
        # Fetch and process data
        df = fetch_data_from_db(
            db_path, table_name, selected_id, columns, start_date, end_date, date_type
        )
        columns = columns.split(",") if columns != "All" else columns
        df = df.get(columns, df) if columns != "All" else df

        if "Equal" not in method and date_type in ['Time', 'Date']:
            df, stats_df = aggregate_data(df, interval, method)
            df["Statistics"] = 'Data'
            df = df[["Statistics"] + columns]
            df = pd.concat([df, stats_df], axis=0)
            df.fillna({date_type:0}, inplace=True)
        elif "None" not in statistics:
            stats_df = calculate_statistics(df, statistics)
            df["Statistics"] = 'Data'
            df = df[["Statistics"] + columns]
            df = pd.concat([df, stats_df], axis=0)

        # Save the processed data to file
        file_path = save_to_file(
            df, output_name + "." + output_type, output_type, output_dest
        )

        # Send the file to the client
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
