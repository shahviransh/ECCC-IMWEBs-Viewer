import sqlite3
import csv
import os
import pandas as pd

def get_aliases_from_lookup(lookup_db3_file, lookup_table_name):
    # Connect to the lookup database
    conn = sqlite3.connect(lookup_db3_file)
    cursor = conn.cursor()

    # Dictionary to hold table and column aliases
    aliases = {}

    # Fetch the table names and column names along with their aliases
    cursor.execute(f"SELECT OUTPUT_ID, COLUMN, UNIT, SHORT_NAME FROM {lookup_table_name}")
    rows = cursor.fetchall()

    # Populate the aliases dictionary
    for row in rows:
        table_name, column_name, unit, column_alias = row
        table_name = f"{table_name}_Results"
        table_name2 = f"{table_name}_SUBAREA_Results"

        if table_name not in aliases:
            aliases[table_name] = {}
            aliases[table_name2] = {}
        aliases[table_name][column_name] = column_alias
        aliases[table_name2][column_name] = column_alias

    # Close the connection
    conn.close()

    return aliases

def export_db3_to_csv_with_aliases(db3_files, lookup_aliases):
    for db3_file in db3_files:
        # Get the base file name without extension, relative to python file
        base_name = os.path.splitext(os.path.basename(db3_file))[0]

        # Output CSV file name
        csv_file_name = f"lookup\\{base_name}_export.csv"

        # Connect to the SQLite database
        conn = sqlite3.connect(db3_file)
        cursor = conn.cursor()

        # Open CSV file for writing
        with open(csv_file_name, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # Write header row
            csv_writer.writerow(["Table Name", "Table Alias", "Column Name", "Column Alias"])

            # Get the list of tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Iterate over each table
            for table in tables:
                table_name = table[0]
                table_alias = ""  # Blank alias for the table

                # Get the list of columns in the table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()

                # Iterate over each column
                for column in columns:
                    column_name = column[1]  # Column name

                    # Get the column alias from the lookup dictionary if it exists
                    column_alias = lookup_aliases.get(table_name, {}).get(column_name, "")

                    # Write row to CSV
                    csv_writer.writerow([table_name, table_alias, column_name, column_alias])

        # Close the connection
        conn.close()

        print(f"Exported data from {db3_file} to {csv_file_name}")

# Define the path to the lookup .db3 file and the lookup table name
lookup_db3_file = "backend\\Jenette_Creek_Watershed\\Database\\lookup.db3"
lookup_table_name = "OUTPUT"


# List of .db3 files to process
db3_files = [
    "backend\\Jenette_Creek_Watershed\\Database\\Hydroclimate.db3",
    "backend\\Jenette_Creek_Watershed\\Model01\\BMP.db3",
    "backend\\Jenette_Creek_Watershed\\Model01\\Output\\Scenario_2\\scenario_2.db3"
]

# Paths to our CSV files
hydroclimate_csv = 'lookup\\Hydroclimate_export.csv'
bmp_csv = 'lookup\\BMP_export.csv'
scenario_csv = 'lookup\\scenario_2_export.csv'

# Load the CSV files into DataFrames
hydroclimate_df = pd.read_csv(hydroclimate_csv)
bmp_df = pd.read_csv(bmp_csv)
scenario_df = pd.read_csv(scenario_csv)

# Connect to our SQLite database (lookup.db3)
conn = sqlite3.connect('backend\\Jenette_Creek_Watershed\\Database\\lookup.db3')
cursor = conn.cursor()

# Function to create a table in SQLite and insert data from DataFrame
def create_and_insert_table(df, table_name):
    # Create the table with column names similar to the CSV
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Table '{table_name}' has been created and data inserted.")

# Insert data into the database
create_and_insert_table(hydroclimate_df, 'Hydroclimate')
create_and_insert_table(bmp_df, 'BMP')
create_and_insert_table(scenario_df, 'scenario_2')

# Commit changes and close the connection
conn.commit()
conn.close()
print("Data has been successfully added to the database.")
