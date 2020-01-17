import settings as s
import csv
import requests
import xml.etree.ElementTree as et
import datetime
import os
import html
import sys

validUnits = ['ccf (hundred cubic feet)','cf (cubic feet)','cGal (hundred gallons) (UK)','cGal (hundred gallons) (US)','Cubic Meters per Day','cm (Cubic meters)','Cords','Gallons (UK)','Gallons (US)','GJ','kBtu (thousand Btu)','kcf (thousand cubic feet)','Kcm (Thousand Cubic meters)','KGal (thousand gallons) (UK)','KGal (thousand gallons) (US)','Kilogram','KLbs. (thousand pounds)','kWh (thousand Watt-hours)','Liters','MBtu (million Btu)','MCF(million cubic feet)','mg/l (milligrams per liter)','MGal (million gallons) (UK)','MGal (million gallons) (US)','Million Gallons per Day','MLbs. (million pounds)','MWh (million Watt-hours)','pounds','Pounds per year','therms','ton hours','Tonnes (metric)','tons']

meterTypeDict = {'Gallons (US)': 'Propane', 'kWh (thousand Watt-hours)': 'Electric', 'KGal (thousand gallons) (US)': 'Municipally Supplied Potable Water - Indoor','kcf (thousand cubic feet)': 'Natural Gas','MBtu (million Btu)':'District Steam'}

def extractErrorMsg(errorMessage):
    errormsg = ''
    root = et.fromstring(errorMessage)
    for errors in root.findall('errors'):
        for error in errors:
            errormsg = errormsg + error.get('errorDescription')
    errormsg = errormsg[:-2]
    return errormsg

def writeError(errorPath, errorMessage):
    f = open(errorPath,'a')
    f.write(str(datetime.datetime.now()) + '    ' + errorMessage + '\n')
    f.close()

