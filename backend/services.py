import sqlite3
import os
import pandas as pd
import numpy as np
from PIL import Image
import geopandas as gpd
import xlsxwriter
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator, LinearLocator
from cycler import cycler
from config import Config
from datetime import datetime
from flask import abort
import sys
import json
import threading
import pyogrio
from osgeo import ogr, osr, gdal

alias_mapping = {}
global_dbs_tables_columns = {}
lock = threading.Lock()
os.environ["PROJ_LIB"] = Config.PROJ_LIB
os.environ["GDAL_DATA"] = Config.GDAL_DATA


def fetch_data_service(data):
    """Fetch data and statistics from the specified databases and tables."""
    try:
        # Extract the required parameters from the request data
        db_tables = json.loads(data.get("db_tables"))
        columns = json.loads(data.get("columns", "All"))
        selected_ids = json.loads(data.get("id"))
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        date_type = data.get("date_type")
        interval = data.get("interval", "daily")
        method = json.loads(data.get("method", "[Equal]"))
        statistics = json.loads(data.get("statistics", "[None]"))
        stats_df = None

        # Initialize DataFrame to store the merged data
        df = pd.DataFrame()

        # Fetch the data for each database and table, and merge it based on date_type & 'ID'
        for table in db_tables:
            try:
                table_key = f'{(table["db"], table["table"])}'
                global_columns = global_dbs_tables_columns.get(table_key)
                ID = ["ID"] if global_columns and "ID" in global_columns else []
                duplicate_columns = []

                if not global_columns:
                    return {"error": f"No columns found for the table {table_key}"}

                # Determine which columns to fetch
                if columns == "All":
                    # Fetch all columns for the table
                    fetch_columns = columns
                else:
                    fetch_columns = set()
                    prefix_columns = [
                        col for col in columns if col.startswith(table["table"])
                    ]

                    for col in columns:
                        if col in prefix_columns:
                            original_col = col[
                                len(table["table"]) + 1 :
                            ]  # Strip prefix
                            if original_col in global_columns:
                                fetch_columns.add(original_col)
                                duplicate_columns.append(col)
                        elif col in global_columns:
                            # Non-prefixed columns for tables without prefixes
                            fetch_columns.add(col)

                # Remove fetched columns from columns list
                columns = list(set(columns) - set(fetch_columns)) + [date_type] + ID

                if not fetch_columns:
                    # If there are no common columns, skip the table
                    continue

                # Fetch data from the database
                df_temp = fetch_data_from_db(
                    table["db"],
                    table["table"],
                    selected_ids,
                    fetch_columns,
                    start_date,
                    end_date,
                    date_type,
                )

                # Rename columns to table-column format
                for col in duplicate_columns:
                    col_temp = col[len(table["table"]) + 1 :]
                    if col_temp in df_temp.columns:
                        df_temp.rename(columns={col_temp: col}, inplace=True)

                # Merge the dataframes on date_type and 'ID' columns
                if df.empty:
                    df = df_temp
                else:
                    # Identify columns for merging; ignore columns with dash if they represent different data sources
                    merge_on_columns = [col for col in df.columns if "ID" in col]
                    for col in df.columns:
                        if col in df_temp.columns and not col.startswith(
                            table["table"]
                        ):
                            merge_on_columns.append(col)
                    df = pd.merge(df, df_temp, on=merge_on_columns, how="outer")
                    # Drop rows with NaN in the required columns
                    df.dropna(inplace=True)
            except Exception as e:
                return {"error": f"Error while processing table {table_key}: {str(e)}"}

        # If the DataFrame is empty after merging, return an error
        if df.empty:
            return {"error": "No data found for the specified filters."}

        # Perform time conversion and aggregation if necessary
        if "Equal" not in method and interval != "daily":
            if not date_type:
                return {
                    "error": "Time conversion and statistics cannot be performed for non-time series data"
                }
            df, stats_df = aggregate_data(df, interval, method, date_type)
        elif "None" not in statistics:
            if not date_type:
                return {
                    "error": "Time conversion and statistics cannot be performed for non-time series data"
                }
            stats_df = calculate_statistics(df, statistics, date_type)

        # Return the data and statistics as dictionaries
        return {
            "data": df.to_dict(orient="records"),
            "stats": stats_df.to_dict(orient="records") if stats_df is not None else [],
            "statsColumns": stats_df.columns.tolist() if stats_df is not None else [],
        }
    except Exception as e:
        return {"error": str(e)}


