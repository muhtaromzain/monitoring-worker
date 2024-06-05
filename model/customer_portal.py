from config.database import Database
import logging
import mariadb

class CustomerPortal():
    def Insert(header: list, data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        headerSql    = "INSERT INTO customer_portal_headers (dt_code, order_number, customer_code, warehouse_code, term_code, created_on) VALUES (?,?,?,?,?,?)"
        sql          = "INSERT INTO customer_portal (dt_code, order_number, barcode, qty, created_on) VALUES (?,?,?,?,?)"

        try:
            # insert data
            cursor.executemany(headerSql, header)
            cursor.executemany(sql, data)
            conn.commit()
            logging.info("inserted values %s", header)
            logging.info("inserted values %s", data)
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to insert values %s", header)
            logging.warn("failed to insert values %s", data)
            print("Error: {}".format(e))
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()
    
    def GetAll():
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql    = f'SELECT * FROM customer_portal'

        try:
            # insert data
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except mariadb.IntegrityError as e:
            print("Error: {}".format(e))
        finally:
            # free resources
            cursor.close()
            conn.close()
    
    def GetCTL(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = CustomerPortal.convertWhereClause(data)

        sql    = """SELECT 	'EPO' AS system_name,
                        COUNT(data_cp.order_number) AS no_of_po_sent,
                        SUM(data_cp.quantity_sent) AS quantity_sent,
                        SUM(data_cp.net_price) AS net_price
                    FROM
                    (
                    SELECT cph.dt_code,
                        cph.order_number,
                        cph.customer_code,
                        cph.warehouse_code,
                        cph.term_code,
                        cph.created_on,
                        COUNT(cp.order_number) AS no_of_lines,
                        0 AS net_price,
                        SUM(cp.qty) AS quantity_sent
                    FROM customer_portal_headers AS cph
                    LEFT JOIN customer_portal AS cp ON cp.order_number = cph.order_number AND cp.dt_code = cph.dt_code
                    WHERE %s
                    GROUP BY cph.order_number, cph.dt_code
                    ) AS data_cp"""

        sql = sql.replace('%s', whereClause)

        try:
            # insert data
            cursor.execute(sql)
            data = cursor.fetchall()

            columns = []
            for col in cursor.description:
                columns.append(col[0])

            res = []
            for val in data:
                res.append({
                    columns[0]: val[0],
                    columns[1]: val[1],
                    columns[2]: int(val[2]),
                    columns[3]: int(val[3])
                })

            return res
        except mariadb.IntegrityError as e:
            print("Error: {}".format(e))
        finally:
            # free resources
            cursor.close()
            conn.close()

    def GetHeader(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = CustomerPortal.convertWhereClause(data)

        sql    = """SELECT cph.dt_code,
                        cph.order_number,
                        cph.customer_code,
                        cph.warehouse_code,
                        cph.term_code,
                        cph.created_on,
                        COUNT(cp.order_number) AS no_of_lines,
                        0 AS net_price,
                        SUM(cp.qty) AS quantity_sent
                    FROM customer_portal_headers AS cph
                    LEFT JOIN customer_portal AS cp ON cp.order_number = cph.order_number AND cp.dt_code = cph.dt_code
                    WHERE %s
                    GROUP BY cph.order_number, cph.dt_code"""

        sql = sql.replace('%s', whereClause)

        try:
            # insert data
            cursor.execute(sql)
            data = cursor.fetchall()

            columns = []
            for col in cursor.description:
                columns.append(col[0])

            res = []
            for val in data:
                res.append({
                    columns[0]: val[0],
                    columns[1]: val[1],
                    columns[2]: val[2],
                    columns[3]: val[3],
                    columns[4]: val[4],
                    columns[5]: val[5],
                    columns[6]: val[6],
                    columns[7]: val[7],
                    columns[8]: int(val[8]),
                })

            return res
        except mariadb.IntegrityError as e:
            print("Error: {}".format(e))
        finally:
            # free resources
            cursor.close()
            conn.close()

    def GetDetail(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = CustomerPortal.convertDetailWhereClause(data)

        sql    = """SELECT cp.dt_code,
                        cp.order_number,
                        cp.barcode AS sku,
                        cp.qty,
                        0 AS price,
                        cp.created_on
                    FROM customer_portal AS cp
                    WHERE %s"""

        sql = sql.replace('%s', whereClause)

        try:
            # insert data
            cursor.execute(sql)
            data = cursor.fetchall()

            columns = []
            for col in cursor.description:
                columns.append(col[0])

            res = []
            for val in data:
                res.append({
                    columns[0]: val[0],
                    columns[1]: val[1],
                    columns[2]: val[2],
                    columns[3]: int(val[3]),
                    columns[4]: int(val[4]),
                    columns[5]: val[5]
                })

            return res
        except mariadb.IntegrityError as e:
            print("Error: {}".format(e))
        finally:
            # free resources
            cursor.close()
            conn.close()

    def convertWhereClause(data: list):
        whereClause = ''
        for value in data:
            separator = '%s'

            if value == data[-1]:
                separator = ''
            
            whereClause += '(' + 'cph.dt_code = "' + value[0] + '"' + ' AND ' + 'cph.order_number = "' + value[1] + '"' + ')' + separator

        whereClause = whereClause.replace('%s', ' OR ')
        return whereClause

    def convertDetailWhereClause(data: list):
        whereClause = ''
        for value in data:
            separator = '%s'

            if value == data[-1]:
                separator = ''
            
            whereClause += '(' + 'cp.dt_code = "' + value[0] + '"' + ' AND ' + 'cp.order_number = "' + value[1] + '"' + ')' + separator

        whereClause = whereClause.replace('%s', ' OR ')
        return whereClause

        
