#!/usr/bin/python

class qsodb:
    byid = {}  # qso database by src.seq
    bysfx = {}  # call list by suffix.band
    hiseq = {}  # high sequence number by node
    lock = threading.RLock()  # sharing lock

    def new(self, source):
        n = qsodb()
        n.src = source  # source id
        return n

    def tolog(self):  # make log file entry
        sqdb.log(self)  # to database
        self.lock.acquire()  # and to ascii journal file as well
        fd = file(logdbf, "a")
        fd.write("\nq|%s|%s|%s|%s|%s|%s|%s|%s|%s|" % \
                 (self.src, self.seq,
                  self.date, self.band, self.call, self.rept,
                  self.powr, self.oper, self.logr))
        fd.close()
        self.lock.release()

    def ldrec(self, line):  # load log entry fm text
        (dummy, self.src, self.seq,
         self.date, self.band, self.call, self.rept,
         self.powr, self.oper, self.logr, dummy) = string.split(line, '|')
        self.seq = int(self.seq)
        self.dispatch('logf')

    def loadfile(self):
        print "Loading Log File"
        i, s, log = 0, 0, []
        global sqdb # setup sqlite database connection
        sqdb = SQDB()
        log = sqdb.readlog()  # read the database
        for ln in log:
            if ln[0] == 'q':  # qso db line 
                r = qdb.new(0)
                try:
                    r.ldrec(ln)
                    i += 1
                except ValueError, e:
                    print "  error, item skipped: ", e
                    print "    in:", ln
                    s += 1
                    # sqdb.log(r)
                    #  push a copy from the file into the
                    # database (temporary for transition)
        if i == 0 and s == 1:
            print "Log file not found, must be new"
            initialize()  # Set up routine
        else:
            print "  ", i, "Records Loaded,", s, "Errors"
        if i == 0:
            initialize()

    def cleanlog(self):
        """return clean filtered dictionaries of the log"""
        d, c, g = {}, {}, {}
        fdstart, fdend = gd.getv('fdstrt'), gd.getv('fdend')
        self.lock.acquire()
        for i in self.byid.values():  # copy, index by node, sequence
            k = "%s|%s" % (i.src, i.seq)
            d[k] = i
        self.lock.release()
        for i in d.keys():  # process deletes
            if d.has_key(i):
                iv = d[i]
                if iv.rept[:5] == "*del:":
                    dummy, st, sn, dummy = iv.rept.split(':')  # extract deleted id
                    k = "%s|%s" % (st, sn)
                    if k in d.keys():
                        #  print iv.rept,; iv.pr()
                        del (d[k])  # delete it
                        # else: print "del target missing",iv.rept
                    del (d[i])
        for i in d.keys():  # filter time window
            iv = d[i]
            if iv.date < fdstart or iv.date > fdend:
                # print "discarding out of date range",iv.date,iv.src,iv.seq
                del (d[i])
        for i in d.values():  # re-index by call-band
            dummy, dummy, dummy, dummy, call, dummy, dummy = self.qparse(i.call)  # extract call (not /...)
            k = "%s-%s" % (call, i.band)
            # filter out noncontest entries
            if ival(i.powr) == 0 and i.band[0] != '*': continue
            if i.band == 'off': continue
            if i.band[0] == '*': continue  # rm special msgs
            if i.src == 'gotanode':
                g[k] = i  # gota is separate dup space
            else:
                c[k] = i
        return (d, c, g)  # Deletes processed, fully Cleaned
        # by id, call-bnd, gota by call-bnd

    def prlogln(self, s):
        "convert log item to print format"
        # note that edit and color read data from the editor so
        # changing columns matters to these other functions.
        if s.band == '*QST':
            ln = "%8s %5s %-41s %-3s %-3s %4s %s" % \
                 (s.date[4:11], s.band, s.rept[:41], s.oper, s.logr, s.seq, s.src)
        elif s.band == '*set':
            ln = "%8s %5s %-11s %-29s %-3s %-3s %4s %s" % \
                 (s.date[4:11], s.band, s.call[:10], s.rept[:29], s.oper, s.logr, s.seq, s.src)
        elif s.rept[:5] == '*del:':
            ln = "%8s %5s %-7s %-33s %-3s %-3s %4s %s" % \
                 (s.date[4:11], s.band, s.call[:7], s.rept[:33], s.oper, s.logr, s.seq, s.src)
        else:
            ln = "%8s %5s %-11s %-24s %4s %-3s %-3s %4s %s" % \
                 (s.date[4:11], s.band, s.call[:11], s.rept[:24], s.powr, s.oper, s.logr, s.seq, s.src)
        return ln


    def prlog(self):
        "print log in time order"
        l = self.filterlog("")
        for i in l:
            print i

    def pradif(self):
        "print clean log in adif format"
        pgm = "FDLog (https://github.com/scotthibbs/FDLog_Enhanced)"
        print "<PROGRAMID:%d>%s" % (len(pgm), pgm)
        dummy, n, g = self.cleanlog()
        for i in n.values() + g.values():
            dat = "20%s" % i.date[0:6]
            tim = i.date[7:11]
            cal = i.call
            bnd = "%sm" % i.band[:-1]
            mod = i.band[-1:]
            if mod == 'p':
                mod = 'SSB'
            elif mod == 'c':
                mod = 'CW'
            elif mod == 'd':
                mod = 'RTTY'
            com = i.rept
            print "<QSO_DATE:8>%s" % (dat)
            print "<TIME_ON:4>%s" % (tim)
            print "<CALL:%d>%s" % (len(cal), cal)
            print "<BAND:%d>%s" % (len(bnd), bnd)
            print "<MODE:%d>%s" % (len(mod), mod)
            print "<QSLMSG:%d>%s" % (len(com), com)
            print "<EOR>"
            print

    def vhf_cabrillo(self):
        "output VHF contest cabrillo QSO data"
        band_map = {'6': '50', '2': '144', '220': '222', '440': '432', '900': '902', '1200': '1.2G'}
        dummy, n, dummy = self.cleanlog()
        mycall = string.upper(gd.getv('fdcall'))
        mygrid = gd.getv('grid')
        l = []
        print "QSO: freq  mo date       time call              grid   call              grid "
        for i in n.values():  # + g.values(): no gota in vhf
            freq = "%s" % i.band[:-1]  # band
            if freq in band_map: freq = band_map[freq]
            mod = i.band[-1:]  # mode
            if mod == "c": mod = "CW"
            if mod == "p": mod = "PH"
            if mod == "d": mod = "RY"
            date = "20%2s-%2s-%2s" % (i.date[0:2], i.date[2:4], i.date[4:6])
            tim = i.date[7:11]
            call = i.call
            grid = ''
            if '/' in call:  # split off grid from call
                call, grid = call.split('/')
            l.append("%sQSO: %-5s %-2s %-10s %4s %-13s     %-6s %-13s     %-6s" % (
                i.date, freq, mod, date, tim, mycall, mygrid, call, grid))
        l.sort()  # sort data with prepended date.time
        for i in l: print i[13:]  # rm sort key date.time
