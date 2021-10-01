import os
import psycopg2


class Database():

    def __init__(self):
        self.DB_URI = os.environ["DATABASE_URL2"]
        self.__connect()

    def __connect(self):
        self.session = psycopg2.connect(self.DB_URI, sslmode="require")

    def __exec_query(self, query: str, status: bool = False) -> any:
        try:
            cur = self.session.cursor()
            cur.execute(query)
            if status is True:
                results = cur.statusmessage
            else:
                results = cur.fetchall()
            self.session.commit()
            cur.close()
            return results
        except ConnectionError as e:
            print(f"catch ConnectionError: {e}\n[ TRYING RECONNECTION ]")
            self.__connect()
            self.__exec_query(query)
        except Exception as e:
            print(f"catch Exceptation: {e}\n[ NOT EXECUTED ({query}) ]")

    def get_all_db(self) -> str:
        results = self.__exec_query("SELECT * FROM wex;")
        result = str(results)
        return result

    def id_exists(self, user_id: str) -> bool:
        results = self.__exec_query("SELECT * FROM wex;")
        tmp = False
        for n in results:
            print(n)
            if user_id == n[0]:
                tmp = True
        return tmp

    def get_address(self, user_id: str) -> str:
        results = self.__exec_query("SELECT * FROM wex;")
        tmp = "no_data"
        for n in results:
            if user_id == n[0]:
                tmp = n[1]
        return tmp

    def add_new_wallet(self, user_id: str, address: str, timestamp: int):
        tmp = str(timestamp)
        tmpp = tmp[:-3]
        timestamp = int(tmpp)
        results = self.__exec_query(
            "INSERT INTO wex values ('{}', '{}', '{}')".format(
                user_id, address, timestamp), True
        )
        return results

    def delete_wallet(self, user_id: str) -> bool:
        if self.id_exists(user_id) is True:
            try:
                results = self.__exec_query(
                    "DELETE FROM wex where user_id='{}';".format(
                        user_id), True)
                print(results)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            return False
