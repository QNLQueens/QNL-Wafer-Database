import tkinter
from tkinter import ttk
from tkinter import messagebox
import os
import openpyxl
from database import *

class WaferEdit:
    def __init__(self, window):
        self.window = window
        self.window.title("Data Entry Form")

        frame = tkinter.Frame(window)
        frame.pack()

        # Wafer Info Frame
        wafer_info_frame = tkinter.LabelFrame(frame, text="Wafer Information")
        wafer_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Wafer ID Selection Listbox
        wid_select_label = tkinter.Label(wafer_info_frame, text="Select Wafer ID")
        wid_select_label.grid(row=0, column=0)
        self.wid_listbox = tkinter.Listbox(wafer_info_frame, height=5)
        self.wid_listbox.grid(row=1, column=0, rowspan=2, padx=10)

        # Populate listbox with Wafer IDs from Excel
        self.load_wafer_ids()

        # Open Button to fetch data for the selected Wafer ID
        open_button = tkinter.Button(wafer_info_frame, text="Open", command=self.load_data)
        open_button.grid(row=1, column=1)

        # Wafer ID Entry (editable)
        wid_label = tkinter.Label(wafer_info_frame, text="Wafer ID")
        wid_label.grid(row=0, column=2)
        self.wid_entry = tkinter.Entry(wafer_info_frame)
        self.wid_entry.grid(row=1, column=2)

        # Year
        year_label = tkinter.Label(wafer_info_frame, text="Year")
        year_label.grid(row=0, column=3)
        self.year_spinbox = tkinter.Spinbox(wafer_info_frame, from_=2015, to=2025)  # Adjusted to a valid range
        self.year_spinbox.grid(row=1, column=3)

        # Wafer Type
        wtype_label = tkinter.Label(wafer_info_frame, text="Wafer Type")
        wtype_label.grid(row=2, column=2)
        self.wtype_combobox = ttk.Combobox(wafer_info_frame, values=["101", "100", "Quarter"])
        self.wtype_combobox.grid(row=3, column=2)

        # Date Acquired
        date_label = tkinter.Label(wafer_info_frame, text="Date Acquired (MM/DD)")
        date_label.grid(row=2, column=3)
        self.date_entry = tkinter.Entry(wafer_info_frame)
        self.date_entry.grid(row=3, column=3)

        # Created At
        from_label = tkinter.Label(wafer_info_frame, text="Created at")
        from_label.grid(row=4, column=0)
        self.from_combobox = ttk.Combobox(wafer_info_frame, values=['NFK', "NRC"])
        self.from_combobox.grid(row=5, column=0)

        # Substrate
        sub_label = tkinter.Label(wafer_info_frame, text="Substrate")
        sub_label.grid(row=4, column=1)
        self.sub_combobox = ttk.Combobox(wafer_info_frame, values=["InP", "GaAs"])
        self.sub_combobox.grid(row=5, column=1)

        # Quality
        qual_label = tkinter.Label(wafer_info_frame, text="Quality")
        qual_label.grid(row=4, column=2)
        self.qual_combobox = ttk.Combobox(wafer_info_frame, values=["Good", "Bad"])
        self.qual_combobox.grid(row=5, column=2)

        # Description Frame
        description_frame = tkinter.LabelFrame(frame, text="Description")
        description_frame.grid(row=1, column=0, padx=20, pady=10)

        # Intended Use
        intuse_label = tkinter.Label(description_frame, text="Intended Use")
        intuse_label.grid(row=0, column=0)
        self.intuse_entry = tkinter.Entry(description_frame)
        self.intuse_entry.grid(row=1, column=0)

        # Summary
        summary_label = tkinter.Label(description_frame, text="Summary")
        summary_label.grid(row=2, column=0)
        self.summary_entry = tkinter.Entry(description_frame)
        self.summary_entry.grid(row=3, column=0)

        # Submit Button to save data
        submit_button = tkinter.Button(frame, text="Submit", command=self.save_data)
        submit_button.grid(row=2, column=0, padx=20, pady=10)

        self.fields = {
            'Year': self.year_spinbox,
            'ID': self.wid_entry,
            'Type': self.wtype_combobox,
            'Intended Use': self.intuse_entry,
            'Date Acquired': self.date_entry,
            'Summary': self.summary_entry,
            'From': self.from_combobox,
            'Substrate': self.sub_combobox,
            'Quality': self.qual_combobox
        }

        self.types = {
            'Year': int,
            'ID': str,
            'Type': str,
            'Intended Use': str,
            'Date Acquired': str,
            'Summary': str,
            'From': str,
            'Substrate': str,
            'Quality': str
        }

    def load_wafer_ids(self):
        """Load Wafer IDs from the database and populate the listbox."""
        con = load_most_recent()
        wafers = con.table('wafers').execute()
        wafer_ids = wafers['ID']


        # Clear the listbox before populating
        self.wid_listbox.delete(0, tkinter.END)

        # Assuming Wafer IDs are in the second column
        for wafer_id in wafer_ids:
            self.wid_listbox.insert(tkinter.END, wafer_id)


    def load_data(self):
        """Load the data for the selected Wafer ID from the Database."""
        try:
            selected_wid = self.wid_listbox.get(self.wid_listbox.curselection())
        except tkinter.TclError:
            messagebox.showwarning("Selection Error", "Please select a Wafer ID to open.")
            return

        # Load the database
        con = load_most_recent()
        wafers = con.table('wafers').execute()

        columns = list(wafers.columns)
        row = wafers.loc[wafers['ID'] == selected_wid]
        
        if not row.empty:
            # Populate the form fields with the data
            for column in columns:
                print(row[column].values[0])
                if isinstance(self.fields[column], ttk.Combobox):
                    self.fields[column].set(row[column].values[0])
                else:
                    self.fields[column].delete(0, tkinter.END)
                    self.fields[column].insert(0, str(row[column].values[0]))

            return    

        messagebox.showwarning("Not Found", f"No data found for Wafer ID: {selected_wid}")

    def save_data(self):
        """Save or update the form data in the Excel file."""
        # Gather data from the form
        df = pd.DataFrame(columns=self.fields.keys())
        for column, field in self.fields.items():
            df[column] = [self.types[column](field.get())]
        print(df)
        # Load the database
        con = load_most_recent()
        
        # Update the database with the new data
        update_database(con, 'wafers', df)

        # Show success message
        messagebox.showinfo("Data Saved", "The data has been saved successfully!")

        # Close the window after saving the data
        self.window.destroy()


    

if __name__ == "__main__":
    root = tkinter.Tk()
    app = WaferEdit(root)
    root.mainloop()
