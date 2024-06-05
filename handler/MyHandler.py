from watchdog.events import FileSystemEventHandler
from process_data import ProcessData
from config.database import Database
from model.customer_portal import CustomerPortal

class MyHandler(FileSystemEventHandler):
    # def on_modified(self, event):
    #     print(event)
    #     print(f'event type: {event.event_type}  path : {event.src_path}')

    # def on_deleted(self, event):
    #     print(event)
    #     print(f'event type: {event.event_type}  path : {event.src_path}')

    def on_created(self, event):
        dataCsv       = ProcessData.readCsv(event.src_path)
        convertData   = ProcessData.convertData(dataCsv)
        header        = ProcessData.generateHeader(dataCsv)
        convertHeader = ProcessData.convertData(header, False)
        insertData    = CustomerPortal.Insert(convertHeader, convertData)

        if (insertData):
            ProcessData.moveFile(event.src_path)
            ProcessData.export(convertHeader)