import sys
import os
import warnings
import settings as s
import pandas as pd
import portfolioManagerServices as pm
from getpass import getpass

s.passwd = getpass('Enter the password for user ' + s.username + ': ')
s.auth_values = (s.username, s.passwd)
pm.checkPassword(s.accountId, s.passwd)
print('Account access verified.')

uploadfile = s.getUploadFilePath()    
errorfile = s.logpath + s.today + '_consumptionData_error.xlsx'

print('Upload file is ' + uploadfile)
print('Log directory is ' + logpath)

doQA = input('\nWould you like to run a basic QA of your upload file? Enter Y for yes or any other key for no:  ')
if doQA.upper() != 'Y':
    sys.exit()

def getErrorMessage(row):
    errormsg = '';
    if row['(16) Portfolio Manager Meter ID']=='*':
        errormsg = 'Invalid Meter ID; '
    if pd.isnull(row['(16) Portfolio Manager Meter ID']) | pd.isnull(row['(05) Start Date']) | pd.isnull(row['(06) End Date']) | pd.isnull(row['Final Consumption to Upload']) | pd.isnull(row['Final Cost to Upload']):
        errormsg = errormsg + 'Meter ID, Cost, Start Date, End Date, and/or Usage is null; '
    errormsg = errormsg[:-2]
    return errormsg;
    
print('\nPerforming basic QA of upload file. This may take a few minutes...')
# turn off numpy FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# upload the file to a dataframe, exit if file can't be read
try:
    df = pd.read_excel(uploadfile)
except:
    sys.exit('Unable to parse file ' + uploadfile + '. Verify the file is a valid Excel spreadsheet and try again.')
# turn off panda's chained assignment warning
pd.options.mode.chained_assignment = None 
    
# remove columns we don't need
# df = df[['(03) ESPM Property Id','(02) Property Name','(16) Portfolio Manager Meter ID','(04) Meter Name','(05) Start Date','(06) End Date','Final Consumption to Upload','Final Cost to Upload','Energy Type']]

# find rows where MeterId = *, or MeterId, StartDate, EndDate, Usage, or Cost is null
mask = (df['(16) Portfolio Manager Meter ID']=='*') | df['(16) Portfolio Manager Meter ID'].isnull() | df['(05) Start Date'].isnull() | df['(06) End Date'].isnull() | df['Final Consumption to Upload'].isnull() | df['Final Cost to Upload'].isnull()
gk = df[mask]
if len(gk) > 0:
    print('There are ' + str(len(gk)) + ' invalid rows that will not be uploaded. Check the error log for details.')
    
    gk['Error Message'] = gk.apply(getErrorMessage, axis=1)
    #  print bad rows to error logs
    gk.to_excel(errorfile, index=False)
    # drop bad rows from dataframe
    df. drop(gk. index, axis=0, inplace=True)

# get list of unique Meter IDs so we can count them
meterIds = list(df['(16) Portfolio Manager Meter ID'].unique())
print('\nThere are ' + str(len(meterIds)) + ' meters to process.')
