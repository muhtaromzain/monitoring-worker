from time import strftime, localtime
import datetime

class Txt():
    def OBRCTL(data: list):
        recordType      = 'OBRCTL'
        sysmName        = data[0]['system_name']
        concatSysName   = recordType + sysmName
        SystemName      = concatSysName + (' ' * (35 - len(concatSysName))
)
        noPoSent = str(data[0]['no_of_po_sent'])
        NoPoSent = noPoSent + (' ' * (2 - len(noPoSent)))

        qty     = str(data[0]['quantity_sent'])
        QtySent = qty + (' ' * (17 - len(qty)))

        price       = str(data[0]['net_price'])
        NetPrice    = price + (' ' * (17 - len(price)))

        res = SystemName + NoPoSent + QtySent + NetPrice
        return res
    
    def OBRHDR(data: list):
        recordType = 'OBRHDR'

        orderNumber = data['order_number']
        PoNumber    = orderNumber + (' ' * (15 - len(orderNumber)))

        dateOrder = strftime('%Y%m%d', localtime(data['created_on']))
        PoDate    = dateOrder + (' ' * (10 - len(dateOrder)))

        noLines       = str(data['no_of_lines'])
        NumberOfLines = noLines + (' ' * (4 - len(noLines))) 

        CustomerCode = str(data['customer_code'])
        SoldToParty  = '00' + str(data['dt_code'])
        ShipTo       = '00' + str(data['dt_code'])

        originalDate = datetime.datetime.fromtimestamp(data['created_on'])

        OrderDate = originalDate + datetime.timedelta(days=1)
        OrderDate = strftime('%Y%m%d', localtime(int(OrderDate.timestamp())))
        OrderDate = OrderDate + (' ' * (10 - (len(OrderDate))))

        DeliveryDate = originalDate + datetime.timedelta(days=3)
        DeliveryDate = strftime('%Y%m%d', localtime(int(DeliveryDate.timestamp())))
        DeliveryDate = DeliveryDate + (' ' * (10 - (len(DeliveryDate))))

        WarehouseCode = str(data['warehouse_code'])
        TermCode      = str(data['term_code'])
        
        res = recordType + PoNumber + PoDate + NumberOfLines + CustomerCode + SoldToParty + ShipTo + OrderDate + DeliveryDate + WarehouseCode + TermCode

        return res
    
    def OBRLIN(data: list, counter):
        recordType = 'OBRLIN'
        LineNumber = str(counter).zfill(4)

        ProductCode = data['sku']
        ProductCode = ProductCode + (' ' * (18 - (len(ProductCode))))

        qty         = str(data['qty'])
        QtyOrdered  = qty + (' ' * (11 - (len(qty))))

        Price = str(data['price'])
        Price = ('0' * (13 - len(Price))) + Price

        Uom = ''

        res = recordType + LineNumber + ProductCode + QtyOrdered + Price + Uom

        return res