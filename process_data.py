# import csvkit
import csv
from datetime import datetime
# from config.database import Database
import shutil
import os
from templates.txt import Txt as template
from itertools import groupby
from model.customer_portal import CustomerPortal
import ntpath

class ProcessData():
    def readCsv(filePath: str, dataHeader: list):
        data = []
        if (filePath):
            with open(filePath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append({
                            'dt_code': row['DT code'],
                            'order_number': dataHeader[row['DT code']],
                            'sku': row['SKU'],
                            'qty': row['Qty'],
                            # 'created_on': int(datetime.now().timestamp())
                            'created_on': row['Timestamps']
                    })

        return data

    def insertTemp(filePath: str):
        data = []
        if (filePath):
            with open(filePath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append({
                            'dt_code': row['DT code'],
                            'sku': row['SKU'],
                            'qty': row['Qty'],
                            'created_on': row['Timestamps']
                    })

        return data

    def convertData(data: list, isDetail = True):
        dataForSql = []
        if (isDetail):
            for val in data:
                dataForSql.append((val['dt_code'], val['order_number'], val['sku'], val['qty'], val['created_on']))
        else:
            for val in data:
                dataForSql.append((val['dt_code'], val['order_number'], val['customer_code'], val['warehouse_code'], val['term_code'], val['is_submitted'], val['remarks'], val['send_timestamps'], val['created_on']))


        return dataForSql

    def generateHeader(data: list):
        header = []

        for k in groupby(data, lambda x: (x["dt_code"], x["order_number"])):
            header.append({
                    "dt_code": k[0][0], 
                    "order_number": k[0][1],
                    "customer_code": '9001',
                    "warehouse_code": '9104',
                    "term_code": '02',
                    "created_on": int(datetime.now().timestamp())
            })
        
        return header
        
    def moveFile(filePath: str):
        fileName = ntpath.basename(filePath)
        directoryName = datetime.today().strftime("%d-%m-%Y")
        directory     = './report/' + directoryName

        destinationPath = directory + '/' + fileName

        if not os.path.exists(directory):
            os.makedirs(directory)

        process = shutil.move(filePath, destinationPath)
        return process 

    def export(data: list, isAuto = True):
        counter = 0

        directoryName = datetime.today().strftime('%d-%m-%Y')
        directory     = './output/' + directoryName
        # extFileName   = datetime.today().strftime('%Y%m%d')
        extFileName   = data['basename'] + '_' + data['timestamps']
        fileName      = 'output_' + extFileName + '.txt'

        if not os.path.exists(directory):
            os.makedirs(directory)

        outputPath = directory + '/' + fileName 

        CTL = CustomerPortal.GetCTL(data, isAuto)
        HDR = CustomerPortal.GetHeader(data, isAuto)
        LIN = CustomerPortal.GetDetail(data, isAuto)

        bindedData = ProcessData.bindHeaderAndDetail(HDR, LIN)

        with open(outputPath, "w") as text_file:
            text_file.write(template.OBRCTL(CTL) + '\n')
            for header in bindedData:
                text_file.write(template.OBRHDR(header) + '\n')
                for item in header['items']:
                    counter += 1
                    text_file.write(template.OBRLIN(item, counter) + '\n')
                counter = 0
                    
    def bindHeaderAndDetail(header: list, detail: list):
        # Create a dictionary to hold the items grouped by 'dt_code' and 'order_number'
        grouped_items = {}

        # Iterate over detail and group items by 'dt_code' and 'order_number'
        for item in detail:
            key = (item['dt_code'], item['order_number'])
            if key not in grouped_items:
                grouped_items[key] = []
            grouped_items[key].append(item)

        # Merge header and grouped items
        result = []
        for hdr in header:
            key = (hdr['dt_code'], hdr['order_number'])
            hdr['items'] = grouped_items.get(key, [])
            result.append(hdr)
        
        return result
    
    def reservedOrderNumber(filePath: str) -> dict:
        res = {}
        with open(filePath) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            data = list(reader)

        data.pop(0)

        flattenedDtCode = [item[0] for item in data]
        distinctDtCode  = list(set(flattenedDtCode))
        
        flattenedTimestamps = [item[3] for item in data]
        timestamps  = list(set(flattenedTimestamps))[0]

        whereClauseDtCode = '(' + ', '.join(['"' + item + '"' for item in distinctDtCode]) + ')'

        # delete temp
        CustomerPortal.DeleteTemp(whereClauseDtCode, timestamps)

        dataOrderNumber = CustomerPortal.GetHeaderOrderNumberCounter(distinctDtCode)

        # converted dt order number
        dtOrderNumber = {}
        insertReservedOrderNumber = []
        for val in dataOrderNumber:
            value = list(val)
            value.append(timestamps)
            insertReservedOrderNumber.append(tuple(value))
            dtOrderNumber[val[0]] = val[1]

        # mapped null dt in epo
        for dtCode in distinctDtCode:
            if dtCode not in dtOrderNumber.keys():
                dtOrderNumber[dtCode] = '00000'
                # include DT code that are not in database
                insertReservedOrderNumber.append((dtCode, '00000', '0000', '0000', '00', 0, None, 0, timestamps))

        insertHeader = CustomerPortal.InsertHeader(insertReservedOrderNumber)
        # insertHeader = True

        # set data master
        res['data'] = dtOrderNumber
        res['detail'] = {
            'dtCodeList': distinctDtCode,
            'dtCode': whereClauseDtCode,
            'timestamps': timestamps,
            'filepath': filePath,
            'filename': ntpath.basename(filePath),
            'basename': ntpath.basename(filePath).replace('.csv', ''),
            'outputFilename': ntpath.basename(filePath).replace('.csv', '.txt')
        }

        if insertHeader:
            res['isSuccess'] = True
        else:
            res['isSuccess'] = False
        
        return res