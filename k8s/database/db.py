import psycopg2
import os


class Database():

    def __init__(self, db_config, apis_api):
        self.host = db_config.get('host')
        self.db_name = db_config.get('db_name')
        self.user = db_config.get('user')
        self.password = db_config.get('password')
        self.apis_api = apis_api

    def db_connect(self):
        conn = psycopg2.connect(host=self.host,
                                database=self.db_name,
                                user=self.user,
                                password=self.password)
        return conn

    def check_conn(self):
        try:
            conn = psycopg2.connect(host=self.host,
                                    database=self.db_name,
                                    user=self.user,
                                    password=self.password)

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        # finally:
        #     if conn is not None:
        #         conn.close()
        #         print('Database connection closed.')

    def insert_namespace(self, namespace_list):
        conn = Database.db_connect(self)

        for item in namespace_list:
            print(f"Inserting {item}")
            sql = f"""INSERT INTO namespaces(name)
                      SELECT '{item}'
                      WHERE NOT EXISTS (
                        SELECT 1 FROM namespaces WHERE name='{item}'
                    );
            """

            cur = conn.cursor()
            cur.execute(sql, (item, item,))
            conn.commit()

        conn.close()

    def create_tables(self):
        """ create tables in the PostgreSQL database"""
        commands = (
            """
            CREATE TABLE IF NOT EXISTS deployments (
                name VARCHAR(255) NOT NULL,
                namespace VARCHAR(255) NOT NULL,
                revision VARCHAR(255) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS namespaces (
                    name VARCHAR(255) NOT NULL
            )
            """
        )

        conn = Database.db_connect(self)
        cur = conn.cursor()
        # create table one by one

        for command in commands:
            print(f"Executing {command}")
            cur.execute(command)
        # close communication with the PostgreSQL database server
        conn.commit()
        cur.close()

    def insert_deployments(self, namespace_list):
        conn = Database.db_connect(self)
        cur = conn.cursor()

        for n in namespace_list:
            response = self.apis_api.list_namespaced_deployment(namespace=n)
            for d in response.items:
                sql = f"""INSERT INTO deployments(name, namespace, revision)
                      SELECT '{d.metadata.name}', '{n}', '{d.metadata.generation}'
                      WHERE NOT EXISTS (
                        SELECT 1 FROM deployments WHERE name='{d.metadata.name}'
                    );
                       """
                cur.execute(sql)
                conn.commit()

        conn.close()

if __name__ == '__main__':
    Database()

