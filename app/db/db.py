import sqlite3
from app import config


class Database:
    connection = None
    cursor = None

    def __init__(self):
        self.connection = sqlite3.connect(config['db']['path'])
        self.cursor = self.connection.cursor()
        cmd_list = ['''CREATE TABLE users(
                           chat_id VARCHAR(20) PRIMARY KEY,
                           name VARCHAR(20) NOT NULL
                       );''',
                    '''CREATE TABLE search_data(
                           no INT NOT NULL,
                           chat_id VARCHAR(20) NOT NULL,
                           title VARCHAR(30) NOT NULL,
                           rating VARCHAR(6) NOT NULL,
                           FOREIGN KEY (chat_id) REFERENCES users(chat_id),
                           CONSTRAINT pr_key PRIMARY KEY(no, chat_id)
                       );''',
                    '''CREATE TABLE cur_search_pos(
                           no INT NOT NULL,
                           chat_id VARCHAR(20) NOT NULL,
                           FOREIGN KEY (no, chat_id) REFERENCES search_data(no, chat_id)
                       );''']
        try:
            self.cursor.executescript(''.join(cmd_list))
            self.connection.commit()
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            print(str(e))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def add_user(self, chat_id, name):
        cmd = "INSERT INTO users VALUES ('{}', '{}');".format(str(chat_id),
                                                              str(name))
        try:
            self.cursor.execute(cmd)
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def get_name(self, chat_id):
        cmd = "SELECT name FROM users WHERE chat_id = (?);"

        self.cursor.execute(cmd, [str(chat_id)])
        if self.cursor.rowcount() == 0:
            raise Exception('No such user found')
        return self.cursor.fetchone()

    def clear_search_data(self, chat_id):
        try:
            self.cursor.execute("DELETE FROM cur_search_pos"
                                " WHERE chat_id = (?);", [str(chat_id)])
            self.cursor.execute("DELETE FROM search_data"
                                " WHERE chat_id = (?);", [str(chat_id)])
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def insert_search_data(self, chat_id, search_data):
        cmd = '''
            INSERT INTO search_data VALUES ((?), (?), (?), (?));
            '''

        try:
            for no, (title, rating) in enumerate(search_data):
                self.cursor.execute(cmd, [no, str(chat_id), title, rating])
            self.cursor.execute("INSERT INTO cur_search_pos"
                                " VALUES (0, (?));", [str(chat_id)])
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def change_cur_search_pos(self, chat_id, new_no):
        cmd = '''
            UPDATE cur_search_pos
            SET no = (?)
            WHERE chat_id = (?);
            '''
        try:
            self.cursor.execute(cmd, [new_no, str(chat_id)])
            self.connection.commit()
        except Exception as e:
            print(str(e))

    def get_cur_search_pos(self, chat_id):
        cmd = "SELECT no FROM cur_search_pos WHERE chat_id = (?);"
        try:
            self.cursor.execute(cmd, [str(chat_id)])
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(str(e))
            return None

    def get_search_data(self, chat_id):
        cmd = '''
            SELECT title, rating
            FROM search_data
            WHERE chat_id = (?)
            ORDER BY no;
            '''
        try:
            self.cursor.execute(cmd, [str(chat_id)])
            return self.cursor.fetchall()
        except Exception as e:
            print(str(e))
            return None

    def close(self):
        self.connection.close()
