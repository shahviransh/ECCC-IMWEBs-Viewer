import sqlite3
import os
import pandas as pd
import xlsxwriter
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from cycler import cycler
from config import Config
from datetime import datetime
from flask import abort
from pathlib import Path
import sys

alias_mapping = {}


def fetch_data_service(data):
    try:
        # Extract the required parameters from the request data
        db_path = data.get("db_path")
        table_name = data.get("table_name")
        columns = data.get("columns", "All")
        selected_ids = data.get("id").split(",")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        date_type = data.get("date_type")
        interval = data.get("interval", "daily")
        method = data.get("method", "Equal").split(",")
        statistics = data.get("statistics", "None").split(",")
        stats_df = None

        # Fetch the data from the database and perform the required operations
        df = fetch_data_from_db(
            db_path, table_name, selected_ids, columns, start_date, end_date, date_type
        )

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
        return {"error": "error at fetch_data_service " + str(e)}


def export_data_service(data):
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
        output_path = data.get("export_path", Config.EXPORT_PATH)
        # Handle options nested structure
        options = {
            "data": data.get("options[data]", "true") == "true",
            "stats": data.get("options[stats]", "true") == "true",
        }
        columns_list = data.get("columns", "All").split(",")
        date_type = data.get("date_type")
        graph_type = data.get("graph_type", "scatter")

        # Parse multi_graph_type
        multi_graph_type = []
        index = 0
        while f"multi_graph_type[{index}][name]" in data:
            name = data.get(f"multi_graph_type[{index}][name]")
            graph_type = data.get(f"multi_graph_type[{index}][type]")
            multi_graph_type.append({"name": name, "type": graph_type})
            index += 1

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
            list(map(int, data.get("id").split(","))) if data.get("id") else [],
        )

        return {"file_path": file_path}
    except Exception as e:
        return {"error": "error at export_data_service " + str(e)}


def fetch_data_from_db(
    db_path, table_name, selected_ids, columns, start_date, end_date, date_type
):
    conn = sqlite3.connect(os.path.join(Config.PATHFILE, db_path))

    # table_name is an alias so replace it with the real table name
    real_table_name = alias_mapping.get(table_name, {}).get("real", table_name)

    # If specific columns are selected, map them to the real columns
    if columns != "All":
        columns_list = columns.split(",")
        real_columns = [
            alias_mapping.get(table_name, {}).get("columns", {}).get(col, col)
            for col in columns_list
        ]
        columns = ",".join(real_columns)

    # Start building the base query using real table name
    query = f"SELECT {columns if columns != 'All' else '*'} FROM {real_table_name}"
    params = []

    # Add conditions for selected_ids
    if selected_ids != [""]:
        placeholders = ",".join(["?"] * len(selected_ids))
        query += f" WHERE ID IN ({placeholders})"
        params.extend(selected_ids)

    # Add date range conditions
    if start_date and end_date:
        if selected_ids != [""]:
            query += f" AND {date_type} BETWEEN ? AND ?"
        else:
            query += f" WHERE {date_type} BETWEEN ? AND ?"
        params.extend([start_date, end_date])

    # Execute the query with parameters
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # Map real column names back to alias if needed
    alias_columns = [
        alias_mapping.get(real_table_name, {}).get("columns", {}).get(col, col)
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
        os.path.join(Config.PATHFILE, export_path)
        if not os.path.exists(export_path)
        else export_path
    )

    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = os.path.join(file_path, filename)

    # Map graph types to Matplotlib Axes methods
    GRAPH_TYPE_MAPPING = {
        "line": "plot",
        "bar": "column",
        "scatter": "scatter",
    }
    graph_title = map(lambda x: x["name"][:4], multi_graph_type).join("-")

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
            if options["data"]:
                dataframe1.to_csv(f, index=False)
            if options["stats"] and dataframe2 is not None:
                f.write("\n")
                dataframe2.to_csv(f, index=False)
    elif file_format == "txt":
        with open(file_path, "w") as f:
            if options["data"]:
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

                if selected_ids and selected_ids != [""]:
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
            chart.set_title({"name": graph_title})
            chart.set_y_axis({"name": "Values (Smaller Values)"})
            chart.set_y2_axis({"name": "Values (Larger Values)"})  # Add second y-axis

            # Insert the chart into the worksheet
            worksheet.insert_chart(f"{chr(65 + len(dataframe1.columns))}2", chart)
    elif file_format in ["png", "jpg", "jpeg", "svg", "pdf"]:
        # Plot each column as a line on the same figure
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()  # Create a secondary y-axis
        for i, column_graph in enumerate(multi_graph_type):
            column = column_graph["name"]
            plot_func = getattr(
                ax1 if column in primary_axis_columns else ax2,
                GRAPH_TYPE_MAPPING[column_graph["type"]],
            )

            ax1.set_prop_cycle(cycler(color=plt.cm.tab10.colors))
            ax2.set_prop_cycle(cycler(color=plt.cm.Set2.colors))

            if selected_ids and selected_ids != [""]:
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

        # Customize the primary axis
        ax1.set_xlabel(date_type)
        ax1.set_ylabel("Values (Smaller Values)")
        ax1.tick_params(axis="y")
        ax1.xaxis.set_major_locator(MaxNLocator(nbins=30))  # Scale x-axis ticks
        ax1.grid(visible=True, linestyle="--", alpha=0.6)

        # Customize the secondary axis
        ax2.set_xlabel(date_type)
        ax2.set_ylabel("Values (Larger Values)")
        ax2.tick_params(axis="y")
        ax2.grid(visible=True, linestyle="--", alpha=0.6)

        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        ax1.set_title(f"{graph_title}")

        # Rotate x-axis labels (explicitly for ax1 and ax2 if shared x-axis is used)
        for tick in ax1.get_xticklabels():
            tick.set_rotation(45)

        # Adjust layout to avoid label overlap
        plt.tight_layout()

        # Save the plot
        plt.savefig(file_path, format=file_format)

    return file_path


