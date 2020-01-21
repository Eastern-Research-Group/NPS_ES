import settings as s
import portfolioManagerServices as pm
import pandas as pd
import datetime
from getpass import getpass
import sys
import warnings

s.passwd = getpass('Enter the password for user ' + s.username + ': ')
s.auth_values = (s.username, s.passwd)
pm.checkPassword(s.accountId, s.passwd)
print('Password accepted.')

uploadfile = s.getUploadFilePath()    

outfile = s.logpath +  s.today + '_consumptionData.csv'
errorfile = s.logpath + s.today + '_consumptionData_error.csv'

print('\nGathering information...')

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

try:
    df = pd.read_excel(uploadfile)
except:
    sys.exit('Unable to parse ' + uploadfile + '. Exiting...')
# remove columns we don't need
# df = df[['(03) ESPM Property Id','(02) Property Name','(16) Portfolio Manager Meter ID','(04) Meter Name','(05) Start Date','(06) End Date','Final Consumption to Upload','Final Cost to Upload','Energy Type']]
# turn off numpy FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# get list of unique Meter IDs so we can loop through it
meterIds = list(df['(16) Portfolio Manager Meter ID'].unique())
print('\nThere are ' + str(len(meterIds)) + ' meters to process.')

for meterId in meterIds:
    for idx, row in df[df['(16) Portfolio Manager Meter ID'] == meterId].iterrows():
        consumptionXml = ''
        errorheadings = ['Timestamp', 'PropertyId', 'MeterId', 'MeterName', 'Cost', 'StartDate', 'EndDate', 'Usage', 'ErrorMessage']
        errordata = [str(datetime.datetime.now()), str(row['(03) ESPM Property Id']), str(meterId), str(row['(04) Meter Name']), str(row['Final Cost to Upload']), str(row['(05) Start Date']), str(row['(06) End Date']), str(row['Final Consumption to Upload'])]
        # print(errordata)

        # cost
        cost = row['Final Cost to Upload']
        if not isNumber(cost):
            error = 'Property ID ' + str(row['(03) ESPM Property Id']) + ', Meter ' + row['(04) Meter Name'] + ' (' + str(meterId) + '): Cost "' + str(row['Final Cost to Upload']) + '" is not a valid number'
            print(error)
            errordata.append('Cost is not a valid number')
            pm.writeExcel(errorfile, errorheadings, errordata)
            continue
        # startDate
        try:
            startDate = row['(05) Start Date'].strftime('%Y-%m-%d')
        except:
            error = 'Property ID ' + str(row['(03) ESPM Property Id']) + ', Meter ' + row['(04) Meter Name'] + ' (' + str(meterId) + '): Start Date "' + str(row['(05) Start Date']) + '" is not valid'
            print(error)
            errordata.append('StartDate is not a valid date')
            pm.writeExcel(errorfile, errorheadings, errordata)
            continue
        # endDate
        try:
            endDate = row['(06) End Date'].strftime('%Y-%m-%d')
        except:
            error = 'Property ID ' + str(row['(03) ESPM Property Id']) + ', Meter ' + row['(04) Meter Name'] + ' (' + str(meterId) + '): End Date "' + str(row['(06) End Date']) + '" is not valid'
            print(error)
            errordata.append('EndDate is not a valid date')
            pm.writeExcel(errorfile, errorheadings, errordata)
            continue
        # usage
        usage = row['Final Consumption to Upload']
        if not isNumber(usage):
            error = 'Property ID ' + str(row['(03) ESPM Property Id']) + ', Meter ' + row['(04) Meter Name'] + ' (' + str(meterId) + '): Usage "' + str(row['Final Consumption to Upload']) + '" is not a valid number'
            print(error)
            errordata.append('Usage is not a valid number')
            pm.writeExcel(errorfile, errorheadings, errordata)
            continue
        consumptionXml = consumptionXml + pm.getMeterConsumptionDataXml(cost, startDate, endDate, usage)
        # print(consumptionXml)
        pm.postMeterConsumptionData(meterId, consumptionXml, outfile, errorfile, errordata)

print('\n\nUpload complete. Please see the success and error logs at ' + logpath + '.')