import portfolioManagerServices as pm
import datetime
import os
import sys
import tkinter as tk
from tkinter import filedialog

accountId = 86044
username = 'NPS WASO Sustainable Buildings'
passwd = ''
urlRoot = 'https://portfoliomanager.energystar.gov/ws/'
auth_values = (username, passwd)
headers = {'Content-Type': 'application/xml'}
today = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

def getUploadFilePath():   
    root = tk.Tk()
    root.withdraw()
    print('\nBrowse to the location of the meter consumption data upload file: ')
    uploadfile = filedialog.askopenfilename()
    if (uploadfile[-4:].lower() != 'xlsx') & (uploadfile[-3:].lower() != 'xls'):
        sys.exit(uploadfile + ' does not appear to be a valid Excel spreadsheet. Exiting...')  
    return uploadfile     

def getLogFilePath():    
    root = tk.Tk()
    root.withdraw()
    print('Browse to the location where you would like the log files to be exported: ')
    logpath = filedialog.askdirectory()
    return logpath + '/'

