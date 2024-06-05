from dotenv import load_dotenv
import mariadb
import os
import sys

load_dotenv()

DB_USERNAME     = os.getenv('DB_USERNAME')
DB_PASSWORD     = os.getenv('DB_PASWORD') if os.getenv('DB_PASWORD') is not None else ""
DB_HOST         = os.getenv('DB_HOST')
DB_PORT         = int(os.getenv('DB_PORT'))
DB_NAME         = os.getenv('DB_NAME')

class Database():
    def Connect():
        # Connect to MariaDB Platform
        try:
            conn = mariadb.connect(
                user=DB_USERNAME,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME
            )
            print("DB Connected")
            return conn
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1) 