import ibis
import pandas as pd

ibis.set_backend('sqlite')
con = ibis.sqlite.connect('./database/data.sqlite3')



def initialize_from_excel(con, filename):
    """
        Initialize a table in the database from an Excel file.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            filename (str): The path to the Excel file to be read.

        Returns:
            None
    """


    df = pd.read_excel(io=filename, sheet_name=None)['Sheet']
    con.create_table('wafers', ibis.memtable(df))

def database_from_excel(con):
    """ 
        This should be run only once to initialize the database from the Excel files.

    Args:
        con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
    
    Returns:
        None
    """

    initialize_from_excel(con, 'wafers.xlsx')
    initialize_from_excel(con, 'all_wafers.xlsx')

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

def update_database(con, table_name, row):
    """
        Append a row to a table in the database.

        Args:
            con (ibis.backends.base.BaseBackend): The Ibis connection object to the database.
            table_name (str): The name of the table to append the row to.
            row (df): The row to be appended.

        Returns:
            None
    """

    con.insert(table_name, row)

if __name__ == '__main__':
    ibis.options.interactive = True
    try:
        database_from_excel(con)
    except Exception as e:
        print(e)
    
    # Load the database
    wafers = con.table('wafers')
    chips = con.table('chips')

    print(wafers.head())

    # Filter the database
    wafers2 = wafers.filter([wafers['Year'] == 2024])

    # Write the filtered database to a new table
    con.create_table('wafers2', wafers2)

    wafers2 = read_database(con, 'wafers2')
    print(wafers2.head())

    # New filter
    wafers3 = wafers.filter([wafers['Intended Use'] == 'Waveguides'])

    # Overwrite the database
    overwrite_database(con, 'wafers2', wafers3)
    
    # Verify the overwrite
    wafers4 = read_database(con, 'wafers2')
    print(wafers4.head())

    # Single row update
    wafers5 = wafers.filter([wafers['ID'] == 'QNL-001'])

    update_database(con, 'wafers2', wafers5)
    
    # Verify the update
    wafers6 = read_database(con, 'wafers2')
    print(wafers6.head())

    con.drop_table('wafers2')
    
