import psycopg2
from datetime import datetime
from Properties import Properties


class Logger:
    def __init__(self, config: Properties, printing=False):
        self.conf = config
        self.conn = None
        self._establish_connection()
        self.print = printing
        if (not self.conf.LOG_TO_DATABASE) and (not self.print):
            print("LOGGING turned off!")

    @property
    def insert_query(self):
        return f"""
            INSERT INTO {self.conf.LOG_TABLE_NAME} (created_at, type, message)
            VALUES (%s, %s, %s)
        """

    def _establish_connection(self):
        if self.conf.LOG_TO_DATABASE:
            self.conn = psycopg2.connect(
                dbname=self.conf.DATABASE,
                user=self.conf.USER,
                password=self.conf.PASSWORD,
                host=self.conf.HOST,
                port=self.conf.PORT
            )

    def log(self, log_type, message):
        if self.print:
            print(f"{log_type}: {message}")
        if self.conf.LOG_TO_DATABASE:
            current_time = datetime.now()
            data_to_insert = (current_time, log_type, message)

            cursor = self.conn.cursor()
            cursor.execute(self.insert_query, data_to_insert)

            self.conn.commit()
            cursor.close()


if '__main__' == __name__:
    conf = Properties("./resources/config.ini")
    print(conf.EN_QUESTION_TRIGGERS)
    print(conf.PL_QUESTION_TRIGGERS)
    print(conf.PL_TRANSLATION_TRIGGERS)
    print(conf.EN_TRANSLATION_TRIGGERS)

    logger = Logger(conf, True)
    logger.log("test", conf.SYSTEM_QUESTION_PROMPT)
    logger.log("test", "This is test of logger with properties setup")
