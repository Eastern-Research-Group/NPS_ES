# Energy Star Portfolio Manager API for NPS

## Description
These scripts upload meter consumption data from an Excel spreadsheet using Portfolio Manager's web services. 

#### Project Files
* .gitignore - Git ignore file; used for Git purposes only. 
* README.md - Documentation about this project. 
* portfolioManagerServices.py - Contains logging functions and functions that interact with the Portfolio Manager API, which can be called by other scripts such as uploadMeterConsumption.py.
* settings.py - Global variables.
* test.py - Can be run to verify a user has installed this project correctly, and also to perform a basic QA of an upload file containing meter consumption data. 
* uploadMeterConsumption.py - Uploads meter consumption data from an Excel spreadsheet to Portfolio Manager. 

When run, uploadMeterConsumption.py may produce two log files: 
* Error log, which contains detailed information about each error. (This file will only be created if any errors occur during the upload.)
* Success log, which documents the consumptionDataId that is created for each successful record. 

If the QA procedure of test.py is run, it will produce an error log if any of the rows in the file being tested contain invalid data as described below in the Installation section.

All log files will be exported to the logs folder in the local repository. 

## Preparation
A meter consumption data upload spreadsheet should be prepared. If there are multiple worksheets in the workbook, the first one will be used for the data upload. The following column headings must exist with these exact names:
* (03) ESPM Property Id
* (16) Portfolio Manager Meter ID
* (05) Start Date
* (06) End Date
* Final Consumption to Upload
* Final Cost to Upload

The columns can be in any order, and any additional columns will be ignored. 

Uploads containing tens or hundreds of thousands of rows will likely take many hours to run (expect an upload of 10,000 meters or 100,000 rows of consumption data to take anywhere from 8-20 hours), therefore it is advisable to install and run this script on a server instead of a personal computer, unless you can be sure the script will be able to run for the entire length of time and there will be no issues with the computer going to sleep. 

## Notes
Currently these scripts can only be used to upload meter consumption data, however, portfolioManagerServices.py contains functions that perform other calls to Portfolio Manager's web services which can be used to expand functionality at a later date. 

## Installation
1. At the command prompt or in Windows Powershell, navigate to the location in which you'd like to install this program. 
1. Clone this repository by issuing this command: ```git clone https://github.com/Eastern-Research-Group/NPS_ES```
1. If necessary, install [python](https://www.python.org/downloads/)
1. Install the dependencies:
    ```
    pip install requests
    pip install pandas
    ```
1. OPTIONAL: To run a test that the program is working, and perform an optional basic QA of the upload file, navigate to the root of the local repository and execute the following: 
    ```
    python test.py
    ``` 
    1. Enter the password for user NPS WASO Sustainable Buildings when prompted. The test script will check that it can access the live environment of the Portfolio Manager web services. 
    1. When prompted, browse to the location of the meter consumption data file to be uploaded. The test script will check that it is a valid Excel file.
    1. The test will next ask if you'd like to perform a basic QA of the upload file. Enter Y to run the test or any other key to exit the test. The test will look for rows in the upload spreadsheet where the Meter ID = '\*' or where any of the following columns are null:
        * (16) Portfolio Manager Meter ID
        * (05) Start Date
        * (06) End Date
        * Final Consumption to Upload
        * Final Cost to Upload
    1. If the QA portion of the test is executed, any rows that fail the QA will be logged to an Excel file in the logs directory. The test will also output the number of meters that need to be uploaded to the screen, which can help determine how long the upload will take. 

## Execution
1. To begin the upload, navigate to the root of the local repository and execute the following: 
    ```
    python uploadMeterConsumption.py
    ```
1. Enter the password for user NPS WASO Sustainable Buildings when prompted. 
1. When prompted, browse to the location of the meter consumption data file to be uploaded.
1. Depending on the number of meters with consumption data to be uploaded, the script may take many hours to execute. 
    * The program will print an "upload complete" message to the screen upon reaching the end of the upload file.
    * Do not exit the program or type anything in the console window until the "upload complete" message appears and the command prompt has reappeared. 
    * If the program encounters a fatal error, it will print an error message to the screen and exit. 
1. When the upload is complete, review the error log. If possible, correct the errors and re-upload. If desired, you can correct errors directly in the error log and re-upload it.
1. If the upload is interrupted before completing (due to user interaction, internet connection loss, or a fatal program error), scroll to the last row of the success log and identify the last successful row, then modify the upload file by deleting all rows prior to the row matching the last successful row in the success log, and re-run the upload by starting at Step 1 above. 

Note that new error and success logs will be created each time uploadMeterConsumption.py is run. The logs contain a timestamp in the file name to identify which run they are from. 


    
    