def get_table_names(db_path):
    try:
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
        return {"error": "error at get_table_names " + str(e)}


def get_files_and_folders(data):
    databases = set()
    folder_path = data.get("folder_path", "Jenette_Creek_Watershed")
    base_folder = folder_path
    base_path = (
        (sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__))
        if folder_path == "Jenette_Creek_Watershed"
        else folder_path
    )
    folder_path = os.path.join(
        base_path, folder_path
    )  # Absolute path relative to app.py
    allowed_base_path = os.path.abspath(
        os.path.join(base_path, base_folder)
    )  # Absolute base folder path

    # Validate that the requested path is within the allowed base directory
    if not folder_path.startswith(allowed_base_path):
        return {"error": "Invalid folder path."}

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
                if file_rel_path.endswith(".db3") and "lookup" not in file_rel_path:
                    databases.add(file_rel_path)
                files_and_folders.append(
                    {
                        "type": (
                            "database" if file_rel_path.endswith(".db3") else "file"
                        ),
                        "name": file_rel_path,
                    }
                )

        (
            alias_mapping.update(load_alias_mapping(databases))
            if not alias_mapping
            else None
        )

        return {"files_and_folders": files_and_folders}
    except Exception as e:
        return {"error": "error at get_files_and_folders " + str(e)}


# Example function to map date strings to seasons
def get_season_from_date(date_str):
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
    # Convert the 'Time' column to datetime
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


def load_alias_mapping(databases):
    """Load alias mapping from the lookup.db3 database."""
    conn = sqlite3.connect(os.path.join(Config.PATHFILE, Config.LOOKUP))
    alias_map = {}

    # Query the alias tables (Hydroclimate, BMP, scenario_2)
    for table in databases:
        # Cross-platform path
        path = Path(table)

        # Extract the table name from the path
        table = path.name.replace(".db3", "")

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
        if "Time" in columns:
            df = pd.read_sql_query(f"SELECT Time FROM {real_table_name}", conn)
            df["Time"] = pd.to_datetime(df["Time"])
            start_date = df["Time"].min().strftime("%Y-%m-%d")
            end_date = df["Time"].max().strftime("%Y-%m-%d")
            date_type = "Time"
            interval = "daily"
        elif "Date" in columns:
            df = pd.read_sql_query(f"SELECT Date FROM {real_table_name}", conn)
            df["Date"] = pd.to_datetime(df["Date"])
            start_date = df["Date"].min().strftime("%Y-%m-%d")
            end_date = df["Date"].max().strftime("%Y-%m-%d")
            date_type = "Time"
            interval = "daily"
        elif "Month" in columns:
            df = pd.read_sql_query(f"SELECT Month FROM {real_table_name}", conn)
            start_date = str(df["Month"].min())
            end_date = str(df["Month"].max())
            date_type = "Month"
            interval = "monthly"
        elif "Year" in columns:
            df = pd.read_sql_query(f"SELECT Year FROM {real_table_name}", conn)
            start_date = str(df["Year"].min())
            end_date = str(df["Year"].max())
            date_type = "Year"
            interval = "yearly"
        # Get list of IDs if an ID column exists, without querying unnecessary data
        id_column = next((col for col in columns if "ID" in col), None)
        ids = []
        if id_column:
            id_query = f"SELECT DISTINCT {id_column} FROM {real_table_name}"
            id_df = pd.read_sql_query(id_query, conn)
            ids = id_df[id_column].astype(str).tolist()

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
        return {"error": "error at get_columns_and_time_range " + str(e)}
