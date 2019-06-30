#!/usr/bin/python

# sqlite database upgrade
# sqlite3.connect(":memory:", check_same_thread = False)
# I found this online to correct thread errors with sql locking to one thread only.
# I'm pretty sure I emailed this fix to Alan Biocca over a year ago. :(
# Scott Hibbs 7/5/2015


class SQDB:
    def __init__(self):
        self.dbPath = logdbf[0:-4] + '.sq3'
        print "Using database", self.dbPath
        self.sqdb = sqlite3.connect(self.dbPath, check_same_thread=False)  # connect to the database
        # Have to add FALSE here to get this stable
        self.sqdb.row_factory = sqlite3.Row  # namedtuple_factory
        self.curs = self.sqdb.cursor()  # make a database connection cursor
        sql = "create table if not exists qjournal(src text,seq int,date text,band " \
              "text,call text,rept text,powr text,oper text,logr text,primary key (src,seq))"
        self.curs.execute(sql)
        self.sqdb.commit()

    def readlog(self):  # ,srcId,srcIdx):            # returns list of log journal items
        print "Loading log journal from sqlite database"
        sql = "select * from qjournal"
        result = self.curs.execute(sql)
        nl = []
        for r in result:
            # print dir(r)
            nl.append("|".join(('q', r['src'], str(r['seq']), r['date'], r['band'], r['call'], r['rept'], r['powr'],
                                r['oper'], r['logr'], '')))
        # print nl
        return nl

    # Removed next(self) function. There is no self.result
    # and nothing calls sqdb.next()

    # def next(self):  # get next item from db in text format
    #     n = self.result
    #     nl = "|".join(n.src, n['seq'], n['date'], n['band'], n['call'], n['rept'], n['powr'], n['oper'], n['logr'])
    #     return nl

    def log(self, n):  # add item to journal logfile table (and other tables...)
        parms = (n.src, n.seq, n.date, n.band, n.call, n.rept, n.powr, n.oper, n.logr)
        sqdb = sqlite3.connect(self.dbPath)  # connect to the database
        #        self.sqdb.row_factory = sqlite3.Row   # namedtuple_factory
        curs = sqdb.cursor()  # make a database connection cursor
        # start commit, begin transaction
        sql = "insert into qjournal (src,seq,date,band,call,rept,powr,oper,logr) values (?,?,?,?,?,?,?,?,?)"
        curs.execute(sql, parms)
        # sql = "insert into qsos values (src,seq,date,band,call,sfx,rept,powr,oper,logr),(?,?,?,?,?,?,?,?,?,?)"
        # self.cur(sql,parms)
        # update qso count, scores? or just use q db count? this doesn't work well for different weights
        # update sequence counts for journals?
        sqdb.commit()  # do the commit
        if n.band == '*QST':
            print("QST\a " + n.rept+" -"+n.logr)  # The "\a" emits the beep sound for QST
