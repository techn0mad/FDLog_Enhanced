#!/usr/bin/python 

class node_info:
    """Threads and networking section"""
    nodes = {}
    nodinfo = {}
    # rembcast = {}
    #  This was not remarked out of the 2015_stable version
    lock = threading.RLock()  # reentrant sharing lock

    def sqd(self, src, seq, t, b, c, rp, p, o, l):
        """process qso data fm net into db"""  # excessive cohesion?
        s = qdb.new(src)
        s.seq, s.date, s.call, s.band, s.rept, s.oper, s.logr, s.powr = \
            seq, t, c, b, rp, o, l, p
        s.dispatch('net')

    def netnum(self, ip, mask):
        """extract net number"""
        i, m, r = [], [], {}
        i = string.split(ip, '.')
        m = string.split(mask, '.')
        for n in (0, 1, 2, 3):
            r[n] = ival(i[n]) & ival(m[n])
        return "%s.%s.%s.%s" % (r[0], r[1], r[2], r[3])

    def ssb(self, pkt_tm, host, sip, nod, stm, stml, ver, td):
        """process status broadcast (first line)"""
        self.lock.acquire()
        if not self.nodes.has_key(nod):  # create if new
            self.nodes[nod] = node_info()
            if nod != node:
                print "New Node Heard", host, sip, nod, stm, stml, ver, td
        i = self.nodes[nod]
        #        if debug: print "ssb before assign",i.nod,i.stm,i.bnd
        i.ptm, i.nod, i.host, i.ip, i.stm, i.age = \
            pkt_tm, nod, host, sip, stm, 0
        self.lock.release()
        #   if debug:
        #  print "ssb:",pkt_tm,host,sip,nod,stm,stml,ver,td

    def sss(self, pkt_tm, fnod, sip, nod, seq, bnd, msc, age):
        """process node status bcast (rest of bcast lines)"""
        self.lock.acquire()
        key = "%s-%s" % (fnod, nod)
        if not self.nodinfo.has_key(key):
            self.nodinfo[key] = node_info()  # create new
            #            if debug: print "sss: new nodinfo instance",key
        i = self.nodinfo[key]
        i.tm, i.fnod, i.fip, i.nod, i.seq, i.bnd, i.msc, i.age = \
            pkt_tm, fnod, sip, nod, seq, bnd, msc, int(age)
        self.lock.release()
        #        if debug: print "sss:",i.age,i.nod,i.seq,i.bnd

    def age_data(self):
        """increment age and delete old band"""
        # updates from 152i
        t = now()[7:]  # time hhmmss
        self.lock.acquire()
        for i in self.nodinfo.values():
            if i.age < 999:
                i.age += 1
                # if debug: print "aging nodinfo",i.fnod,i.nod,i.bnd,i.age
            if i.age > 55 and i.bnd:
                print t, "age out info from", i.fnod, "about", i.nod, "on", i.bnd, "age", i.age
                i.bnd = ""
        for i in self.nodes.values():
            if i.age < 999: i.age += 1
        self.lock.release()

    def fill_requests_list(self):
        """return list of fills needed"""
        r = []
        self.lock.acquire()
        for i in self.nodinfo.values():  # for each node
            j = qdb.hiseq.get(i.nod, 0)
            if int(i.seq) > j:  # if they have something we need
                r.append((i.fip, i.nod, j + 1))  # add req for next to list
                # if debug: print "req fm",i.fip,"for",i.nod,i.seq,"have",j+1
        self.lock.release()
        return r  # list of (addr,src,seq)

    def node_status_list(self):
        """return list of node status tuples"""
        sum = {}  # summary dictionary
        self.lock.acquire()
        i = node_info()  # update our info
        i.nod, i.bnd, i.age = node, band, 0
        i.msc = "%s %s %sW" % (exin(operator), exin(logger), power)
        sum[node] = i
        for i in qdb.hiseq.keys():  # insure all db nod on list
            if not sum.has_key(i):  # add if new
                j = node_info()
                j.nod, j.bnd, j.msc, j.age = i, '', '', 999
                sum[i] = j
                # if debug: print "adding nod fm db to list",i
        for i in self.nodinfo.values():  # browse bcast data
            if not sum.has_key(i.nod):
                j = node_info()
                j.nod, j.bnd, j.msc, j.age = i.nod, '', '', 999
                sum[i.nod] = j
            j = sum[i.nod]  # collect into summary
            #            if debug:
            #                print "have",      j.nod,j.age,j.bnd,j.msc
            #                print "inspecting",i.nod,i.age,i.bnd,i.msc
            if i.age < j.age:  # keep latest wrt src time
                #                if debug:
                #                    print "updating",j.nod,j.age,j.bnd,j.msc,\
                #                                "to",      i.age,i.bnd,i.msc
                j.bnd, j.msc, j.age = i.bnd, i.msc, i.age
        self.lock.release()
        r = []  # form the list (xx return sum?)
        for s in sum.values():
            seq = qdb.hiseq.get(s.nod, 0)  # reflect what we have in our db
            if seq or s.bnd:  # only report interesting info
                r.append((s.nod, seq, s.bnd, s.msc, s.age))
        return r  # list of (nod,seq,bnd,msc,age)

    def nod_on_band(self, band):
        """return list of nodes on this band"""
        r = []
        for s in self.node_status_list():
            # print s[0],s[2] # (nod,seq,bnd,msc,age)
            if band == s[2]:
                r.append(s[0])
        return r

    def nod_on_bands(self):
        """return dictionary of list of nodes indexed by band and counts"""
        r, hf, vhf, gotanode = {}, 0, 0, 0
        for s in self.node_status_list():
            #            print s[0],s[2]
            if not r.has_key(s[2]):
                r[s[2]] = []
            r[s[2]].append(s[0])
            if s[2] == 'off' or s[2] == "": continue
            if s[0] == 'gotanode':
                gotanode += 1
            else:
                b = ival(s[2])
                if b > 8 or b < 200: hf += 1
                if b < 8 or b > 200: vhf += 1
        return r, hf, vhf, gotanode
