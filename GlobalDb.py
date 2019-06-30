#!/usr/bin/python 


class GlobalDb:
    """new sqlite globals database fdlog.sq3 replacing globals file"""
    def __init__(self):
        self.dbPath = globf[0:-4] + '.sq3'
        print "  Using local value database", self.dbPath
        self.sqdb = sqlite3.connect(self.dbPath, check_same_thread=False)  # connect to the database
        # Have to add FALSE here to get this stable.
        self.sqdb.row_factory = sqlite3.Row  # row factory
        self.curs = self.sqdb.cursor()  # make a database connection cursor
        sql = "create table if not exists global(nam text,val text,primary key(nam))"
        self.curs.execute(sql)
        self.sqdb.commit()
        self.cache = {}  # use a cache to reduce db i/o

    def get(self, name, default):
        if name in self.cache:
            # print "reading from globCache",name
            return self.cache[name]
        sql = "select * from global where nam == ?"
        results = self.curs.execute(sql, (name,))
        value = default
        for result in results:
            value = result['val']
            # print "reading from globDb", name, value
            self.cache[name] = value
        return value

    def put(self, name, value):
        now = self.get(name, 'zzzzz')
        # print now,str(value),now==str(value)
        if str(value) == now: return  # skip write if same
        sql = "replace into global (nam,val) values (?,?)"
        self.curs.execute(sql, (name, value))
        self.sqdb.commit()
        # print "writing to globDb", name, value
        self.cache[name] = str(value)
