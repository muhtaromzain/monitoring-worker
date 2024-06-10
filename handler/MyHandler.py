from watchdog.events import FileSystemEventHandler
from process_data import ProcessData
from model.customer_portal import CustomerPortal
import logging
import os

class MyHandler(FileSystemEventHandler):
    # def on_modified(self, event):
    #     print(event)
    #     print(f'event type: {event.event_type}  path : {event.src_path}')

    # def on_deleted(self, event):
    #     print(event)
    #     print(f'event type: {event.event_type}  path : {event.src_path}')

    def on_created(self, event):
        if event.src_path.endswith('.csv'):
            orderData = ProcessData.reservedOrderNumber(event.src_path)

            if orderData['isSuccess']:
                dataCsv       = ProcessData.readCsv(event.src_path, orderData['data'])
                convertData   = ProcessData.convertData(dataCsv)
                insertData    = CustomerPortal.InsertTemp(convertData)

                if insertData:
                    insert = CustomerPortal.InsertFromTemp(orderData['detail'])
                    if insert:
                        CustomerPortal.DeleteTemp(orderData['detail']['dtCode'], orderData['detail']['timestamps'])
                        # CustomerPortal.DeleteUnknownDtCode(orderData['detail'])
                        ProcessData.moveFile(event.src_path)
                        ProcessData.export(orderData['detail'])
                        # pass
                    else:
                        CustomerPortal.RollbackHeader(orderData['detail'])
                        ProcessData.moveFileToError(event.src_path)

                else:
                    CustomerPortal.RollbackHeader(orderData['detail'])
                    ProcessData.moveFileToError(event.src_path)

            else:
                ProcessData.moveFileToError(event.src_path)
        else:
            logging.warn("Invalid file type, must send csv file")
            os.remove(event.src_path)