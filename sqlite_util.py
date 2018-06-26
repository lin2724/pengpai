import sqlite3
import threading

class DBItem:
    def __init__(self, name, type_str, is_primary=False):
        self.name = name[:]
        self.value = None
        self.type_str = type_str[:]
        self.is_primary = is_primary

        pass


class DBRow:
    def __init__(self):
        self.item_list = list()
        self.lock = threading.RLock()
        self.do_init()
        pass

    def __str__(self):
        ret_str = ''
        for item in self.item_list:
            ret_str += item.name + ' : ' + str(item.value) + '\n'
        return ret_str

    def do_init(self):

        pass

    def load(self, tuple_row):
        for idx, item in enumerate(self.item_list):
            item.value = tuple_row[idx]
        pass

    def get_proper_column_str(self, column):
        if type(column) == str or type(column)==unicode:
            ret_str = "'" + column + "'"
            return ret_str
        return str(column)
        pass

    def generate_create_table_str(self, table_name):
        ret_str = ''
        ret_str += 'CREATE TABLE IF NOT EXISTS %s(' % table_name
        for idx, item in enumerate(self.item_list):
            ret_str += item.name + ' ' + item.type_str + ' '
            if item.is_primary:
                ret_str += 'PRIMARY KEY'
            if idx != len(self.item_list) - 1:
                ret_str += ','
        ret_str += ')'
        return ret_str
        pass

    def generate_select_cmd_str(self, table_name):
        ret_str = ' select '
        for idx, item in enumerate(self.item_list):
            ret_str += table_name + '.' + item.name
            if idx != len(self.item_list)-1:
                ret_str += ' , '
        ret_str += ' from %s ' % table_name
        return ret_str
        pass

    def generate_insert_cmd__str(self, table_name):
        ret_str = ' insert into %s ' % table_name
        ret_str += ' ( '
        for idx, item in enumerate(self.item_list):
            ret_str += item.name
            if idx != len(self.item_list)-1:
                ret_str += ' , '
        ret_str += ' ) '
        ret_str += ' values '
        ret_str += '( '
        for idx, item in enumerate(self.item_list):
            ret_str += self.get_proper_column_str(item.value)
            if idx != len(self.item_list)-1:
                ret_str += ' , '
        ret_str += ' ) '
        return ret_str
        pass

    def generate_update_cmd__str(self, table_name):
        ret_str = ' update %s set ' % table_name
        for idx, item in enumerate(self.item_list):
            ret_str += item.name + '=' + self.get_proper_column_str(item.value)
            if idx != len(self.item_list)-1:
                ret_str += ' , '
        return ret_str
        pass


class DBRowHuaBan(DBRow):
    def do_init(self):
        self.item_list.append(DBItem('title', 'CHAR', is_primary=True))
        self.item_list.append(DBItem('auth', 'CHAR'))
        self.item_list.append(DBItem('key_word', 'CHAR'))
        self.item_list.append(DBItem('from_src', 'CHAR'))
        self.item_list.append(DBItem('article_time', 'CHAR'))
        self.item_list.append(DBItem('comments_count', 'INT'))
        self.item_list.append(DBItem('thumb_up_count', 'INT'))
        pass


class DBHandler:
    def __init__(self):
        self.con = None
        self.change_cur = None
        self.select_cur = None
        self.table_name = 'PengPai'
        self.lock = threading.RLock()
        pass

    def load(self, db_file_path):
        self.con = sqlite3.connect(db_file_path)
        self.change_cur = self.con.cursor()
        self.select_cur = self.con.cursor()
        pass

    def do_init(self):
        pass

    def add_table(self, table_name):
        self.table_name = table_name[:]
        huaban_row = DBRowHuaBan()
        create_command = huaban_row.generate_create_table_str(self.table_name)
        print create_command
        self.con.execute(create_command)
        self.con.commit()
        pass

    def get_row(self, limit):
        self.lock.acquire()

        huaban_row = DBRowHuaBan()
        command = huaban_row.generate_select_cmd_str(self.table_name)
        command += ' where %s.%s == 0 ' % (self.table_name, huaban_row.item_list[3].name)
        command += 'limit %d' % limit
        print command
        cur = self.con.cursor()
        # self.con.execute(command)
        # self.con.commit()
        cur.execute(command)
        self.con.commit()
        tup_items = cur.fetchall()
        # print tup_items
        ret_row_list = list()
        print 'get [%d]' % len(tup_items)
        for tup_item in tup_items:
            row = DBRowHuaBan()
            row.load(tup_item)
            ret_row_list.append(row)

        self.lock.release()
        return ret_row_list

    def insert_row(self, db_row):
        self.lock.acquire()

        # db_row = DBRowHuaBan()
        command = db_row.generate_insert_cmd__str(self.table_name)
        # command += ' where %s.%s != 0 ' % (self.table_name, db_row.item_list[3].name)
        print command
        try:
            self.con.execute(command)
            self.con.commit()
        except sqlite3.IntegrityError:
            pass

        self.lock.release()

    def update_row(self, db_row):
        self.lock.acquire()

        # db_row = DBRowHuaBan()
        command = db_row.generate_update_cmd__str(self.table_name)
        command += " where %s.%s = %s " % (self.table_name, db_row.item_list[2].name, db_row.get_proper_column_str(db_row.item_list[2].value))
        # print command
        self.con.execute(command)
        self.con.commit()

        self.lock.release()

    def exist(self):
        if self.con:
            self.con.close()


def test():
    print type(str)
    handler = DBHandler()
    handler.load('test.db')
    handler.add_table('huaban')
    huaban_row = DBRowHuaBan()

    huaban_row.item_list[0].value = 'tatle'
    huaban_row.item_list[1].value = 'auth'
    huaban_row.item_list[2].value = 'key_word'
    huaban_row.item_list[3].value = 'from_src'
    huaban_row.item_list[4].value = 'article_time'
    huaban_row.item_list[5].value = 128
    huaban_row.item_list[6].value = 0
    handler.insert_row(huaban_row)
    handler.get_row(100)
    # handler.update_row('xx', 123)
    pass


if __name__ == '__main__':
    test()