def writeCsv(path, headings, data):
    with open(path, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        if os.path.getsize(path) == 0:
            writer.writerow(headings)
        writer.writerow(data)
    csvfile.close()

################################################################################

def checkPath(path):
    # check if trailing slash exists on a path and if not, add it
    if (path[-1] != '\\') & (path[-1] != '/'):
        if '/' in path:
            # Linux path
            newpath = path + '/'
        else: 
            # Windows path
            newpath = path + '\\'
    else:
        newpath = path
    return newpath

################################################################################

def checkPassword(accountId, password):
    url = s.urlRoot + 'account/'
    response = requests.get(url, auth=s.auth_values)
    if not response.ok:
        sys.exit('Incorrect password; please try again.')

################################################################################

def getPropertiesFromAccount(accountId, outfile=None, errorfile=None):
    url = s.urlRoot + 'account/' + str(accountId) + '/property/list'
    response = requests.get(url, auth=s.auth_values)
    if response.ok:
        root = et.fromstring(response.content)
        propertyDict = {}
        for links in root.findall('links'):
            for link in links.findall('link'):
                propertyDict[link.get('id')] = link.get('hint')
                if outfile:
                    headings = ['PropertyId', 'PropertyName']
                    data = [link.get('id'), link.get('hint')]
                    writeCsv(outfile, headings, data)
        return propertyDict
    else:
        print(accountId + ': ' + str(response))
        if errorPath:
            errorheadings = ['Timestamp','AccountId','ErrorMessage']
            error = [str(datetime.datetime.now()), accountId, extractErrorMsg(str(response))]
            writeCsv(errorfile, errorheadings, error)

def deleteProperty(propertyId, outfile=None, errorfile=None):
    url = s.urlRoot + 'property/' + str(propertyId)
    response = requests.delete(url, auth=s.auth_values)

    if response.ok:
        headings = ['PropertyId','Message']
        print('Property ID ' + str(propertyId) + ' deleted')
        writeCsv(outfile, headings, [propertyId, 'deleted'])
    else:
        errorheadings = ['Timestamp', 'PropertyId', 'ErrorMessage']
        error = [str(datetime.datetime.now()), str(propertyId), extractErrorMsg(str(response.text))]
        writeCsv(errorfile, errorheadings, error)
################################################################################

def getMetersFromProperty(propertyId, outfile=None, errorfile=None):
    url = s.urlRoot + 'property/' + str(propertyId) + '/meter/list'
    response = requests.get(url, auth=s.auth_values)
    if response.ok:
        root = et.fromstring(response.content)
        meterDict = {}
        for links in root.findall('links'):
            for link in links.findall('link'):
                meterDict[link.get('hint')] = link.get('id')
                if outfile:
                    headings = ['PropertyId', 'MeterId', 'MeterName']
                    data = [propertyId, link.get('id'), link.get('hint')]
                    writeCsv(outfile, headings, data)
        return meterDict
    else:
        print(str(propertyId) + ': ' + str(response))
        if errorfile:
            errorheadings = ['Timestamp','PropertyId','ErrorMessage']
            error = [str(datetime.datetime.now()), str(propertyId), extractErrorMsg(str(response))]
            writeCsv(errorfile, errorheadings, error)

def getMeter(meterId, outfile=None, errorfile=None, propertyId=None):
    url = s.urlRoot + 'meter/' + str(meterId)
    response = requests.get(url, auth=s.auth_values)

    if response.ok:
        root = et.fromstring(response.content)
        meterDict = {}

        meterDict['MeterId'] = root.find("./id").text
        meterDict['MeterName'] = root.find("./name").text
        meterDict['MeterType'] = root.find("./type").text
        meterDict['Unit'] = root.find("./unitOfMeasure").text
        meterDict['FirstBillDate'] = root.find("./firstBillDate").text
        meterDict['InUse'] = root.find("./inUse").text

        if outfile:
            headings = []
            data = []
            if propertyId:
                headings.append('PropertyId')
                data.append(propertyId)
            headings.extend(['MeterId', 'MeterName', 'MeterType', 'Unit', 'FirstBillDate', 'InUse'])
            data.extend(meterDict.values())
            writeCsv(outfile, headings, data)
        return meterDict
    else:
        print(str(meterId) + ': ' + str(response))
        if errorfile:
            errorheadings = ['Timestamp','MeterId','ErrorMessage']
            error = [str(datetime.datetime.now()), str(meterId), extractErrorMsg(str(response))]
            writeCsv(errorfile, errorheadings, error)

def deleteMeter(meterId):
    url = s.urlRoot + 'meter/' + str(meterId)
    response = requests.delete(url, auth=s.auth_values)

################################################################################

def getMeterConsumptionDataXml(cost, startDate, endDate, usage):
    vCost = '<cost>' + str(cost) + '</cost>'
    vStartDate = '<startDate>' + str(startDate) + '</startDate>'
    vEndDate = '<endDate>' + str(endDate) + '</endDate>'
    vUsage = '<usage>' + str(usage) + '</usage>'

    xml = '<meterConsumption estimatedValue="false">' + vCost + vStartDate + vEndDate + vUsage + '</meterConsumption>'
    return xml;

def postMeterConsumptionData(meterId, xml, outfile, errorfile, errordata):
    url = s.urlRoot + 'meter/' + str(meterId) + '/consumptionData'

    xml = '<meterData>' + xml + '</meterData>'
    response = requests.post(url, auth=s.auth_values, data=xml, headers=s.headers)

    if response.ok:
        root = et.fromstring(response.content)
        headings = ['meterId']
        for tag in root[0]:
            headings.append(tag.tag)

        for child in root:
            data = [str(meterId)]
            for child2 in child:
                data.append(child2.text)
        print(data)
        writeCsv(outfile, headings, data)
    else:
        errorheadings = ['Timestamp', 'PropertyId', 'MeterId', 'MeterName', 'Cost', 'StartDate', 'EndDate', 'Usage', 'ErrorMessage']
        errordata.append(extractErrorMsg(str(response.text)))
        writeCsv(errorfile, errorheadings, errordata)
        

def deleteMeterConsumption(consumptionDataId, outfile=None, errorfile=None):
    url = s.urlRoot + 'consumptionData/' + str(consumptionDataId)
    response = requests.delete(url, auth=s.auth_values)

    if response.ok:
        print('Consumption Data ID ' + str(consumptionDataId) + ' deleted')
        if outfile:
            headings = ['ConsumptionDataId','Message']
            writeCsv(outfile, headings, [consumptionDataId, 'deleted'])
    else:
        print(str(consumptionDataId) + ' ' + response.text)
        if errorfile:
            errorheadings = ['Timestamp', 'ConsumptionDataId', 'ErrorMessage']
            error = [str(datetime.datetime.now()), str(consumptionDataId), extractErrorMsg(str(response.text))]
            writeCsv(errorfile, errorheadings, error)

def deleteAllConsumptionData(meterId, outfile=None, errorfile=None):
    url = s.urlRoot + 'meter/' + str(meterId) + '/consumptionData'
    response = requests.delete(url, auth=s.auth_values)

    if response.ok:
        print('All consumption data for meter ID ' + str(meterId) + ' deleted')
        if outfile:
            headings = ['MeterId','Message']
            writeCsv(outfile, headings, [meterId, 'All consumption data deleted'])
    else:
        print(str(meterId) + ' ' + response.text)
        if errorfile:
            errorheadings = ['Timestamp', 'MeterId', 'ErrorMessage']
            error = [str(datetime.datetime.now()), str(meterId), extractErrorMsg(str(response.text))]
            writeCsv(errorfile, errorheadings, error)
