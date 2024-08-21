# QNL-Wafer-Database
Web interface to access the Wafer Samples used by the Queen's Nanophotonics Lab (QNL).

References are included at the end with a short description. Highly recommend going through these to help understanding of the code in general.

Contact: Dylan (dylan.burke@queensu.ca)

## Intro
This database is a system of two programs which serves as a directory to easily access information about the Wafer Samples at QNL. Specifically, the aim of this project is to be able to easily access information about both wafers as well as the devices on the wafers. 

All Coded in Python using several libraries, with two used extensivley; Tkinter and Plotly Dash for the Chip Input and the Viewing App, respectivley.

### File Management

## Program Descriptions
### Chip and Wafer Inputs - Tkinter
The Input interface is coded primarily using the Tkinter library, which allows for creating a basic Graphical User Interface (GUI). This library is pretty old and low level, but this also means it is open ended in its application. It is used here to make an interactive map that allows for the simple plotting of devices onto a wafer by simply drawing the perimeter of the device onto the wafer.

![image](https://github.com/user-attachments/assets/0c1f2936-cc4e-4238-8123-6aa1885292de)
![image](https://github.com/user-attachments/assets/eb242896-837f-4ac6-86dd-1e152ee3a451)

Every wafer has its own Excel file where device data is stored, currently this data consists of an ID, the chip's owner and a short description which is inputed by the user after drawing the device. In addition, the coordinates of the four corners are saved.

![image](https://github.com/user-attachments/assets/85e2937a-5886-4d36-9370-52ba9922894c)
![image](https://github.com/user-attachments/assets/084bd433-741e-4ddb-b13c-2635fb4bfde1)

### Directory - Plotly Dash
The wafer view is used for simply accessing the data for both the wafers and devices. It uses Plotly Dash to develop the website, which is a library for Python that I find very easy to use and is great for viewing data, although it does not support saving new data, which is why tkinter is used for the editor. 

You will need certain files in an assets folder for the website to look correctly. The stylesheet is a css page, while favicon.ico and qnllogo.jpeg are simply the QNL logo in different formats. 

## Improvements needed
This directory uses many excel files in different folders to store data. It would be much more benificial (and probably easier), to use SQL to store all data (wafers and chips) into one .db file and sort through that.

A more useful edit feature is needed for both wafers and chips.

## Reference Links
### Front End: Plotly Dash
Here is a list of all the components native to plotly dash, along with examples for every widget. 

https://dash.plotly.com/dash-core-components

using dependent components: 

https://www.youtube.com/watch?v=TsYwhX0hEA8

### Dash Layout
These links include examples and tutorials on editing the layout and style of the Dash website:
https://hellodash.pythonanywhere.com/
https://dash-building-blocks.com/

### AG Grid
This is the sortable grid that is compatible with dash

https://www.ag-grid.com/

This link shows how to integrate it into a dash interface: https://dash.plotly.com/dash-ag-grid

### SQL 

https://docs.sqlalchemy.org/en/14/orm/quickstart.html 

https://www.youtube.com/watch?v=AKQ3XEDI9Mw&t=3s

### Tkinter
Two videos on how to make tkinter apps that store user inputted information

https://www.youtube.com/watch?app=desktop&v=vusUfPBsggw


https://www.youtube.com/watch?v=fvIThtPt6Nc

customtkinter add on: https://www.youtube.com/watch?v=Miydkti_QVE
