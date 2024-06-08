from config.database import Database
import logging
import mariadb

class CustomerPortal():
    def Insert(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql          = "INSERT INTO customer_portal (dt_code, order_number, sku, qty, created_on) VALUES (?,?,?,?,?)"

        try:
            # insert data
            cursor.executemany(sql, data)
            conn.commit()
            logging.info("inserted values %s", data)
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to insert values %s", data)
            print("Error: {}".format(e))
            conn.rollback()
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()
    
    def InsertFromTemp(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql    = """INSERT INTO customer_portal
                    SELECT cpt.dt_code,
                        cpt.order_number,
                        cpt.sku,
                        cpt.qty,
                        cpt.created_on
                    FROM users AS u
                    LEFT JOIN users_groups AS ug ON ug.user_id = u.id
                    LEFT JOIN customer_portal_headers AS cph ON cph.dt_code = u.username
                    LEFT JOIN customer_portal_temp AS cpt ON cpt.dt_code = cph.dt_code AND cpt.created_on = cph.created_on AND cpt.order_number = cpt.order_number
                    WHERE u.username IN %s"""
        
        sql = sql.replace('%s', data['dtCode'])

        try:
            # insert data
            cursor.execute(sql)
            conn.commit()
            logging.info("inserted values from temp succeed")
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to insert from temp")
            print("Error: {}".format(e))
            conn.rollback()
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()
    
    def InsertTemp(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql          = "INSERT INTO customer_portal_temp (dt_code, order_number, sku, qty, created_on) VALUES (?,?,?,?,?)"

        try:
            # insert data
            cursor.executemany(sql, data)
            conn.commit()
            logging.info("inserted values %s", data)
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to insert values %s", data)
            print("Error: {}".format(e))
            conn.rollback()
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()
    
    def InsertHeader(dataHeader: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        headerSql    = "INSERT INTO customer_portal_headers (dt_code, order_number, customer_code, warehouse_code, term_code, is_submitted, remarks, send_timestamps, created_on) VALUES (?,?,?,?,?,?,?,?,?)"

        try:
            # insert data
            cursor.executemany(headerSql, dataHeader)
            conn.commit()
            logging.info("inserted values %s", dataHeader)
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to insert values %s", dataHeader)
            print("Error: {}".format(e))
            conn.rollback()
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()

    def DeleteTemp(dtCode: str, timestamps: str):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql    = """DELETE FROM customer_portal_temp
                    WHERE dt_code IN %s
                    AND created_on = "$timestamps"
                """
        
        sql = sql.replace('%s', dtCode).replace('$timestamps', timestamps)

        try:
            # insert data
            cursor.execute(sql)
            conn.commit()
            logging.info("deleted values from temp succeed")
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to deleted temp")
            print("Error: {}".format(e))
            conn.rollback()
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
    
    def GetCTL(data: list, isAuto: bool):
        sendToCp = '0'
        if isAuto:
            sendToCp = '1'
        
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = data['dtCode']

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
                    FROM users AS u
                    LEFT JOIN users_groups AS ug ON ug.user_id = u.id
                    LEFT JOIN customer_portal_headers AS cph ON cph.dt_code = u.username
                    LEFT JOIN customer_portal AS cp ON cp.order_number = cph.order_number AND cp.dt_code = cph.dt_code AND cp.created_on = cph.created_on
                    WHERE cp.dt_code IN %s
                    AND cp.created_on = "1717654526"
                    AND u.send_to_cp = "$sendToCp"
                    AND u.active = "1"
                    AND ug.group_id = "2"
                    GROUP BY cph.dt_code, cph.created_on, cph.order_number
                    ) AS data_cp"""

        sql = sql.replace('%s', whereClause).replace('$timestamps', data['timestamps']).replace('$sendToCp', sendToCp)

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

    def GetHeader(data: list, isAuto: bool):
        sendToCp = '0'
        if isAuto:
            sendToCp = '1'
        
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = data['dtCode']

        sql    = """SELECT cph.dt_code,
                        cph.order_number,
                        cph.customer_code,
                        cph.warehouse_code,
                        cph.term_code,
                        cph.created_on,
                        COUNT(cp.order_number) AS no_of_lines,
                        0 AS net_price,
                        SUM(cp.qty) AS quantity_sent
                    FROM users AS u
                    LEFT JOIN users_groups AS ug ON ug.user_id = u.id
                    LEFT JOIN customer_portal_headers AS cph ON cph.dt_code = u.username
                    LEFT JOIN customer_portal AS cp ON cp.dt_code = cph.dt_code AND cp.created_on = cph.created_on AND cp.order_number = cp.order_number
                    WHERE cph.dt_code IN %s
                    AND cp.created_on = "$timestamps"
                    AND u.send_to_cp = "$sendToCp"
                    AND u.active = "1"
                    AND ug.group_id = "2"
                    GROUP BY cph.dt_code, cph.created_on, cph.order_number"""

        sql = sql.replace('%s', whereClause).replace('$timestamps', data['timestamps']).replace('$sendToCp', sendToCp)

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

    def GetDetail(data: list, isAuto: True):
        sendToCp = '0'
        if isAuto:
            sendToCp = '1'
        
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = data['dtCode']

        sql    = """SELECT cp.dt_code,
                        cp.order_number,
                        cp.sku,
                        cp.qty,
                        0 AS price,
                        cp.created_on
                    FROM users AS u
                    LEFT JOIN users_groups AS ug ON ug.user_id = u.id
                    LEFT JOIN customer_portal_headers AS cph ON cph.dt_code = u.username
                    LEFT JOIN customer_portal AS cp ON cp.dt_code = cph.dt_code AND cp.created_on = cph.created_on AND cp.order_number = cp.order_number
                    WHERE cph.dt_code IN %s
                    AND cp.created_on = "$timestamps"
                    AND u.send_to_cp = "$sendToCp"
                    AND u.active = "1"
                    AND ug.group_id = "2" 
                """

        sql = sql.replace('%s', whereClause).replace('$timestamps', data['timestamps']).replace('$sendToCp', sendToCp)

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

    def GetHeaderOrderNumberCounter(dataDtCode: list):
        # query get counter order number for DT
        conn   = Database.Connect()
        cursor = conn.cursor()

        whereClause = '(%s)'
        whereValue = ''
        for value in dataDtCode:
            separator = ','

            if value == dataDtCode[-1]:
                separator = ''
            
            whereValue += '"' + value + '"' + separator

        whereClause = whereClause.replace('%s', whereValue)

        sql    = """SELECT u.username AS dt_code,
                        CASE WHEN u.active = 1
                            THEN IF(cph.order_number IS NULL, LPAD(1, '5', 0), LPAD(MAX(cph.order_number) + 1, '5',0)) 
                        ELSE LPAD(0, '5', 0)
                        END AS order_number_counter,
                        '9001' AS customer_code,
                        '9104' AS warehouse_code,
                        '02' AS term_code,
                        0 AS is_submitted,
                        NULL AS remarks,
                        0 AS send_timestamp
                    FROM users AS u
                    LEFT JOIN users_groups AS ug ON ug.user_id = u.id
                    LEFT JOIN customer_portal_headers AS cph ON cph.dt_code = u.username
                    LEFT JOIN customer_hierarchy AS ch ON ch.customer = u.username
                    WHERE u.username IN %s
                    AND ug.group_id = "2"
                    AND (cph.order_number != '00000' OR cph.order_number IS NULL)
                    AND u.active = "1"
                    AND u.send_to_cp = "1"
                    GROUP BY u.username, cph.dt_code"""

        sql = sql.replace('%s', whereClause)

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

    def DeleteUnknownDtCode(data: list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql    = """DELETE FROM customer_portal_headers WHERE dt_code IN
                        (
                            SELECT cph.dt_code
                            FROM customer_portal_headers AS cph
                            LEFT JOIN customer_portal AS cp ON cp.dt_code = cph.dt_code AND cp.created_on = cph.created_on
                            WHERE cph.dt_code IN %s
                            AND cp.dt_code IS NULL
                            GROUP BY cph.dt_code, cph.created_on
                        )
                    AND created_on IN
                        (
                            SELECT cph.created_on
                            FROM customer_portal_headers AS cph
                            LEFT JOIN customer_portal AS cp ON cp.dt_code = cph.dt_code AND cp.created_on = cph.created_on
                            WHERE cph.dt_code IN %s
                            AND cp.dt_code IS NULL
                            GROUP BY cph.dt_code, cph.created_on
                        )
                """
        
        sql = sql.replace('%s', data['dtCode'])

        try:
            # insert data
            cursor.execute(sql)
            conn.commit()
            logging.info("deleted unknown dt from header succeed")
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to deleted unknown dt")
            print("Error: {}".format(e))
            conn.rollback()
            return False
        finally:
            # free resources
            cursor.close()
            conn.close()

    def RollbackHeader(data:list):
        conn   = Database.Connect()
        cursor = conn.cursor()
        sql    = """DELETE FROM customer_portal_headers 
                    WHERE dt_code IN %s
                    AND created_on = "$timestamp"
                """
        
        sql = sql.replace('%s', data['dtCode']).replace('$timestamps', data['timestamps'])

        try:
            # insert data
            cursor.execute(sql)
            conn.commit()
            logging.info("Rollback header succeed")
            return True
        except mariadb.IntegrityError as e:
            logging.warn("failed to rollback header")
            print("Error: {}".format(e))
            conn.rollback()
            return False
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
    
    
