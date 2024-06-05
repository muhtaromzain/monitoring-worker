# import csvkit
import csv
from datetime import datetime
# from config.database import Database
import shutil
import os
from templates.txt import Txt as template
from itertools import groupby
from model.central_portal import CentralPortal

class ProcessData():
    def readCsv(filePath: str):
        data = []
        if (filePath):
            with open(filePath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    data.append({
                            'dt_code': row['DT code'],
                            'order_number': row['Order number'],
                            'barcode': row['Barcode'],
                            'qty': row['Qty'],
                            'created_on': int(datetime.now().timestamp())
                    })

        return data

    def convertData(data: list, isDetail = True):
        dataForSql = []
        if (isDetail):
            for val in data:
                dataForSql.append((val['dt_code'], val['order_number'], val['barcode'], val['qty'], val['created_on']))
        else:
            for val in data:
                dataForSql.append((val['dt_code'], val['order_number'], val['customer_code'], val['warehouse_code'], val['term_code'], val['created_on']))


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
        listFilePath  = filePath.split('\\')
        directoryName = datetime.today().strftime("%d-%m-%Y")
        directory     = './report/' + directoryName

        destinationPath = directory + '/' + listFilePath[1] 

        if not os.path.exists(directory):
            os.makedirs(directory)

        shutil.move(filePath, destinationPath)

    def export(data: list):
        counter = 0

        directoryName = datetime.today().strftime('%d-%m-%Y')
        directory     = './output/' + directoryName
        extFileName   = datetime.today().strftime('%Y%m%d')
        fileName      = 'output_' + extFileName + '.txt'

        if not os.path.exists(directory):
            os.makedirs(directory)

        outputPath = directory + '/' + fileName 

        CTL = CentralPortal.GetCTL(data)
        HDR = CentralPortal.GetHeader(data)
        LIN = CentralPortal.GetDetail(data)

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
    
