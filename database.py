import ibis
import ibis.expr
import pandas as pd
import datetime
import glob
import os
import sqlite3

ibis.set_backend('sqlite')

def load_most_recent(from_excel=False):
    """
        Load the most recent data from the database.
        If it is a new day, save a new database with the most recent data.

        Args:
            None

        Returns:
            ibis.table: The table object.
    """
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    data_files = glob.glob('./database/data*.sqlite3')
    if (not from_excel) & (len(data_files) != 0): 
        most_recent_file = max(data_files, key=os.path.getctime) 
        con_old = ibis.sqlite.connect(most_recent_file)
        try:
            metadata = con_old.table('metadata').execute()
        except ibis.common.exceptions.IbisError:
            metadata = pd.DataFrame({'Date': ['']})
        if metadata['Date'].values[0] == date:
            # Ensure con_old contains all the tables we want
            tables = con_old.list_tables()
            if 'wafers' not in tables:
                initialize_from_excel(con_old, './database/wafers.xlsx', 'wafers')
            if 'chips' not in tables:
                initialize_from_excel(con_old, './database/chips.xlsx', 'chips', index='Chip ID')
            if 'epistructures' not in tables:
                initialize_from_excel(con_old, './database/epistructure.xlsx', 'epistructures', index='Layer ID')
            return con_old
        con = ibis.sqlite.connect(f'./database/data{date}.sqlite3')
        try:
            wafers = con_old.table('wafers').execute()
            con.create_table('wafers', wafers)
        except sqlite3.OperationalError:
            wafers = initialize_from_excel(con, './database/wafers.xlsx', 'wafers')
        try:
            chips = con_old.table('chips').execute()
            con.create_table('chips', chips)
        except sqlite3.OperationalError:
            chips = initialize_from_excel(con, './database/chips.xlsx', 'chips', index='Chip ID')
            con.create_table('epistructures', epistructures)
        try:
            epistructures = con_old.table('epistructures').execute()
        except ibis.common.exceptions.IbisError:
            epistructures = initialize_from_excel(con, './database/epistructures.xlsx', 'epistructures', index='Layer ID')
    else:
        os.remove(f'./database/data{date}.sqlite3')
        con = ibis.sqlite.connect(f'./database/data{date}.sqlite3')
        initialize_from_excel(con, './database/wafers.xlsx', 'wafers', index='Wafer ID')
        initialize_from_excel(con, './database/chips.xlsx', 'chips', index='Chip ID')
        initialize_from_excel(con, './database/epistructures.xlsx', 'epistructures', index='Layer ID')
    con.create_table('metadata', ibis.table([('Date', 'string')], name='metadata'))
    con.insert('metadata', pd.DataFrame({'Date': [date]}), overwrite=True)
    return con

def initialize_from_excel(con, filename, table_name, index='Wafer ID'):
    """
        Initialize a table in the database from an Excel file.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            filename (str): The path to the Excel file to be read.

        Returns:
            None
    """


    df = pd.read_excel(io=filename, sheet_name=None)['Sheet']
    df = df.fillna('')

    # Attempt to convert numeric-looking strings to proper numeric types
    for column in df.select_dtypes(include=['object']).columns:
        # Skip the index column - keep it as string
        if column == index:
            df[column] = df[column].astype('string')
            continue
            
        # Try to convert to numeric if appropriate
        try:
            # Check if column contains only integers or empty strings
            numeric_values = pd.to_numeric(df[df[column] != ''][column])
            if numeric_values.apply(lambda x: x.is_integer()).all():
                # Convert to integer
                temp_series = pd.to_numeric(df[column], errors='coerce')
                df[column] = temp_series.fillna('').astype('Int64')
            else:
                # It's not all integers, keep as string
                df[column] = df[column].astype('string')
        except:
            # If conversion fails, keep as string
            df[column] = df[column].astype('string') 

    # SQLite statement which creates a table with the same columns as the DataFrame
    # The ID column will have the unique constraint, and be the main key
    create_table = f'CREATE TABLE {table_name} (\n'
    columns = df.columns
    if index:
        columns = columns.drop(index)
        create_table += f'{index.replace(' ', '_')} TEXT PRIMARY KEY,\n'

    for column in columns:
        datatype = df[column].dtype
        column = column.replace(' ', '_')
        if datatype == 'int64':
            create_table += f'{column} INTEGER,\n'
        elif datatype == 'float64':
            create_table += f'{column} REAL,\n'
        else: 
            create_table += f'{column} TEXT,\n'
    create_table = create_table[:-2] + ')'
    con.raw_sql(create_table)
    if index:
        df = df.reindex(columns=[index] + list(columns))
    con.insert(table_name, df)
 
    # con.create_table(table_name, ibis.memtable(df))
    # print(con.compile(con.create_table(table_name, ibis.memtable(df))))

