import ibis
import ibis.expr
import pandas as pd
import datetime
import glob
import os
import sqlite3
ibis.set_backend('sqlite')

def load_most_recent():
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
    if len(data_files) != 0: 
        most_recent_file = max(data_files, key=os.path.getctime) 
        con_old = ibis.sqlite.connect(most_recent_file)
        metadata = con_old.table('metadata').execute()
        if metadata['Date'][0] == date:
            return con_old
    con = ibis.sqlite.connect(f'./database/data{date}.sqlite3')
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
    object_columns = df.select_dtypes(include='object').columns
    for column in object_columns:
        df[column] = df[column].astype('string')

    # SQLite statement which creates a table with the same columns as the DataFrame
    # The ID column will have the unique constraint, and be the main key
    create_table = f'CREATE TABLE {table_name} (\n'
    columns = df.columns
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
    df = df.reindex(columns=[index] + list(columns))
    con.insert(table_name, df)


    
    # con.create_table(table_name, ibis.memtable(df))
    # print(con.compile(con.create_table(table_name, ibis.memtable(df))))

def save_to_excel(con, table_name, filename):
    """
        Save a table in the database to an Excel file.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to be saved.
            filename (str): The path to the Excel file to be written.

        Returns:
            None
    """

    df = con.table(table_name).execute()
    df.to_excel(filename)

def database_from_excel(con):
    """ 
        This should be run only once to initialize the database from the Excel files.

    Args:
        con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
    
    Returns:
        None
    """

    initialize_from_excel(con, './database/wafers.xlsx', 'wafers')
    initialize_from_excel(con, './database/all_wafers.xlsx', 'chips', index='Chip ID')

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

def update_database(con, table_name, row, index='Wafer ID'):
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
    if row[index] in table[index].values:
        con.update(table_name, row)

    con.insert(table_name, row)

def execute(con):
    con.execute()
    
if __name__ == '__main__':
    con = load_most_recent()
    ibis.options.interactive = True
    
    database_from_excel(con)
        
    print(con.list_tables())

    
    # Load the database
    wafers = con.table('wafers')
    chips = con.table('chips')

    print(wafers.head())

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
    
