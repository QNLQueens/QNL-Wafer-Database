import tkinter
from tkinter import ttk
from tkinter import messagebox
import os
import openpyxl

class WaferAdd:
    def __init__(self, window):
        self.window = window
        self.window.title("Data Entry Form")

        frame = tkinter.Frame(window)
        frame.pack()

        # Wafer Info Frame
        wafer_info_frame = tkinter.LabelFrame(frame, text="User Information")
        wafer_info_frame.grid(row=0, column=0, padx=20, pady=10)

        # Year
        year_label = tkinter.Label(wafer_info_frame, text="Year")
        year_label.grid(row=0, column=0)
        self.year_spinbox = tkinter.Spinbox(wafer_info_frame, from_=2015, to='infinity')
        self.year_spinbox.grid(row=1, column=0)

        # Wafer ID
        wid_label = tkinter.Label(wafer_info_frame, text="Wafer ID")
        wid_label.grid(row=0, column=1)
        self.wid_entry = tkinter.Entry(wafer_info_frame)
        self.wid_entry.grid(row=1, column=1)
        
        #Wafer Type
        wtype_label = tkinter.Label(wafer_info_frame, text="Wafer Type")
        wtype_label.grid(row=0, column=2)
        self.wtype_combobox = ttk.Combobox(wafer_info_frame, values=["101", "100", "Quarter"])
        self.wtype_combobox.grid(row=1, column=2)
        
        #Date Acquired
        date_label = tkinter.Label(wafer_info_frame, text="Date Acquired (MM/DD)")
        date_label.grid(row=0, column=3)
        self.date_entry = tkinter.Entry(wafer_info_frame)
        self.date_entry.grid(row=1, column=3)
        
        # Configure grid padding
        for widget in wafer_info_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        
        #Description Frame
        description_frame = tkinter.LabelFrame(frame, text="User Information")
        description_frame.grid(row=1, column=0, padx=20, pady=10)
        
        #Intended Use
        intuse_label = tkinter.Label(description_frame, text="Intended Use")
        intuse_label.grid(row=0, column=0)
        self.intuse_entry = tkinter.Entry(description_frame)
        self.intuse_entry.grid(row=1, column=0)
        
        #Summary
        summary_label = tkinter.Label(description_frame, text="Summary")
        summary_label.grid(row=2, column=0)
        self.summary_entry = tkinter.Entry(description_frame)
        self.summary_entry.grid(row=3, column=0)
        
        for widget in description_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)
        
        # Submit Button
        button = tkinter.Button(frame, text="Enter data", command=self.enter_data)
        button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

    def enter_data(self):
        year = self.year_spinbox.get()
        wid = self.wid_entry.get()
        wtype = self.wtype_combobox.get()
        date = self.date_entry.get()
        intuse = self.intuse_entry.get()
        summary = self.summary_entry.get()

        filepath = "C:/Users/ittas/2.0 QNL Wafer Directory/wafers.xlsx"

        if not os.path.exists(filepath):
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            heading = ["Year", "ID", "Type", "Intended Use", "Date Acquired","Summary"]
            sheet.append(heading)
            workbook.save(filepath)

        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        sheet.append([year, wid, wtype, intuse, date, summary])
        workbook.save(filepath)

if __name__ == "__main__":
    root = tkinter.Tk()
    app = WaferAdd(root)
    root.mainloop()
