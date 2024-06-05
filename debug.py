import os
from process_data import Process as process
from config.database import Database
from model.customer_portal import CustomerPortal
from templates.txt import Txt as template
from time import strftime, localtime
import datetime
from itertools import groupby

class Debug():
    def convertData():
        print(os.path.join(os.sep, "input", "text.csv"))
        process.moveFile('./input\\ContohReport.csv')
        data = process.readCsv('./input\\ContohReport.csv')
        data = process.readCsv('ContohReport2.csv')
        data2 = process.convertData(data)
        process.export(data)
        print(data2)

    def distinctData():
        data = process.readCsv('ContohReport2.csv')
        unique_data = []

        for k, g in groupby(data, lambda x: (x["dt_code"], x["order_number"])):
            print(k[0])
            print(k[1])
            unique_data.append({"dt_code": k[0][0], "order_number": k[0][1]})
        for k in groupby(data, lambda x: (x["dt_code"], x["order_number"])):
            unique_data.append({"dt_code": k[0][0], "order_number": k[0][1]})

        print(unique_data)

    def writeCsv():
        data = process.readCsv('ContohReport2.csv')
        counter = 0

        with open("./output/output.txt", "w") as text_file:
            for val in data:
                match val['record']:
                    case 'OBRCTL':
                        text_file.write(template.OBRCTL(val) + '\n')
                    case 'OBRHDR':
                        text_file.write(template.OBRHDR(val) + '\n')
                    case 'OBRLIN':
                        counter += 1
                        text_file.write(template.OBRLIN(val, counter) + '\n')

        datetime.datetime.utcfromtimestamp('1717342136').strftime("%Y%m%d")
        time = strftime('%Y%m%d', localtime(1717342136))
        print(time)
        orig = datetime.datetime.fromtimestamp(1717342136)
        new = orig + datetime.timedelta(days=1)
        time1 = strftime('%Y%m%d', localtime(int(new.timestamp())))
        print(time1)

    def demoExport():
        header = CustomerPortal.GetHeader()
        print(header)
        CTL = CustomerPortal.GetCTL()
        print(CTL)
        data = process.readCsv('ContohReport2.csv')
        header        = process.generateHeader(data)
        convertHeader = process.convertData(header, False)
        export = process.export(convertHeader)
        detail = CustomerPortal.GetDetail(convertHeader)
        print(detail)

    def convertWhereClause():
        data = process.readCsv('ContohReport2.csv')
        header        = process.generateHeader(data)
        convertHeader = process.convertData(header, False)
        whereClause = ''
        for value in convertHeader:
            separator = '%s'

            if value == convertHeader[-1]:
                separator = ''
            
            whereClause += '(' + 'cph.dt_code = "' + value[0] + '"' + ' AND ' + 'cph.order_number = "' + value[1] + '"' + ')' + separator
        # print(convertHeader)
        whereClause = whereClause.replace('%s', ' OR ')

        print(convertHeader[-1])

    def bindData():

        HDR = [
            {
                "code": "62",
                "no": "01"
            },
            {
                "code": "62",
                "no": "02"
            },
            {
                "code": "61",
                "no": "01"
            },
            {
                "code": "61",
                "no": "02"
            },
        ] 

        LIN = [
            {
                "code": "62",
                "no": "01",
                "item_code": '89',
                "qty": '10'
            },
            {
                "code": "62",
                "no": "01",
                "item_code": '90',
                "qty": '20'
            },
            {
                "code": "62",
                "no": "02",
                "item_code": '89',
                "qty": '10'
            },
            {
                "code": "62",
                "no": "02",
                "item_code": '90',
                "qty": '20'
            },
            {
                "code": "61",
                "no": "01",
                "item_code": '89',
                "qty": '10'
            },
            {
                "code": "61",
                "no": "01",
                "item_code": '90',
                "qty": '20'
            },
            {
                "code": "61",
                "no": "02",
                "item_code": '89',
                "qty": '10'
            },
            {
                "code": "61",
                "no": "02",
                "item_code": '90',
                "qty": '20'
            },
        ]

        # Create a dictionary to hold the items grouped by 'code' and 'no'
        grouped_items = {}

        # Iterate over LIN and group items by 'code' and 'no'
        for item in LIN:
            key = (item['code'], item['no'])
            if key not in grouped_items:
                grouped_items[key] = []
            grouped_items[key].append(item)

        # Merge HDR and grouped items
        result = []
        for hdr in HDR:
            key = (hdr['code'], hdr['no'])
            hdr['items'] = grouped_items.get(key, [])
            result.append(hdr)

        # Print the merged result
        print(result)

    def print():
        print("Hello")

if __name__ == "__main__":
    Debug.print()