# added support for winter field day, this outputs the cabrillo format that is posted on their website. 
    def winter_fd(self):
        "output Winter Field day QSO data in cabrillo format:"
        #vars:
        band_map = {'160': '1800', '80': '3500', '40': '7000', '20': '14000','15': '21000','10': '28000','6': '50', '2': '144', '220': '222', '440': '432', '900': '902', '1200': '1.2G'}
        dummy, n, dummy = self.cleanlog()
        l = []
        mycall = string.upper(gd.getv('fdcall'))
        mycat = gd.getv('class')
        mystate, mysect = gd.getv('sect').split("-")
        #number of tx
        txnum = mycat[:-1]
        #data crunching:
        
        #QSO log generation:
        for i in n.values():
            freq = "%s" % i.band[:-1]  # band
            #if freq in band_map: freq = band_map[freq]
            mod = i.band[-1:]  # mode
            if mod == "c": mod = "CW"
            if mod == "p": mod = "PH"
            if mod == "d": mod = "DI" # per 2019 rules
            date = "20%2s-%2s-%2s" % (i.date[0:2], i.date[2:4], i.date[4:6])
            #date = "%2s-%2s-20%2s" % (i.date[2:4], i.date[4:6], i.date[0:2])
            tim = i.date[7:11]
            call = i.call
            cat, sect = i.rept.split(" ")
            if '/' in call:  # split off grid from call
                call, grid = call.split('/')
            #cabrillo example: QSO:  40 DI 2019-01-19 1641 KC7SDA        1H  WWA    KZ9ZZZ        1H  NFL   
            l.append("%sQSO:  %-5s %-2s %-10s %4s %-10s %-2s  %-5s %-10s %-2s  %-5s" % (
                i.date,freq, mod, date, tim, mycall, mycat, mysect, call, cat, sect))
        l.sort()  # sort data with prepended date.time
        
        #check operator (single or multi op):
        cat_op = ""
        if len(participants) > 1:
            cat_op = "MULTI-OP"
        else:
            cat_op = "SINGLE-OP"
            
        #check fixed or portable?
        
        #tx power:
        
        #calls for ops:
        ops_calls_list = []
        #print(participants)
        #participants: {u'am': u'am, art miller, kc7sda, 37, '}
        for i in participants.values():
            dummy, dummy, cs, dummy, dummy = i.split(", ")
            ops_calls_list.append(string.upper(cs))
        ops_calls = ', '.join(ops_calls_list)
        
        #output
        print "Winter field day Cabrillo output"
        print "START-OF-LOG: 3.0"
        print "Created-By: FDLog (https://github.com/scotthibbs/FDLog_Enhanced)"
        print "CONTEST: WFD "
        print "CALLSIGN: " + mycall
        print "LOCATION: " + mystate
        print "ARRL-SECTION: " + mysect
        print "CATEGORY-OPERATOR: " + cat_op
        print "CATEGORY-STATION: " #fixed or portable
        print "CATEGORY_TRANSMITTER: " + txnum # how many transmitters
        print "CATEGORY_POWER: LOW" #qrp low or high
        print "CATEGORY_ASSISTED: NON-ASSISTED" #assisted or non-assisted
        print "CATEGORY-BAND: ALL" # leave for wfd
        print "CATEGORY-MODE: MIXED" #leave for wfd
        print "CATEGORY-OVERLAY: OVER-50" # leave for wfd
        print "SOAPBOX: " #fill in?
        print "CLAIMED-SCORE: " #figure out score and add
        print "OPERATORS: " + ops_calls #agregate the ops
        print "NAME: " + gd.getv('fmname')
        print "ADDRESS: " + gd.getv('fmad1')
        print "ADDRESS-CITY: " + gd.getv('fmcity')
        print "ADDRESS-STATE: " + gd.getv('fmst')
        print "ADDRES-POSTALCODE: " + gd.getv('fmzip') #zip
        print "ADDRESS-COUNTRY: USA" # hard coded for now, possibly change later
        print "EMAIL: " + gd.getv('fmem') #email address
        #print log:
        for i in l: print i[13:]  # rm sort key date.time
        print "END-OF-LOG:"

    def filterlog(self, filt):
        """list filtered (by bandm) log in time order, nondup valid q's only"""
        l = []
        dummy, n, g = self.cleanlog()
        for i in n.values() + g.values():
            if filt == "" or re.match('%s$' % filt, i.band):
                l.append(i.prlogln(i))
        l.sort()
        return l

    def filterlog2(self, filt):
        "list filtered (by bandm) log in time order, including special msgs"
        l = []
        m, dummy, dummy = self.cleanlog()
        for i in m.values():
            if filt == "" or re.match('%s$' % filt, i.band):
                l.append(i.prlogln(i))
        l.sort()
        return l

    def filterlogst(self, filt):
        "list filtered (by nod) log in time order, including special msgs"
        l = []
        m, dummy, dummy = self.cleanlog()
        for i in m.values():
            if re.match('%s$' % filt, i.src):
                l.append(i.prlogln(i))
        l.sort()
        return l

    def qsl(self, time, call, bandmod, report):
        "log a qsl"
        return self.postnewinfo(time, call, bandmod, report)

    def qst(self, msg):
        "put a qst in database + log"
        return self.postnewinfo(now(), '', '*QST', msg)

    def globalshare(self, name, value):
        "put global var set in db + log"
        return self.postnewinfo(now(), name, '*set', value)

    def postnewinfo(self, time, call, bandmod, report):
        "post new locally generated info"
        # s = self.new(node)
        #        s.date,s.call,s.band,s.rept,s.oper,s.logr,s.powr =
        #            time,call,bandmod,report,exin(operator),exin(logger),power
        # s.seq = -1
        return self.postnew(time, call, bandmod, report, exin(operator),
                            exin(logger), power)
        # s.dispatch('user') # removed in 152i

    def postnew(self, time, call, bandmod, report, oper, logr, powr):
        "post new locally generated info"
        s = self.new(node)
        s.date, s.call, s.band, s.rept, s.oper, s.logr, s.powr = time, call, bandmod, report, oper, logr, powr
        s.seq = -1
        return s.dispatch('user')

    def delete(self, nod, seq, reason):
        "remove a Q by creating a delete record"
        #        print "del",nod,seq
        a, dummy, dummy = self.cleanlog()
        k = "%s|%s" % (nod, seq)
        if a.has_key(k) and a[k].band[0] != '*':  # only visible q
            tm, call, bandmod = a[k].date, a[k].call, a[k].band
            rept = "*del:%s:%s:%s" % (nod, seq, reason)
            s = self.new(node)
            s.date, s.call, s.band, s.rept, s.oper, s.logr, s.powr = \
                now(), call, bandmod, rept, exin(operator), exin(logger), 0
            s.seq = -1
            s.dispatch('user')
            txtbillb.insert(END, " DELETE Successful %s %s %s\n" % (tm, call, bandmod))
            logw.configure(state=NORMAL)
            logw.delete(0.1,END)
            logw.insert(END, "\n")
            # Redraw the logw text window (on delete) to only show valid calls in the log. 
            # This avoids confusion by only listing items in the log to edit in the future.
            l = []
            for i in sorted(a.values()):
                if i.seq == seq:
                    continue
                else:
                    l.append(logw.insert(END, "\n"))
                    if nod == node:
                        l.append(logw.insert(END, i.prlogln(i), "b"))    
                    else:
                        l.append(logw.insert(END, i.prlogln(i)))
                        l.append(logw.insert(END, "\n"))
            logw.insert(END, "\n")
            logw.configure(state=DISABLED)
        else:
            txtbillb.insert(END, " DELETE Ignored [%s,%s] Not Found\n" % (nod, seq))
            topper()

    def todb(self):
        """"Q record object to db"""
        r = None
        self.lock.acquire()
        current = self.hiseq.get(self.src, 0)
        self.seq = int(self.seq)
        if self.seq == current + 1:  # filter out dup or nonsequential
            self.byid["%s.%s" % (self.src, self.seq)] = self
            self.hiseq[self.src] = current + 1
            #            if debug: print "todb:",self.src,self.seq
            r = self
        elif self.seq == current:
            if debug: print "dup sequence log entry ignored"
        else:
            print "out of sequence log entry ignored", self.seq, current + 1
        self.lock.release()
        return r

    def pr(self):
        """"print Q record object"""
        sms.prmsg(self.prlogln(self))

    def dispatch(self, src):
        """"process new db rec (fm logf,user,net) to where it goes"""
        self.lock.acquire()
        self.seq = int(self.seq)
        if self.seq == -1:  # assign new seq num
            self.seq = self.hiseq.get(self.src, 0) + 1
        r = self.todb()
        self.lock.release()
        if r:  # if new
            self.pr()
            if src != 'logf': self.tolog()
            if src == 'user': net.bc_qsomsg(self.src, self.seq)
            if self.band == '*set':
                m = gd.setv(r.call, r.rept, r.date)
                if not m: r = None
            else:
                self.logdup()
        return r

    def bandrpt(self):
        """band report q/band pwr/band, q/oper q/logr q/station"""
        qpb, ppb, qpop, qplg, qpst, tq, score, maxp = {}, {}, {}, {}, {}, 0, 0, 0
        cwq, digq, fonq = 0, 0, 0
        qpgop, gotaq, nat, sat = {}, 0, [], []
        dummy, c, g = self.cleanlog()
        for i in c.values() + g.values():
            if re.search('sat', i.band): sat.append(i)
            if 'n' in i.powr: nat.append(i)
            # stop ignoring above 100 q's per oper per new gota rules
            # GOTA q's stop counting over 400 (500 in 2009)
            if i.src == 'gotanode':  # analyze gota limits
                qpgop[i.oper] = qpgop.get(i.oper, 0) + 1
                qpop[i.oper] = qpop.get(i.oper, 0) + 1
                qplg[i.logr] = qplg.get(i.logr, 0) + 1
                qpst[i.src] = qpst.get(i.src, 0) + 1
                if gotaq >= 500: continue  # stop over 500 total
                gotaq += 1
                tq += 1
                score += 1
                if 'c' in i.band:
                    cwq += 1
                    score += 1
                    qpb['gotac'] = qpb.get('gotac', 0) + 1
                    ppb['gotac'] = max(ppb.get('gotac', 0), ival(i.powr))
                if 'd' in i.band:
                    digq += 1
                    score += 1
                    qpb['gotad'] = qpb.get('gotad', 0) + 1
                    ppb['gotad'] = max(ppb.get('gotad', 0), ival(i.powr))
                if 'p' in i.band:
                    fonq += 1
                    qpb['gotap'] = qpb.get('gotap', 0) + 1
                    ppb['gotap'] = max(ppb.get('gotap', 0), ival(i.powr))
                continue
            qpb[i.band] = qpb.get(i.band, 0) + 1
            ppb[i.band] = max(ppb.get(i.band, 0), ival(i.powr))
            maxp = max(maxp, ival(i.powr))
            qpop[i.oper] = qpop.get(i.oper, 0) + 1
            qplg[i.logr] = qplg.get(i.logr, 0) + 1
            qpst[i.src] = qpst.get(i.src, 0) + 1
            score += 1
            tq += 1
            if 'c' in i.band:
                score += 1  # extra cw and dig points
                cwq += 1
            if 'd' in i.band:
                score += 1
                digq += 1
            if 'p' in i.band:
                fonq += 1
        return (qpb, ppb, qpop, qplg, qpst, tq, score, maxp, cwq, digq, fonq, qpgop, gotaq, nat, sat)

    def bands(self):
        """ .ba command band status station on, q/band, xx needs upgd"""
        # This function from 152i
        qpb, tmlq, dummy = {}, {}, {}
        self.lock.acquire()
        for i in self.byid.values():
            if ival(i.powr) < 1: continue
            if i.band == 'off': continue
            v = 1
            if i.rept[:5] == '*del:': v = -1
            qpb[i.band] = qpb.get(i.band, 0) + v  # num q's
            tmlq[i.band] = max(tmlq.get(i.band, ''), i.date)  # time of last (latest) q
        self.lock.release()
        print
        print "Stations this node is hearing:"
        # scan for stations on bands
        for s in net.si.nodes.values():  # xx
            # print dir(s)
            print s.nod, s.host, s.ip, s.stm
            # nod[s.bnd] = s.nod_on_band()
            # print "%8s %4s %18s %s"%(s.nod,s.bnd,s.msc,s.stm)
            # s.stm,s.nod,seq,s.bnd,s.msc
            # i.tm,i.fnod,i.fip,i.stm,i.nod,i.seq,i.bnd,i.msc
        d = {}
        print
        print "Node Info"
        print "--node-- band --opr lgr pwr----- last"
        for t in net.si.nodinfo.values():
            dummy, dummy, age = d.get(t.nod, ('', '', 9999))
            if age > t.age: d[t.nod] = (t.bnd, t.msc, t.age)
        for t in d:
            print "%8s %4s %-18s %4s" % (t, d[t][0], d[t][1], d[t][2])  # t.bnd,t.msc,t.age)
        print
        print "  band -------- cw ----- ------- dig ----- ------- fon -----"
        print "          nod  Q's  tslq    nod  Q's  tslq    nod  Q's  tslq"
        #      xxxxxx yyyyyy xxxx xxxxx yyyyyy xxxx xxxxx yyyyyy xxxx xxxxx
        t1 = now()
        for b in (160, 80, 40, 20, 15, 10, 6, 2, 220, 440, 900, 1200, 'Sat'):
            print "%6s" % b,
            for m in 'cdp':
                bm = "%s%s" % (b, m)
                # be nice to do min since q instead of time of last q --- DONE
                t2 = tmlq.get(bm, '')  # time since last Q minutes
                if t2 == '':
                    tdif = ''
                else:
                    tdif = int(tmsub(t1, t2) / 60.)
                    tmin = tdif % 60
                    tdhr = tdif / 60
                    if tdhr > 99: tdhr = 99
                    tdif = tdhr * 100 + tmin
                    #    if tdif > 9999: tdif = 9999
                    #    tdif = str(int(tdif))           # be nice to make this hhmm instead of mmmm
                #  t = "" # time of latest Q hhmm
                #  m = re.search(r"([0-9]{4})[0-9]{2}$",tmlq.get(bm,''))
                #  if m: t = m.group(1)
                nob = net.si.nod_on_band(bm)  # node now on band
                if len(nob) == 0:
                    nob = ''  # list take first item if any
                else:
                    nob = nob[0]
                print "%6s %4s %5s" % \
                      (nob[0:6], qpb.get(bm, ''), tdif),  # was t
                #    (nod.get(bm,'')[0:5],qpb.get(bm,''),t),
            print

    def sfx2call(self, suffix, band):
        """return calls w suffix on this band"""
        return self.bysfx.get(suffix + '.' + band, [])

    def qparse(self, line):
        """"qso/call/partial parser"""
        # check for valid input at each keystroke
        # return status, time, extended call, base call, suffix, report
        # stat: 0 invalid, 1 partial, 2 suffix, 3 prefix, 4 call, 5 full qso
        # example --> :12.3456 wb4ghj/ve7 2a sf Steve in CAN
        stat, tm, pfx, sfx, call, xcall, rept = 0, '', '', '', '', '', ''
        # break into basic parts: time, call, report
        m = re.match(r'(:([0-9.]*)( )?)?(([a-z0-9/]+)( )?)?([0-9a-zA-Z ]*)$', line)
        if m:
            tm = m.group(2)
            xcall = m.group(5)
            rept = m.group(7)
            stat = 0
            if m.group(1) > '' or xcall > '': stat = 1
            #            print; print "tm [%s] xcall [%s] rept [%s]"%(tm,xcall,rept)
            if tm > '':
                stat = 0
                m = re.match(r'([0-3]([0-9]([.]([0-5]([0-9]([0-5]([0-9])?)?)?)?)?)?)?$', tm)
                if m:
                    stat = 1  # at least partial time
            if xcall > '':
                stat = 0  # invalid unless something matches
                m = re.match(r'([a-z]+)$', xcall)
                if m:
                    stat = 2  # suffix
                    sfx = xcall
                m = re.match(r'([0-9]+)$', xcall)
                if m:
                    stat = 2  # suffix
                    sfx = xcall
                m = re.match(r'([a-z]+[0-9]+)$', xcall)
                if m:
                    stat = 3  # prefix
                    pfx = xcall
                m = re.match(r'([0-9]+[a-z]+)$', xcall)
                if m:
                    stat = 3  # prefix
                    pfx = xcall
                m = re.match(r'(([a-z]+[0-9]+)([a-z]+))(/[0-9a-z]*)?$', xcall)
                if m:
                    stat = 4  # whole call
                    call = m.group(1)
                    pfx = m.group(2)
                    sfx = m.group(3)
                m = re.match(r'(([0-9]+[a-z]+)([0-9]+))(/[0-9a-z]*)?$', xcall)
                if m:
                    stat = 4  # whole call
                    call = m.group(1)
                    pfx = m.group(2)
                    sfx = m.group(3)
                if (stat == 4) & (rept > ''):
                    stat = 0
                    m = re.match(r'[0-9a-zA-Z]+[0-9a-zA-Z ]*$', rept)
                    if m:
                        stat = 5  # complete qso
                if len(xcall) > 12: stat = 0  # limit lengths
                if len(pfx) > 5: stat = 0
                if len(sfx) > 3: stat = 0
                if tm:  # if forced time exists
                    if len(tm) < 7:  # it must be complete
                        stat = 0
                        #        print "stat[%s] time[%s] pfx[%s] sfx[%s] call[%s] xcall[%s] rpt[%s]"%\
                        #              (stat,tm,pfx,sfx,call,xcall,rept)
        return (stat, tm, pfx, sfx, call, xcall, rept)

    def dupck(self, wcall, band):
        """check for duplicate call on this band"""
        dummy, dummy, dummy, sfx, call, xcall, dummy = self.qparse(wcall)
        if gd.getv('contst').upper() == "VHF":
            return xcall in self.sfx2call(sfx, band)  # vhf contest
        return call in self.sfx2call(sfx, band)  # field day

    # Added function to test against participants like dupes
    # Added function to test against call and gota call like dupes
    def partck(self, wcall):
        """ check for participants to act as dupes in this event"""
        dummy, dummy, dummy, dummy, call, xcall, dummy = self.qparse(wcall)
        l = []
        for i in participants.values():
            l.append(i)
            dummy, dummy, dcall, dummy, dummy = string.split(i, ', ')
            if dcall == xcall:
                # to debug: print ("%s dcall matches %s xcall" % (dcall, xcall))
                if gd.getv('contst').upper() == "VHF":
                    return xcall  # vhf contest
                return call # field day
            if dcall == call:
                #to debug: print ("%s dcall matches %s call" % (dcall, call))
                if gd.getv('contst').upper() == "VHF":
                    return xcall # vhf contest
                return call # field day

    def logdup(self):
        """enter into dup log"""
        dummy, dummy, dummy, sfx, dummy, xcall, dummy = self.qparse(self.call)
        #        print call,sfx,self.band
        key = sfx + '.' + self.band
        self.lock.acquire()
        if self.rept[:5] == "*del:":
            self.redup()
        else:
            # duplog everything with nonzero power, or on band off (test)
            if (self.band == 'off') | (ival(self.powr) > 0):
                # dup only if Q and node type match (gota/not)
                if (node == 'gotanode') == (self.src == 'gotanode'):
                    if self.bysfx.has_key(key):  # add to suffix db
                        self.bysfx[key].append(xcall)
                    else:
                        self.bysfx[key] = [xcall]
                        #                else: print "node type mismatch",node,self.src
        self.lock.release()

    def redup(self):
        """rebuild dup db"""
        dummy, c, g = self.cleanlog()
        self.lock.acquire()
        #        print self.bysfx
        qsodb.bysfx = {}
        for i in c.values() + g.values():
            #            print i.call,i.band
            i.logdup()
        self.lock.release()
        #        print qsodb.bysfx

    def wasrpt(self):
        """worked all states report"""
        sectost, stcnt, r, e = {}, {}, [], []
        try:
            fd = file("Arrl_sect.dat", "r")  # read section data
            while 1:
                ln = fd.readline()  # read a line and put in db
                if not ln: break
                # if ln == "": continue
                if ln[0] == '#': continue
                try:
                    sec, st, dummy, dummy = string.split(ln, None, 3)
                    sectost[sec] = st
                    stcnt[st] = 0
                #                    print sec,st,desc
                except ValueError, e:
                    print "rd arrl sec dat err, itm skpd: ", e
            fd.close()
        except IOError, e:
            print "io error during arrl section data file load", e
        a, dummy, dummy = self.cleanlog()
        for i in a.values():
            sect, state = "", ""
            if i.rept[:1] == '*': continue
            if i.band[0] == '*': continue
            if i.band == 'off': continue
            if i.powr == '0': continue
            m = re.match(r' *[0-9]+[a-fiohA-FIOH] +([A-Za-z]{2,4})', i.rept)
            if m:
                sect = m.group(1)
                sect = string.upper(sect)
                state = sectost.get(sect, "")
                #                print "sec",sect,"state",state
                if state: stcnt[state] += 1
            if not state:
                #                print "section not recognized in:\n  %s"%i.prlogln()
                #                print "sec",sect,"state",state
                e.append(i.prlogln(i))
        h, n = [], []  # make have and need lists
        for i in stcnt.keys():
            if i != "--":
                if stcnt[i] == 0:
                    n.append("%s" % i)
                else:
                    h.append("%s" % i)
        n.sort()
        r.append("Worked All States Report\n%s Warning(s) Below\nNeed %s States:" % (len(e), len(n)))
        for i in n:
            r.append(i)
        h.sort()
        r.append("\nHave %s States:" % len(h))
        for i in h:
            r.append("%s %s" % (i, stcnt[i]))
        if len(e) > 0:
            r.append("\nWarnings - Cannot Discern US Section in Q(s):\n")
            for i in e:
                r.append(i)
        return r
