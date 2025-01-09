import tkinter
from tkinter import ttk
from tkinter import messagebox
import os
import openpyxl

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

    def load_wafer_ids(self):
        """Load Wafer IDs from the Excel file and populate the listbox."""
        filepath = "wafers.xlsx"
        if not os.path.exists(filepath):
            return  # No data file yet, so nothing to load

        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active

        # Clear the listbox before populating
        self.wid_listbox.delete(0, tkinter.END)

        # Assuming Wafer IDs are in the second column
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header
            self.wid_listbox.insert(tkinter.END, row[1])

        workbook.close()

    def load_data(self):
        """Load the data for the selected Wafer ID from the Excel file."""
        try:
            selected_wid = self.wid_listbox.get(self.wid_listbox.curselection())
        except tkinter.TclError:
            messagebox.showwarning("Selection Error", "Please select a Wafer ID to open.")
            return

        filepath = "wafers.xlsx"
        if not os.path.exists(filepath):
            messagebox.showwarning("File Not Found", "No data file found.")
            return

        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active

        # Search for the row with the matching Wafer ID
        for row in sheet.iter_rows(values_only=True):
            if row[1] == selected_wid:  # Assuming the Wafer ID is in the second column
                # Prepopulate form with the row data
                self.wid_entry.delete(0, "end")
                self.wid_entry.insert(0, row[1])

                self.year_spinbox.delete(0, "end")
                self.year_spinbox.insert(0, row[0])

                self.wtype_combobox.set(row[2])
                self.intuse_entry.delete(0, "end")
                self.intuse_entry.insert(0, row[3])

                self.date_entry.delete(0, "end")
                self.date_entry.insert(0, row[4])

                self.summary_entry.delete(0, "end")
                self.summary_entry.insert(0, row[5])

                self.from_combobox.set(row[6])
                self.sub_combobox.set(row[7])
                self.qual_combobox.set(row[8])

                workbook.close()
                return

        workbook.close()
        messagebox.showwarning("Not Found", f"No data found for Wafer ID: {selected_wid}")

    def save_data(self):
        """Save or update the form data in the Excel file."""
        filepath = "wafers.xlsx"

        # Load the existing workbook or create a new one if it doesn't exist
        if os.path.exists(filepath):
            workbook = openpyxl.load_workbook(filepath)
            sheet = workbook.active
        else:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            # Add headers
            sheet.append(["Year", "Wafer ID", "Wafer Type", "Intended Use", "Date Acquired",
                        "Summary", "Created At", "Substrate", "Quality"])

        # Gather data from the form
        year = self.year_spinbox.get()
        wid = self.wid_entry.get()
        wtype = self.wtype_combobox.get()
        intuse = self.intuse_entry.get()
        date_acquired = self.date_entry.get()
        summary = self.summary_entry.get()
        created_at = self.from_combobox.get()
        substrate = self.sub_combobox.get()
        quality = self.qual_combobox.get()

        # Search for the Wafer ID in the file and overwrite the existing entry
        found = False
        for row_index, row in enumerate(sheet.iter_rows(min_row=2, values_only=False), start=2):  # Skip header row
            if row[1].value == wid:  # Wafer ID is in the second column (index 1)
                # Update the existing row
                found = True
                sheet.cell(row=row_index, column=1).value = year
                sheet.cell(row=row_index, column=2).value = wid
                sheet.cell(row=row_index, column=3).value = wtype
                sheet.cell(row=row_index, column=4).value = intuse
                sheet.cell(row=row_index, column=5).value = date_acquired
                sheet.cell(row=row_index, column=6).value = summary
                sheet.cell(row=row_index, column=7).value = created_at
                sheet.cell(row=row_index, column=8).value = substrate
                sheet.cell(row=row_index, column=9).value = quality
                break
        
        if not found:
            # If Wafer ID doesn't exist, append new row
            sheet.append([year, wid, wtype, intuse, date_acquired, summary, created_at, substrate, quality])

        # Save the workbook
        workbook.save(filepath)
        workbook.close()

        # Show success message
        messagebox.showinfo("Data Saved", "The data has been saved successfully!")

        # Close the window after saving the data
        self.window.destroy()


if __name__ == "__main__":
    root = tkinter.Tk()
    app = WaferEdit(root)
    root.mainloop()