def export_data_service(data):
    """Export data and statistics to a file in the specified format."""
    try:
        # Fetch the data and statistics from the fetch_data_service
        output = fetch_data_service(data)
        if output.get("error", None):
            return output
        df = pd.DataFrame(output["data"])
        stats_df = (
            pd.DataFrame(output["stats"]) if output.get("statsColumns", None) else None
        )

        # Extract the required parameters from the request data
        output_filename = data.get(
            "export_filename",
            f"exported_data_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        output_format = data.get("export_format", "csv")
        output_path = data.get("export_path", "dataExport")
        # Handle options json stringify
        options = json.loads(data.get("options", '{"data": true, "stats": true}'))
        columns_list = json.loads(data.get("columns", "All"))
        date_type = data.get("date_type")
        graph_type = data.get("graph_type", "scatter")

        # Parse multi_graph_type
        multi_graph_type = json.loads(data.get("multi_graph_type", "[]"))

        if not multi_graph_type:
            multi_graph_type = [
                {"type": graph_type, "name": column}
                for column in columns_list
                if not column.endswith("ID") and column != date_type
            ]

        if not date_type:
            return {
                "error": "Graph creation cannot be performed for non-time series data"
            }

        # Save the data and statistics to the specified file format
        # Perform graph creation if the output format is an image or excel format
        file_path = save_to_file(
            df,
            stats_df,
            f"{output_filename}.{output_format}",
            output_format,
            output_path,
            options,
            date_type,
            multi_graph_type,
            list(map(int, json.loads(data.get("id")))) if data.get("id") != [] else [],
        )

        return {"file_path": file_path}
    except Exception as e:
        return {"error": str(e)}


def fetch_data_from_db(
    db_path, table_name, selected_ids, columns, start_date, end_date, date_type
):
    """Fetch data from a SQLite database table with real-to-alias mapping."""
    conn = sqlite3.connect(os.path.join(Config.PATHFILE, db_path))

    # table_name is an alias so replace it with the real table name
    real_table_name = alias_mapping.get(table_name, {}).get("real", table_name)

    # If specific columns are selected, map them to the real columns
    if columns != "All":
        columns_list = columns
        real_columns = [
            alias_mapping.get(table_name, {}).get("columns", {}).get(col, col)
            for col in columns_list
        ]
        columns = ",".join(real_columns)

    # Start building the base query using real table name
    query = f"SELECT {columns if columns != 'All' else '*'} FROM {real_table_name}"
    params = []

    # Add conditions for selected_ids
    if selected_ids != []:
        placeholders = ",".join(["?"] * len(selected_ids))
        query += f" WHERE ID IN ({placeholders})"
        params.extend(selected_ids)

    # Add date range conditions
    if start_date and end_date:
        if selected_ids != []:
            query += f" AND {date_type} BETWEEN ? AND ?"
        else:
            query += f" WHERE {date_type} BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    # Execute the query with parameters
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Map real column names back to alias if needed
    alias_columns = [
        (
            alias_mapping.get(real_table_name, {}).get("columns", {}).get(col, col)
            if "ID" not in col
            else col
        )
        for col in df.columns
    ]
    df.columns = alias_columns

    return df.map(round_numeric_values)


# Helper function to save data to CSV or text formats
def save_to_file(
    dataframe1,
    dataframe2,
    filename,
    file_format,
    export_path,
    options,
    date_type,
    multi_graph_type,
    selected_ids=[],
):
    """Save two DataFrames to the specified file format sequentially."""
    # Set the file path
    file_path = (
        os.path.join(Config.PATHFILE_EXPORT, export_path)
        if not os.path.isabs(export_path)
        else export_path
    )

    os.makedirs(file_path, exist_ok=True)
    file_path = os.path.join(file_path, filename)

    # Map graph types to Matplotlib Axes methods
    GRAPH_TYPE_MAPPING = {
        "line": "plot",
        "bar": "column",
        "scatter": "scatter",
    }

    # Check if the dataframe contains an ID column
    ID = next((col for col in dataframe1.columns if "ID" in col), None)
    dataframe1[date_type] = pd.to_datetime(dataframe1[date_type])

    # Keep track of which axis (primary or secondary) to use for each column
    primary_axis_columns = []
    secondary_axis_columns = []

    # Classify columns based on their value ranges (example threshold: >100 for secondary y-axis)
    for column in dataframe1.columns[1:]:
        if dataframe1[column].max() > 100:
            secondary_axis_columns.append(column)
        else:
            primary_axis_columns.append(column)

    # Write first dataframe and/or statistics dataframe to file with csv/text format
    if file_format == "csv":
        with open(file_path, "w", newline="") as f:
            if options["table"]:
                dataframe1.to_csv(f, index=False)
            if options["stats"] and dataframe2 is not None:
                f.write("\n")
                dataframe2.to_csv(f, index=False)
    elif file_format == "txt":
        with open(file_path, "w") as f:
            if options["table"]:
                dataframe1.to_csv(f, index=False, sep=" ")
            if options["stats"] and dataframe2 is not None:
                f.write("\n")
                dataframe2.to_csv(f, index=False, sep=" ")
    elif file_format == "xlsx":
        # Write the DataFrame to an Excel file
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            # Sort dataframe by ID column for consistent selection
            dataframe1 = dataframe1.sort_values([ID])
            # Write the DataFrame to Excel
            dataframe1.to_excel(writer, sheet_name="Sheet1", index=False)

            # Access the workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]

            # Initialize the chart object
            chart = None

            # Define chart type and add data for the chart
            for i, column_graph in enumerate(multi_graph_type, start=1):
                multi_graph_type_same = (
                    i > 1 and multi_graph_type[i - 2]["type"] == column_graph["type"]
                )
                overlay_chart = (
                    chart
                    if multi_graph_type_same
                    else workbook.add_chart(
                        {"type": GRAPH_TYPE_MAPPING[column_graph["type"]]}
                    )
                )
                column = column_graph["name"]
                row_count = len(dataframe1) + 1

                if selected_ids and selected_ids != []:
                    prev_end_row = 1  # Start from the first data row

                    for j, selected_id in enumerate(selected_ids):
                        # Calculate the start and end rows for the current ID
                        start_row = prev_end_row + 1
                        end_row = (
                            start_row
                            + len(dataframe1[dataframe1[ID] == selected_id])
                            - 1
                        )

                        # Add a series to the overlay chart
                        overlay_chart.add_series(
                            {
                                "name": f"{column} - {ID}: {selected_id}",
                                "categories": f"Sheet1!$A${start_row}:$A${end_row}",  # Assuming column A contains categories
                                "values": f"Sheet1!${chr(65 + i + 1)}${start_row}:${chr(65 + i + 1)}${end_row}",
                                "y2_axis": column
                                in secondary_axis_columns,  # Assign to secondary y-axis if applicable
                            }
                        )

                        # Update previous end row
                        prev_end_row = end_row

                else:
                    # Add a single series for each selected column when selected_ids is empty
                    overlay_chart.add_series(
                        {
                            "name": column,
                            "categories": f"Sheet1!$A$2:$A${row_count}",
                            "values": f"Sheet1!${chr(65 + i)}$2:${chr(65 + i)}${row_count}",
                            "y2_axis": column in secondary_axis_columns,
                        }
                    )
                if chart is None or multi_graph_type_same:
                    chart = overlay_chart
                else:
                    chart.combine(overlay_chart)
            # Customize the chart
            chart.set_x_axis(
                {
                    "name": date_type,
                    "date_axis": True,
                    "num_format": "yyyy-mm-dd",
                    "major_gridlines": {"visible": True},
                    "num_font": {"rotation": -45},
                }
            )
            chart.set_y_axis({"name": "Values (Smaller Values)"})
            chart.set_y2_axis({"name": "Values (Larger Values)"})  # Add second y-axis

            # Insert the chart into the worksheet
            worksheet.insert_chart(f"{chr(65 + len(dataframe1.columns))}2", chart)
            workbook.close()
    elif file_format in ["png", "jpg", "jpeg", "svg", "pdf"]:
        # Plot each column as a line on the same figure
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()  # Create a secondary y-axis
        # Setting color cycles
        ax1.set_prop_cycle(cycler(color=plt.cm.tab10.colors))
        # Check if ax2 will have plots
        ax2_has_data = any(
            column_graph["name"] not in primary_axis_columns
            for column_graph in multi_graph_type
        )
        if ax2_has_data:
            ax2.set_prop_cycle(cycler(color=plt.cm.Set2.colors))

        for i, column_graph in enumerate(multi_graph_type):
            column = column_graph["name"]
            plot_func = getattr(
                ax1 if column in primary_axis_columns else ax2,
                GRAPH_TYPE_MAPPING[column_graph["type"]],
            )

            if selected_ids and selected_ids != []:
                # Create separate plots for each ID-Column combination
                for j, selected_id in enumerate(selected_ids):
                    filtered_data = dataframe1[dataframe1[ID] == selected_id]
                    plot_func(
                        (
                            filtered_data[date_type] + pd.DateOffset((i + j) * 2)
                            if column_graph["type"] == "bar"
                            else filtered_data[date_type]
                        ),
                        filtered_data[column],
                        label=f"{column} - {ID}: {selected_id}",
                        alpha=0.7,
                    )
            else:
                # Plot each column as a single series if selected_ids is empty
                plot_func(
                    (
                        dataframe1[date_type] + pd.DateOffset(i * 2)
                        if column_graph["type"] == "bar"
                        else dataframe1[date_type]
                    ),
                    dataframe1[column],
                    label=column,
                    alpha=0.7,
                )

        # Customize axes
        ax1.set_xlabel(date_type)
        ax1.set_ylabel("Values (Smaller Values)")
        ax1.xaxis.set_major_locator(MaxNLocator(nbins=30))  # Scale x&y-axis ticks
        ax1.yaxis.set_major_locator(LinearLocator(numticks=8))
        ax1.grid(visible=True, linestyle="--", alpha=0.6)

        if ax2_has_data:
            ax2.set_ylabel("Values (Larger Values)")
            ax2.xaxis.set_major_locator(
                MaxNLocator(nbins=30)
            )  # Ensure same number of x&y-axis ticks on both axes
            ax2.yaxis.set_major_locator(LinearLocator(numticks=8))
            ax2.grid(visible=True, linestyle="--", alpha=0.6)

        ax1.legend(loc="upper left")
        if ax2_has_data:
            ax2.legend(loc="upper right")

        # Rotate x-axis labels (explicitly for ax1 and ax2 if shared x-axis is used)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)

        # Adjust layout to avoid label overlap
        plt.tight_layout()

        # Save the plot
        plt.savefig(file_path, format=file_format)

    return file_path


def get_table_names(data):
    """
    Get the names of all tables in a SQLite database.
    """
    try:
        db_path = data.get("db_path")
        conn = sqlite3.connect(os.path.join(Config.PATHFILE, db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        # Map real table names to alias names
        alias_tables = [
            alias_mapping.get(table[0], {}).get("alias", table[0]) for table in tables
        ]
        return {"tables": alias_tables}
    except Exception as e:
        return {"error": str(e)}


def get_files_and_folders(data):
    """
    Construct a tree of folders and files within a given folder path.
    """

    folder_tree = set()
    folder_path = data.get("folder_path", "Jenette_Creek_Watershed")

    if os.path.isabs(folder_path):
        # Update Config.PATHFILE to point to the parent directory of the provided absolute path
        Config.PATHFILE = os.path.dirname(folder_path)
        base_folder = os.path.basename(folder_path)
        root = Config.PATHFILE
    else:
        # If the folder path is relative, use it directly
        base_folder = folder_path
        # Determine the base path of the application
        base_path = (
            (
                sys._MEIPASS  # When the application is packaged with PyInstaller
                if getattr(sys, "frozen", False)
                else os.path.dirname(__file__)
            )
            if folder_path == "Jenette_Creek_Watershed"
            else folder_path
        )
        # Construct the absolute folder path relative to the current file location
        folder_path = os.path.join(base_path, folder_path)
        root = os.path.abspath(base_folder)

    try:
        files_and_folders = []
        lookup_found = False

        for dirpath, dirs, files in os.walk(folder_path):
            # Construct the relative path from the base folder
            rel_dir = os.path.relpath(dirpath, root)

            # Append directories
            for fdir in dirs:
                dir_rel_path = os.path.join(rel_dir, fdir)
                # Ensure the relative path starts with the base folder name
                dir_rel_path = dir_rel_path[dir_rel_path.find(base_folder) :]
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
                file_rel_path = file_rel_path[file_rel_path.find(base_folder) :]

                # Only include .shp, .db3, and .tif files
                if file_rel_path.endswith((".shp", ".db3", ".tif")):
                    if file_rel_path.endswith(".db3") and "lookup" not in file_rel_path:
                        folder_tree.add(os.path.join(Config.PATHFILE, file_rel_path))
                    elif file_rel_path.endswith(".db3") and "lookup" in file_rel_path:
                        Config.LOOKUP = file_rel_path
                        lookup_found = True
                    files_and_folders.append(
                        {
                            "type": (
                                "database" if file_rel_path.endswith(".db3") else "file"
                            ),
                            "name": file_rel_path,
                        }
                    )
        # Load alias mapping for each database
        (
            alias_mapping.update(load_alias_mapping(folder_tree))
            if not alias_mapping and lookup_found
            else None
        )

        return {"files_and_folders": files_and_folders}
    except Exception as e:
        return {"error": str(e)}


# Example function to map date strings to seasons
def get_season_from_date(date_str):
    """Map date strings to seasons."""
    month = date_str.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"


# Helper function to apply time interval aggregation
def aggregate_data(df, interval, method, date_type):
    """Aggregate data based on the specified interval and method."""
    # Convert the date_type column to datetime
    df[date_type] = pd.to_datetime(df[date_type])
    df.set_index(date_type, inplace=True)
    resampled_df = None
    ID = next((col for col in df.columns if "ID" in col), None)
    # Resample the data based on the specified interval
    if interval == "monthly":
        resampled_df = df.groupby(ID).resample("ME").first()
    elif interval == "seasonally":
        # Custom resampling for seasons
        df.reset_index(inplace=True)
        df["Season"] = df[date_type].apply(lambda x: get_season_from_date(x))
        df.set_index(date_type, inplace=True)
        resampled_df = df
    elif interval == "yearly":
        resampled_df = df.groupby(ID).resample("YE").first()
    else:
        resampled_df = df

    # Drop the ID column if it exists
    resampled_df = (
        resampled_df.drop(columns=[ID])
        if ID in resampled_df.index.names
        else resampled_df
    )
    resampled_df.reset_index(inplace=True)

    # Format the date column based on the interval
    if interval != "seasonally":
        resampled_df[date_type] = (
            resampled_df[date_type].dt.strftime("%Y-%m")
            if interval == "monthly"
            else resampled_df[date_type].dt.strftime("%Y")
        )
    else:
        resampled_df[date_type] = resampled_df[date_type].dt.strftime("%Y-%m-%d")
    stats_df = calculate_statistics(resampled_df, method, date_type)

    return resampled_df, stats_df.map(round_numeric_values)


def round_numeric_values(value):
    """Round numeric values to 3 decimal places."""
    if isinstance(value, (float, int)):  # Check if the value is a number
        return round(value, 3)  # Round to 3 decimal places
    return value  # Leave non-numeric values unchanged


def calculate_statistics(df, statistics, date_type):
    """Calculate specified statistics for numerical data in the DataFrame."""
    stats_df = pd.DataFrame()

    # Store the original DataFrame with all columns
    original_df = df.copy()

    # Select only numerical columns for calculations
    df = df.select_dtypes(include=["number"])
    # Drop the date_type column if it exists
    df = df.drop(columns=[date_type], errors="ignore")

    if "Average" in statistics:
        stats_df["Average"] = df.mean()
    if "Sum" in statistics:
        stats_df["Sum"] = df.sum()
    if "Maximum" in statistics:
        stats_df["Maximum"] = df.max()
        # Use original DataFrame to get the corresponding date_type values for maximums
        # Ignore if date_type is not present in the original DataFrame
        max_date_type = {
            col: original_df.loc[original_df[col].idxmax(), date_type]
            for col in df.columns
            if date_type in original_df.columns
        }
        stats_df[f"Maximum {date_type}"] = pd.Series(max_date_type)
    if "Minimum" in statistics:
        stats_df["Minimum"] = df.min()
        # Use original DataFrame to get the corresponding date_type values for minimums
        # Ignore if date_type is not present in the original DataFrame
        min_date_type = {
            col: original_df.loc[original_df[col].idxmin(), date_type]
            for col in df.columns
            if date_type in original_df.columns
        }
        stats_df[f"Minimum {date_type}"] = pd.Series(min_date_type)
    if "Standard Deviation" in statistics:
        stats_df["Standard Deviation"] = df.std()

    # Transpose and format DataFrame
    stats_df = stats_df.T
    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"index": "Statistics"}, inplace=True)

    return stats_df.map(round_numeric_values)


def load_alias_mapping(folder_tree):
    """Load alias mapping from the lookup.db3 database."""
    conn = sqlite3.connect(os.path.join(Config.PATHFILE, Config.LOOKUP))
    alias_map = {}

    # Query the alias tables (Hydroclimate, BMP, scenario_2)
    for table in folder_tree:
        # Extract the table name from the path
        table = os.path.basename(table).replace(".db3", "")

        query = f"SELECT * FROM {table}"
        df = pd.read_sql_query(query, conn)

        for _, row in df.iterrows():
            real_table = row["Table Name"]
            alias_table = row["Table Alias"]
            real_column = row["Column Name"]
            alias_column = row["Column Alias"]

            # Map real-to-alias and alias-to-real for both tables and columns
            alias_map.setdefault(real_table, {}).setdefault("alias", alias_table)
            alias_map[real_table].setdefault("columns", {})[real_column] = alias_column
            alias_map.setdefault(alias_table, {}).setdefault("real", real_table)
            alias_map[alias_table].setdefault("columns", {})[alias_column] = real_column

    conn.close()
    return alias_map


def get_columns_and_time_range(db_path, table_name):
    """Fetch column names and time range from a SQLite database table with real-to-alias mapping."""

    try:
        # Convert the table alias to its real name if necessary
        real_table_name = alias_mapping.get(table_name, {}).get("real", table_name)

        # Connect to the database
        conn = sqlite3.connect(os.path.join(Config.PATHFILE, db_path))

        # Fetch column information using PRAGMA for the real table name
        query = f"PRAGMA table_info('{real_table_name}')"
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [row[1] for row in cursor.fetchall()]

        # Convert real column names to alias names (if available in the mapping)
        alias_columns = [
            alias_mapping.get(real_table_name, {}).get("columns", {}).get(col, col)
            for col in columns
        ]

        # Initialize variables
        start_date = end_date = date_type = interval = None

        # Check and query for specific date/time columns (using real column names)
        for date_col, dtype, inter in [
            ("Time", "Time", "daily"),
            ("Date", "Time", "daily"),
            ("Month", "Month", "monthly"),
            ("Year", "Year", "yearly"),
        ]:
            if date_col in columns:
                df = pd.read_sql_query(
                    f"SELECT {date_col} FROM {real_table_name}", conn
                )
                if date_col in ["Time", "Date"]:
                    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                    start_date = df[date_col].min().strftime("%Y-%m-%d")
                    end_date = df[date_col].max().strftime("%Y-%m-%d")
                elif date_col in ["Month", "Year"]:
                    start_date = int(df[date_col].min())
                    end_date = int(df[date_col].max())
                date_type = dtype
                interval = inter
                break

        # Get list of IDs if an ID column exists, without querying unnecessary data
        id_column = next((col for col in columns if "ID" in col), None)
        ids = []
        if id_column:
            id_query = f"SELECT DISTINCT {id_column} FROM {real_table_name}"
            id_df = pd.read_sql_query(id_query, conn)
            ids = id_df[id_column].tolist()

        # Close the connection
        conn.close()

        # Return alias column names instead of real ones
        return {
            "columns": alias_columns,
            "start_date": start_date,
            "end_date": end_date,
            "ids": ids,
            "date_type": date_type,
            "interval": interval,
        }
    except Exception as e:
        return {"error": str(e)}


def get_multi_columns_and_time_range(data):
    """Fetch column names and time range from multiple SQLite database tables."""
    try:
        db_tables = json.loads(data.get("db_tables"))
        multi_columns_time_range = []
        all_columns = set()

        for table in db_tables:
            table_key = f'{(table["db"], table["table"])}'

            columns_time_range = get_columns_and_time_range(table["db"], table["table"])

            if columns_time_range.get("error"):
                return columns_time_range

            # Rename columns if they are duplicates by prefixing with the table name and a dash
            prefixed_columns = [
                (
                    f"{table['table']}-{col}"
                    if col in all_columns
                    and col != columns_time_range["date_type"]
                    and "ID" not in col
                    else col
                )
                for col in columns_time_range["columns"]
            ]

            all_columns.update(columns_time_range["columns"])

            global_dbs_tables_columns[table_key] = (
                columns_time_range["columns"] + ["ID"]
                if columns_time_range["ids"] != []
                else columns_time_range["columns"]
            )

            multi_columns_time_range.append(
                {**columns_time_range, "columns": prefixed_columns}
            )

        # Verify each entry in global_dbs_tables_columns against db_tables
        existing_keys = {f'{(table["db"], table["table"])}' for table in db_tables}

        keys_to_delete = [
            key for key in global_dbs_tables_columns.keys() if key not in existing_keys
        ]
        # Delete keys that do not exist in db_tables
        for key in keys_to_delete:
            del global_dbs_tables_columns[key]

        # Check consistency across tables for date_type, interval, start_date, end_date, and ids
        keys_to_check = ["date_type", "interval"]
        for key in keys_to_check:
            unique_values = set(table[key] for table in multi_columns_time_range)
            if len(unique_values) > 1:
                return {"error": f"Tables have different {key.replace('_', ' ')}"}

        # Intersection of start and end dates from all tables
        start_dates = [table["start_date"] for table in multi_columns_time_range]
        end_dates = [table["end_date"] for table in multi_columns_time_range]
        start_date = max(start_dates)
        end_date = min(end_dates)

        # Combine all columns with date_type as first column
        columns = [multi_columns_time_range[0]["date_type"]]

        # Check if ID column is present in any of the tables
        include_id = any(
            table.get("ids", []) != [] for table in multi_columns_time_range
        )

        if include_id:
            columns.append("ID")

        # Add all other columns from each table
        columns += [
            col
            for table in multi_columns_time_range
            for col in table["columns"]
            if col
            not in [
                multi_columns_time_range[0]["date_type"],
                "ID",
            ]
            and "ID" not in col
        ]

        # Intersection of IDs from all tables
        ids = set(multi_columns_time_range[0]["ids"]).intersection(
            *[set(table["ids"]) for table in multi_columns_time_range]
        )

        return {
            "columns": columns,
            "global_columns": global_dbs_tables_columns,
            "start_date": start_date,
            "end_date": end_date,
            "ids": [str(id) for id in sorted(ids)],
            "date_type": multi_columns_time_range[0]["date_type"],
            "interval": multi_columns_time_range[0]["interval"],
        }
    except Exception as e:
        return {"error": str(e)}


def round_coordinates(geojson_data, decimal_points=4):
    """
    Recursively round all coordinates in the GeoJSON to a specified number of decimal points.
    """

    def round_coords(coords):
        if isinstance(coords[0], list):
            # If the first element is a list, recurse (for MultiPolygon, Polygon, etc.)
            return [round_coords(c) for c in coords]
        else:
            # Otherwise, round the coordinates (for Point, etc.)
            return [round(coord, decimal_points) for coord in coords]

    if isinstance(geojson_data, str):
        geojson_data = json.loads(geojson_data)

    for feature in geojson_data.get("features", []):
        geometry = feature.get("geometry", {})
        if "coordinates" in geometry:
            geometry["coordinates"] = round_coords(geometry["coordinates"])

    return geojson_data


def bounds_overlap_or_similar(bounds1, bounds2, tolerance=0.0001):
    """
    Check if two bounds are overlapping, contained, or in the same location.
    If similar, return the larger bound; if far apart, return the first bound.
    """

    if not bounds1:
        return True, bounds2

    # Unpack bounds
    minY1, minX1 = bounds1[0]
    maxY1, maxX1 = bounds1[1]
    minY2, minX2 = bounds2[0]
    maxY2, maxX2 = bounds2[1]

    # Adjust for tolerance
    minY1 -= tolerance
    minX1 -= tolerance
    maxY1 += tolerance
    maxX1 += tolerance

    minY2 -= tolerance
    minX2 -= tolerance
    maxY2 += tolerance
    maxX2 += tolerance

    # Check for overlap (intersection)
    horizontal_overlap = not (maxX1 < minX2 or maxX2 < minX1)
    vertical_overlap = not (maxY1 < minY2 or maxY2 < minY1)

    if horizontal_overlap and vertical_overlap:
        # Merge to create a larger bounding box
        merged_bounds = [
            [min(minY1, minY2), min(minX1, minX2)],
            [max(maxY1, maxY2), max(maxX1, maxX2)],
        ]
        return True, merged_bounds  # Overlapping bounds merged

    # Check for containment (one inside another)
    is_contained = (
        minX1 >= minX2 and maxX1 <= maxX2 and minY1 >= minY2 and maxY1 <= maxY2
    ) or (minX2 >= minX1 and maxX2 <= maxX1 and minY2 >= minY1 and maxY2 <= maxY1)

    if is_contained:
        # Return the larger bound
        area1 = (maxX1 - minX1) * (maxY1 - minY1)
        area2 = (maxX2 - minX2) * (maxY2 - minY2)
        return True, bounds1 if area1 >= area2 else bounds2

    # Check if centers are very close (proximity)
    center1 = [(minX1 + maxX1) / 2, (minY1 + maxY1) / 2]
    center2 = [(minX2 + maxX2) / 2, (minY2 + maxY2) / 2]

    center_distance = (
        (center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2
    ) ** 0.5

    if center_distance < tolerance:
        # Merge if centers are close
        merged_bounds = [
            [min(minY1, minY2), min(minX1, minX2)],
            [max(maxY1, maxY2), max(maxX1, maxX2)],
        ]
        return True, merged_bounds

    # If completely far apart, return the first bound
    return False, bounds1


def get_raster_normalized(band):
    """
    Normalize a raster band by computing the min and max values while ignoring NoData values.
    """
    # Read raster data as a NumPy array
    raster_data = band.ReadAsArray()

    # Get the NoData value
    no_data_value = band.GetNoDataValue()

    # Mask NoData values if present
    if no_data_value is not None:
        raster_data = np.ma.masked_equal(raster_data, no_data_value)

    # Compute min and max while ignoring NoData
    raster_min = (
        np.min(raster_data) if np.ma.is_masked(raster_data) else np.nanmin(raster_data)
    )
    raster_max = (
        np.max(raster_data) if np.ma.is_masked(raster_data) else np.nanmax(raster_data)
    )

    # Normalize the raster while avoiding division by zero
    if raster_max - raster_min == 0:
        raster_normalized = np.zeros_like(
            raster_data
        )  # If constant values, return all zeros
    else:
        raster_normalized = (raster_data - raster_min) / (raster_max - raster_min)

    return raster_data, raster_normalized, raster_min, raster_max


def get_raster_color_levels(band, colormap, num_classes=5):
    """
    Generate color levels for a raster band, using its native color mapping.
    """
    _, _, min_value, max_value = get_raster_normalized(band)

    if min_value == max_value:
        return []  # Avoid division by zero for constant rasters

    # Define classification breakpoints
    levels = np.linspace(min_value, max_value, num_classes + 1)

    # Get color values from the colormap
    cmap = plt.get_cmap(colormap, num_classes)
    colors = [mcolors.to_hex(cmap(i / (num_classes - 1))) for i in range(num_classes)]

    # Create the color level mapping
    color_levels = [
        {
            "min": round(levels[i].item(), 2),
            "max": round(levels[i + 1].item(), 2),
            "color": colors[i],
        }
        for i in range(num_classes)
    ]

    return color_levels


def get_metadata_colormap(band):
    """
    Determine an appropriate colormap based on raster metadata.
    """
    metadata = band.GetMetadata()
    colormap_name = metadata.get("COLOR_MAP", "gray")  # Default to "gray" if missing

    if colormap_name not in plt.colormaps():
        colormap_name = "gray"  # Fallback to terrain if unknown

    return plt.get_cmap(colormap_name)


def get_geojson_metadata(geojson_path):
    """Extract metadata from an existing GeoJSON file."""
    if not os.path.exists(geojson_path):
        return None

    with open(geojson_path, "r") as file:
        geojson_data = json.load(file)

    features = geojson_data.get("features", [])
    feature_count = len(features)

    x_min = y_min = float("inf")
    x_max = y_max = float("-inf")

    field_names = []

    for feature in features:
        geom = feature.get("geometry", {})
        props = feature.get("properties", {})

        # Update bounding box
        bbox = feature.get("bbox", [])
        if bbox:
            x_min = min(x_min, bbox[0])
            y_min = min(y_min, bbox[1])
            x_max = max(x_max, bbox[2])
            y_max = max(y_max, bbox[3])

        # Collect property field names
        field_names.extend(list(props.keys()))

    return {
        "feature_count": feature_count,
        "extent": (round(x_min, 6), round(x_max, 6), round(y_min, 6), round(y_max, 6)),
        "field_names": list(dict.fromkeys(field_names)),
    }


def process_geospatial_data(data):
    """
    Process a geospatial file (shapefile or raster) and return GeoJSON/Tiff Image Url, bounds, and center.
    """

    file_paths = map(
        lambda x: os.path.join(Config.PATHFILE, x), json.loads(data.get("file_paths"))
    )
    combined_geojson = {}
    combined_bounds = None
    raster_color_levels = []
    combined_properties = []
    tool_tip = {}
    image_urls = []

    for file_path in file_paths:
        toolTipKey = f"{(os.path.basename(file_path),os.path.basename(file_path))}"
        # Check if the file is a shapefile (.shp)
        if file_path.endswith(".shp"):
            # Open shapefile
            driver = ogr.GetDriverByName("ESRI Shapefile")
            dataset = driver.Open(file_path, 0)
            if dataset is None:
                continue

            layer = dataset.GetLayer()

            # Handle Spatial Reference System
            source_srs = layer.GetSpatialRef()
            if not source_srs:
                source_srs = osr.SpatialReference()
                source_srs.ImportFromEPSG(26917)  # Default UTM Zone 17N if unspecified

            target_srs = osr.SpatialReference()
            target_srs.ImportFromEPSG(4326)  # WGS84 (longitude/latitude)

            # Ensure the axis order is longitude-latitude
            if target_srs.SetAxisMappingStrategy:
                target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

            coord_transform = osr.CoordinateTransformation(source_srs, target_srs)

            # Create a new memory layer for the reprojected data
            memory_driver = ogr.GetDriverByName("Memory")
            memory_ds = memory_driver.CreateDataSource("reprojected")
            reprojected_layer = memory_ds.CreateLayer(
                "reprojected_layer", srs=target_srs, geom_type=layer.GetGeomType()
            )

            # Copy fields from the original layer
            layer_defn = layer.GetLayerDefn()
            for i in range(layer_defn.GetFieldCount()):
                reprojected_layer.CreateField(layer_defn.GetFieldDefn(i))

            # Collect properties dynamically
            properties = [
                layer_defn.GetFieldDefn(i).GetName()
                for i in range(layer_defn.GetFieldCount())
            ]

            # Reproject features in batches if needed
            feature_buffer = []
            BATCH_SIZE = 1000
            for feature in layer:
                geom = feature.GetGeometryRef()
                if geom:
                    geom.Transform(coord_transform)  # Transform geometry to WGS84

                # Create a new feature and store in buffer
                reprojected_feature = ogr.Feature(reprojected_layer.GetLayerDefn())
                reprojected_feature.SetGeometry(geom)
                for i in range(feature.GetFieldCount()):
                    reprojected_feature.SetField(i, feature.GetField(i))

                feature_buffer.append(reprojected_feature)

                # Bulk insert when buffer reaches batch size
                if len(feature_buffer) >= BATCH_SIZE:
                    reprojected_layer.StartTransaction()
                    for f in feature_buffer:
                        reprojected_layer.CreateFeature(f)
                    reprojected_layer.CommitTransaction()
                    feature_buffer.clear()

            # Insert remaining features
            if feature_buffer:
                reprojected_layer.StartTransaction()
                for f in feature_buffer:
                    reprojected_layer.CreateFeature(f)
                reprojected_layer.CommitTransaction()

            # Calculate bounds in WGS84
            extent = reprojected_layer.GetExtent()  # (minX, maxX, minY, maxY)

            x_min = extent[0]
            y_min = extent[2]
            x_max = extent[1]
            y_max = extent[3]

            # Swap longitude & latitude order for Leaflet (Leaflet expects [[minY, minX], [maxY, maxX]])
            bounds = [
                [y_min, x_min],
                [y_max, x_max],
            ]

            shp_metadata = {
                "feature_count": reprojected_layer.GetFeatureCount(),
                "extent": (round(x_min, 6), round(x_max, 6), round(y_min, 6), round(y_max, 6)),
                "field_names": properties,
            }
            geojson_metadata = {}
            geojson_path = os.path.splitext(file_path)[0] + "_output.geojson"

            # Check if a GeoJSON file already exists and extract metadata
            if os.path.exists(geojson_path):
                geojson_metadata = get_geojson_metadata(geojson_path)

            if shp_metadata != geojson_metadata:
                # Convert reprojected layer to GeoJSON
                geojson_driver = ogr.GetDriverByName("GeoJSON")

                geojson_dataset = geojson_driver.CreateDataSource(geojson_path)
                geojson_dataset.CopyLayer(
                    reprojected_layer,
                    "layer",
                    ["RFC7946=YES", "WRITE_BBOX=YES"],
                )
                geojson_dataset = None

            with open(geojson_path, "r") as file:
                geojson_data = json.load(file)

            # Update the combined bounds
            (overlap, combined_bounds) = bounds_overlap_or_similar(
                combined_bounds, bounds
            )

            # Add GeoJSON data/properties to the combined GeoJSON/properties only if the combined bounds are not far apart
            if overlap:
                if combined_geojson:

                    def append_features(geojson_data):
                        """Efficiently append features to GeoJSON."""
                        for feature in geojson_data["features"]:
                            yield feature

                    # Append features to the combined GeoJSON using generator
                    for feature in append_features(geojson_data):
                        combined_geojson["features"].append(feature)
                else:
                    combined_geojson = geojson_data
                if combined_properties:
                    combined_properties.extend(properties)
                else:
                    combined_properties = properties

            # Save properties for each shapefile path
            tool_tip[toolTipKey] = properties
        # Handle GeoTIFF files
        elif file_path.endswith(".tif"):
            raster_dataset = gdal.Open(file_path)
            if not raster_dataset:
                continue

            # Ensure raster is in EPSG:4326 (WGS84)
            source_srs = osr.SpatialReference()
            source_srs.ImportFromWkt(raster_dataset.GetProjection())
            target_srs = osr.SpatialReference()
            target_srs.ImportFromEPSG(4326)

            # Ensure the axis order is longitude-latitude
            if target_srs.SetAxisMappingStrategy:
                target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

            if not source_srs.IsSame(target_srs):
                # Reproject the raster to EPSG:4326
                reprojected_file_path = (
                    os.path.splitext(file_path)[0] + "_reprojected.tif"
                )
                gdal.Warp(reprojected_file_path, raster_dataset, dstSRS="EPSG:4326")
                raster_dataset = gdal.Open(reprojected_file_path)
            else:
                reprojected_file_path = file_path

            # Get raster metadata
            geotransform = raster_dataset.GetGeoTransform()

            x_min = geotransform[0]
            y_max = geotransform[3]
            x_max = x_min + geotransform[1] * raster_dataset.RasterXSize
            y_min = y_max + geotransform[5] * raster_dataset.RasterYSize

            # Calculate bounds for Leaflet
            bounds = [
                [y_min, x_min],
                [y_max, x_max],
            ]

            output_image_path = os.path.splitext(file_path)[0] + "_rendered.png"

            # Read raster data and render to an image
            band = raster_dataset.GetRasterBand(1)  # Use the first raster band
            # Get colormap based on metadata
            cmap = get_metadata_colormap(band)

            if not os.path.exists(output_image_path):
                raster_data, raster_normalized, _, _ = get_raster_normalized(band)

                rgba_colored = cmap(raster_normalized)  # Apply colormap (RGBA values)

                # Convert to uint8 format (0-255)
                rgba_image = (rgba_colored[:, :, :4] * 255).astype(np.uint8)

                # Set the alpha channel for transparency (No-data = Transparent)
                rgba_image[..., 3] = np.where(raster_data.mask, 0, 255)

                # Convert the RGBA array to an image
                color_ramp = Image.fromarray(rgba_image, mode="RGBA")

                # Save the rendered image with transparency
                color_ramp.save(output_image_path, "PNG", quality=95)

            # Get color levels for the raster band
            raster_color_levels = get_raster_color_levels(band, cmap)

            raster_dataset = None

            # Clean up the temporary files
            if reprojected_file_path != file_path:
                os.remove(reprojected_file_path)

            # Update the combined bounds
            (overlap, combined_bounds) = bounds_overlap_or_similar(
                combined_bounds, bounds
            )

            # Save the image URL for each GeoTIFF path only if the combined bounds are not far apart
            if overlap:
                image_urls.append(f"/geotiff/{output_image_path}")
        else:
            return {"error": "Unsupported file type. Only .shp and .tif are supported."}

    # Define a function to get a sorting key based on geometry type
    def get_geometry_order(feature):
        geometry_type = feature["geometry"]["type"]
        order = {
            "Polygon": 1,
            "MultiPolygon": 1,
            "LineString": 2,
            "MultiLineString": 2,
            "Point": 3,
            "MultiPoint": 3,
        }
        return order.get(geometry_type, 4)  # Default to last if unknown type

    def sorted_merge(*iterables, key=None):
        import heapq

        """Efficiently merge sorted iterables."""
        return heapq.merge(*iterables, key=key)

    if combined_geojson:
        combined_geojson["features"] = list(
            sorted_merge(combined_geojson["features"], key=get_geometry_order)
        )
    return {
        "geojson": combined_geojson,
        "bounds": combined_bounds,
        "center": (
            [
                (combined_bounds[0][0] + combined_bounds[1][0]) / 2,
                (combined_bounds[0][1] + combined_bounds[1][1]) / 2,
            ]
            if combined_bounds
            else None
        ),
        "raster_levels": raster_color_levels,
        "properties": combined_properties,
        "image_urls": image_urls,
        "tooltip": tool_tip,
    }


def export_map_service(image, form_data):
    try:
        output_format = form_data.get("export_format")
        output_path = form_data.get("export_path")
        output_filename = form_data.get("export_filename")
        file_paths = map(
            lambda x: os.path.join(Config.PATHFILE, x),
            json.loads(form_data.get("file_paths")),
        )

        valid_formats = ["png", "jpg", "jpeg", "pdf"]
        if output_format not in valid_formats:
            return {"error": "Unsupported export format"}

        export_dir = os.path.join(Config.PATHFILE_EXPORT, output_path)
        os.makedirs(export_dir, exist_ok=True)
        image_path = os.path.join(export_dir, f"{output_filename}.{output_format}")

        # Export image formats
        if output_format in ["jpg", "jpeg", "png", "pdf"] and image:
            img = Image.open(image)
            img.convert("RGB").save(image_path, output_format.upper(), quality=95)

        # Export shapefiles or raster datasets as images
        exported_images = [image_path]
        fig, ax = plt.subplots(figsize=(10, 8))
        raster_data = None

        for file_path in file_paths:
            fig, ax = plt.subplots(figsize=(10, 8))  # Create a new figure for each file

            if file_path.endswith(".shp"):
                gdf = gpd.read_file(file_path)
                gdf.plot(ax=ax, edgecolor="black")
            elif file_path.endswith(".tif"):
                dataset = gdal.Open(file_path)
                band = dataset.GetRasterBand(1)
                cmap = get_metadata_colormap(band)
                raster_data, _, raster_min, raster_max = get_raster_normalized(band)
                # Normalize raster values
                norm = mcolors.Normalize(vmin=raster_min, vmax=raster_max)
                # Display raster
                ax.imshow(raster_data, cmap=cmap, norm=norm, alpha=1)
                # Add raster legend (Colorbar)
                cbar = plt.colorbar(
                    plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                    ax=ax,
                    fraction=0.03,
                    pad=0.04,
                )
                cbar.set_label("Raster Classification", fontsize=12)

            # Add north arrow
            ax.annotate(
                "N",
                xy=(0.05, 0.9),
                xycoords="axes fraction",
                fontsize=14,
                fontweight="bold",
                ha="center",
            )
            ax.arrow(
                0.05,
                0.75,
                0,
                0.1,
                transform=ax.transAxes,
                color="black",
                head_width=0.02,
                head_length=0.03,
                lw=2,
            )

            # Save plot
            file_name = os.path.basename(file_path).split(".")[0]
            image_path = os.path.join(
                export_dir, f"{output_filename}_{file_name}.{output_format}"
            )
            plt.savefig(image_path, dpi=300, format=output_format)
            plt.close(fig)

            exported_images.append(image_path)

        return {"exported_images": exported_images}
    except Exception as e:
        return {"error": str(e)}
