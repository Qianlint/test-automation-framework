import traceback
import pymysql
import redis
import sys
import pymongo
import paramiko

from conf.operation_config import OperationConfig
from common.record_log import logs


conf = OperationConfig()

class ConnectMysql:

    def __init__(self):

        mysql_conf = {
            'host': conf.get_section_mysql('host'),
            'port': int(conf.get_section_mysql('port')),
            'user': conf.get_section_mysql('username'),
            'password': conf.get_section_mysql('password'),
            'database': conf.get_section_mysql('database')
        }

        try:
            self.conn = pymysql.connect(**mysql_conf, charset='utf8')
            # DictCursor returns database fields as key-value pairs.
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""Connected to MySQL successfully---
            host：{host}
            port：{port}
            db：{database}
            """.format(**mysql_conf))
        except Exception as e:
            logs.error(f"except:{e}")

    def close(self):
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()
        return True

    def query_all(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchall()

            keys = ''
            values = []
            for item in res:
                keys = list(item.keys())

            for ite in res:
                values.append(list(ite.values()))

            for val in values:
                # lst_format = [
                #     keys,
                #     val
                # ]
                lst_format = [
                    val
                ]

                return lst_format
                # return print_table(lst_format)

        except Exception as e:
            logs.error(e)
        finally:
            self.close()

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            logs.info('Deleted successfully')
        except Exception as e:
            logs.error(e)
        finally:
            self.close()

class ConnectRedis:

    def __init__(self, ip=conf.get_section_redis("host"), port=conf.get_section_redis("port"), username=None,
                 passwd=None, db=conf.get_section_redis("db")):
        self.host = ip
        self.port = port
        self.username = username
        self.password = passwd
        self.db = db
        # Use a connection pool; decode_responses=True converts responses to strings automatically.
        logs.info(f"Connecting to Redis--host:{ip},port:{port},user:{username},password:{passwd},db:{db}")
        try:
            pool = redis.ConnectionPool(host=self.host, port=int(self.port), password=self.password)
            self.first_conn = redis.Redis(connection_pool=pool, decode_responses=True)
            # print(self.first_conn.keys())
        except Exception:
            logs.error(str(traceback.format_exc()))

    def set_kv(self, key, value, ex=None):
        """
        :param key:
        :param value:
        :param ex: Expiration time in seconds.
        :return:
        """
        try:
            return self.first_conn.set(name=key, value=value, ex=ex)
        except Exception:
            logs.error(str(traceback.format_exc()))

    def get_kv(self, name):
        try:
            return self.first_conn.get(name)
        except Exception:
            logs.error(str(traceback.format_exc()))

    def hash_set(self, key, value, ex=None):
        try:
            return self.first_conn.set(name=key, value=value, ex=ex)
        except Exception:
            logs.error(str(traceback.format_exc()))

    def hash_hget(self, names, keys):
        """Get the value for a key from the hash identified by names."""
        try:
            data = self.first_conn.hget(names, keys).decode()
            return data
        except Exception:
            logs.error(str(traceback.format_exc()))

    def hash_hmget(self, name, keys, *args):
        """Get values for multiple keys from the hash identified by name."""
        if not isinstance(keys, list):
            raise ("keys must be a list")
        try:
            return self.first_conn.hmget(name, keys, *args)
        except Exception:
            logs.error(str(traceback.format_exc()))

class ConnectMongo(object):

    def __init__(self):

        mg_conf = {
            'host': conf.get_section_mongodb("host"),
            'port': int(conf.get_section_mongodb("port")),
            'user': conf.get_section_mongodb("username"),
            'passwd': conf.get_section_mongodb("password"),
            'db': conf.get_section_mongodb("database")
        }

        try:
            client = pymongo.MongoClient(
                'mongodb://{user}:{passwd}@{host}:{port}/{db}'.format(**mg_conf))
            self.db = client[mg_conf['db']]
            logs.info("Connected to MongoDB, ip:{host}, port:{port}, database:{db}".format(**mg_conf))
        except Exception as e:
            logs.error(e)

    def use_collection(self, collection):
        try:
            collect_table = self.db[collection]
        except Exception as e:
            logs.error(e)
        else:
            return collect_table

    def insert_one_data(self, data, collection):
        """
        :param data: Data to insert.
        :param collection: Collection to insert into.
        :return:
        """
        try:
            self.use_collection(collection).insert_one(data)
        except Exception as e:
            logs.error(e)

    def insert_many_data(self, documents, collection):
        """
        :param args: Multiple records to insert.
        :param collection:
        :return:
        """
        if not isinstance(documents, list):
            raise TypeError("documents must be a non-empty list")
        for item in documents:
            try:
                self.use_collection(collection).insert_many([item])
            except Exception as e:
                logs.error(e)
                return None

    def query_one_data(self, query_parame, collection):
        """
        Query one record.
        :param query_parame: Query parameters as a dict, e.g. {'entId':'2192087652225949165'}
        :param collection: MongoDB collection, analogous to a MySQL table, stored in the database.
        :return:
        """
        if not isinstance(query_parame, dict):
            raise TypeError("query_parame must be a dict")
        try:
            res = self.use_collection(collection=collection).find_one(query_parame)
            return res
        except Exception as e:
            logs.error(e)

    def query_all_data(self, collection, query_parame=None, limit_num=sys.maxsize):
        """
        Query multiple records.
        :param collection: MongoDB collection, analogous to a MySQL table, stored in the database.
        :param query_parame: Query parameters as a dict, e.g. {'entId':'2192087652225949165'}
        :param limit_num: Maximum number of results.
        :return:
        """

        table = self.use_collection(collection)
        if query_parame is not None:
            if not isinstance(query_parame, dict):
                raise TypeError("query_parame must be a dict")
        try:
            query_results = table.find(query_parame).limit(limit_num)  # Limit the result count.
            res_list = [res for res in query_results]
            return res_list
        except Exception:
            return None

    def update_collection(self, query_conditions, after_change, collection):
        """
        :param query_conditions: Query criteria.
        :param after_change: Data to update.
        """
        if not isinstance(query_conditions, dict) or not isinstance(after_change, dict):
            raise TypeError("parameters must be dicts")
        res = self.query_one_data(query_conditions, collection)
        if res is not None:
            try:
                self.use_collection(collection).update_one(query_conditions, {"$set": after_change})
            except Exception as e:
                logs.error(e)
                return None
        else:
            logs.info("No records match the query criteria")

    def delete_collection(self, search, collection):
        """Delete one record."""
        if not isinstance(search, dict):
            raise TypeError("parameters must be dicts")
        try:
            self.use_collection(collection).delete_one(search)
        except Exception as e:
            logs.error(e)

    def delete_many_collection(self, search, collecton):
        try:
            self.use_collection(collecton).delete_many(search)
        except Exception:
            return None

    def drop_collection(self, collection):
        """Drop a collection."""
        try:
            self.use_collection(collection).drop()
            logs.info("delete success")
        except Exception:
            return None

class ConnectSSH(object):
    """Connect to an SSH server."""

    def __init__(self,
                 host=None,
                 port=22,
                 username=None,
                 password=None,
                 timeout=None):
        self.__conn_info = {
            'hostname': conf.get_section_ssh('host') if host is None else host,
            'port': int(conf.get_section_ssh('port')) if port is not None else port,
            'username': conf.get_section_ssh('username') if username is None else username,
            'password': conf.get_section_ssh('password') if password is None else password,
            'timeout': int(conf.get_section_ssh('timeout')) if timeout is None else timeout
        }

        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__client.connect(**self.__conn_info)

        if self.__client:
            logs.info('Connected to server {}'.format(self.__conn_info['hostname']))

    def get_ssh_content(self, command=None):
        stdin, stdout, stderr = self.__client.exec_command(
            command if command is not None else conf.get_section_ssh('command'))
        content = stdout.read().decode()
        return content