def save_to_excel(con, table_name, filename, index):
    """
        Save a table in the database to an Excel file.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to be saved.
            filename (str): The path to the Excel file to be written.
            index (str): The name of the index column.

        Returns:
            None
    """

    df = con.table(table_name).execute()

    # Reindex the DataFrame to have the index as the first column
    df = df.set_index(index)
    df.index.name = index

    # Convert integer-looking floats to integers to avoid decimal display
    for col in df.select_dtypes(include=['float']).columns:
        # Check if all non-NA values in the column are effectively integers
        if df[col].dropna().apply(lambda x: x.is_integer()).all():
            df[col] = df[col].astype('Int64')  # pandas nullable integer type
    
    # Replace underscores with spaces in column names
    df.columns = df.columns.str.replace('_', ' ')

    # Create an Excel writer with the specified engine
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet')

def database_from_excel(con):
    """ 
        This should be run only once to initialize the database from the Excel files.

    Args:
        con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
    
    Returns:
        None
    """

    initialize_from_excel(con, './database/wafers.xlsx', 'wafers', index='Wafer ID')
    initialize_from_excel(con, './database/chips.xlsx', 'chips', index='Chip ID')
    initialize_from_excel(con, './database/epistructures.xlsx', 'epistructures', index='Layer ID')

def read_database(con, table_name):
    """
        Read a table from the database.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to be read.

        Returns:
            ibis.table: The table object.
    """

    return con.table(table_name)

def write_database(con, table_name, df):
    """
        Write a table to the database.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to be written.
            df (pandas.DataFrame): The DataFrame to be written.

        Returns:
            None
    """

    con.create_table(table_name, ibis.memtable(df))
    
def overwrite_database(con, table_name, df):
    """
        Update a table in the database.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to be updated.
            df (pandas.DataFrame): The DataFrame to be updated.

        Returns:
            None
    """

    con.insert(table_name, df, overwrite=True)

def update_database(con, table_name, row, index='Wafer_ID'):
    """
        Append a row to a table in the database.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to append the row to.
            row (df): The row to be appended.

        Returns:
            None
    """
    table = con.table(table_name).execute()
    if row[index].values in table[index].values:
        table = table[table[index] != row[index].values[0]]
        overwrite_database(con, table_name, table)

    con.insert(table_name, row)

def execute(con):
    con.execute()
    
if __name__ == '__main__':
    con = load_most_recent(from_excel=True)
    ibis.options.interactive = True
    # try:
    #     database_from_excel(con)
    # except sqlite3.OperationalError:
    #     pass
        
    print(con.list_tables())

    
    # Load the database
    wafers = con.table('wafers')
    chips = con.table('chips')
    epistructures = con.table('epistructures')

    print(wafers.head())
    print(chips.head())
    print(epistructures.head())

    try:
        con.drop_table('wafers2')
    except:
        pass

    # Filter the database
    wafers2 = wafers.filter([wafers['Year'] == 2024])

    # Write the filtered database to a new table
    con.create_table('wafers2', wafers2)

    wafers2 = read_database(con, 'wafers2')
    print(wafers2.head())

    # New filter
    wafers3 = wafers.filter([wafers['Intended_Use'] == 'Waveguides'])

    # Overwrite the database
    overwrite_database(con, 'wafers2', wafers3)
    
    # Verify the overwrite
    wafers4 = read_database(con, 'wafers2')
    print(wafers4.head())

    # Single row update
    wafers5 = wafers.filter([wafers['Wafer_ID'] == 'QNL-001']).execute()
    wafers5['Wafer_ID'] = 'testing99'
    print(wafers5.head())

    update_database(con, 'wafers2', wafers5)
    
    # Verify the update
    wafers6 = read_database(con, 'wafers2')
    print(wafers6.head())

    con.drop_table('wafers2')

    # con.disconnect()
    
    # con = ibis.sqlite.connect('./database/dataTest.sqlite3')

    # database_from_excel(con)

    # # Test saving to excel
    save_to_excel(con, 'wafers', './database/wafers.xlsx', index='Wafer_ID')
    save_to_excel(con, 'chips', './database/chips.xlsx', index='Chip_ID')
    save_to_excel(con, 'epistructures', './database/epistructures.xlsx', index='Layer_ID')

    # # Delete the test database
    # con.drop_table('wafers')
    # con.drop_table('chips')
    # con.drop_table('epistructures')
    
    # con.disconnect()
    
    # os.remove('./database/dataTest.sqlite3')
    
