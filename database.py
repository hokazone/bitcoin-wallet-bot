import psycopg2
import os


class Database():
    def __init__(self):
        self.DATABASE_URL = os.environ["DATABASE_URL"]

    def getAllIdsByDatabase(self) -> str:
        with psycopg2.connect(self.DATABASE_URL, sslmode="require") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM wex;")
            results = str(cur.fetchall())
            cur.close()
            return results

    def searchIdsByDatabase(self, user_id: str) -> bool:
        with psycopg2.connect(self.DATABASE_URL, sslmode="require") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM wex;")
            results = cur.fetchall()
            cur.close()
            tmp = False
            for n in results:
                print(n)
                if user_id == n[0]:
                    tmp = True
            return tmp

    def searchAddressByDatabase(self, user_id: str) -> str:
        with psycopg2.connect(self.DATABASE_URL, sslmode="require") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM wex;")
            results = cur.fetchall()
            cur.close()
            tmp = "no_data"
            for n in results:
                print(n)
                if user_id == n[0]:
                    tmp = n[1]
            return tmp

    def insertToDatabase(self, user_id: str, address: str, timestamp: int):
        tmp = str(timestamp)
        tmpp = tmp[:-3]
        timestamp = int(tmpp)
        with psycopg2.connect(self.DATABASE_URL, sslmode="require") as conn:
            cur = conn.cursor()
            results = cur.execute(
                "INSERT INTO wex values ('{}', '{}', '{}')".format(
                    user_id, address, timestamp)
            )
            cur.close()
            return results

    def deleteAddressInDatabase(self, user_id: str) -> bool:
        if self.searchIdsByDatabase(user_id) is True:
            with psycopg2.connect(
                self.DATABASE_URL, sslmode="require"
            ) as conn:
                cur = conn.cursor()
                try:
                    cur.execute(
                        "delete from wex where user_id='{}';".format(user_id))
                    cur.close()
                    return True
                except Exception as e:
                    print(e)
                    cur.close()
                    return False
        else:
            return False
