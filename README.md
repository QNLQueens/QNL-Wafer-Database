# QNL-Wafer-Database
Web interface to access the Wafer Samples used by the Queen's Nanophotonics Lab (QNL).

References are included at the end.

Contact: Dylan (dylan.burke@queensu.ca)

## Intro
This database is a system of two programs which serves as a directory to easily access information about the Wafer Samples at QNL. Specifically, the aim of this project is to be able to easily access information about both wafers as well as the devices on the wafers. 

Coded in Python

### File Management

## Chip Input - Tkinter
The Input interface is coded primarily using the Tkinter library, which allows for creating a basic Graphical User Interface (GUI). This library is pretty old and low level, but this also means it is open ended in its application. It is used here to make an interactive map that allows for the simple plotting of devices onto a wafer by simply drawing the perimeter of the device onto the wafer.

![image](https://github.com/user-attachments/assets/0c1f2936-cc4e-4238-8123-6aa1885292de)
![image](https://github.com/user-attachments/assets/eb242896-837f-4ac6-86dd-1e152ee3a451)

Every wafer has its own Excel file where device data is stored, currently this data consists of an ID, the chip's owner and a short description which is inputed by the user after drawing the device. In addition, the coordinates of the four corners are saved.

![image](https://github.com/user-attachments/assets/85e2937a-5886-4d36-9370-52ba9922894c)
![image](https://github.com/user-attachments/assets/084bd433-741e-4ddb-b13c-2635fb4bfde1)

## Viewing App - Plotly Dash

## Improvements needed



Front End: Plotly Dash
https://dash.plotly.com/dash-core-components

AG Grid
https://www.ag-grid.com/
https://www.youtube.com/watch?v=Ww7-LC6rU6U

Back End: SQL Alchemy
https://docs.sqlalchemy.org/en/14/orm/quickstart.html 
https://www.youtube.com/watch?v=AKQ3XEDI9Mw&t=3s

Integration:
https://medium.com/plotly/building-plotly-dash-apps-on-a-lakehouse-with-databricks-sql-advanced-edition-4e1015593633

Tkinter: https://www.youtube.com/watch?app=desktop&v=vusUfPBsggw
https://www.youtube.com/watch?v=fvIThtPt6Nc
