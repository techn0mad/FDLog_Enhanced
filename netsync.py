#!/usr/bin/python

class netsync:
    """network database synchronization"""
	# removed netmask - it isn't used anywhere in the program from what I can tell (do a search for 'netmask' this is the only place you find it)
	# re-coded the ip address calculation to smooth it out and make it cross platform compatible
    #netmask = '255.255.255.0'
    rem_adr = ""  # remote bc address
    authkey = hashlib.md5()
    pkts_rcvd, fills, badauth_rcvd, send_errs = 0, 0, 0, 0
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
            s.connect(("8.8.8.8", 53))
            my_addr = s.getsockname()[0]
    except:
            my_addr = '127.0.0.1'
    finally:
            s.close()
    print "\n IP address is:  %s\n" % my_addr
    bc_addr = re.sub(r'[0-9]+$', '255', my_addr)  # calc bcast addr
    si = node_info()  # node info

    def setport(self, useport):
        """set net port"""
        self.port = useport
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # send socket
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Eric's linux fix
        self.skt.bind((self.my_addr, self.port + 1))

    def setauth(self, newauth):
        """set authentication key code base, copy on use"""
        global authk
        authk = newauth
        seed = "2004070511111akb"  # change when protocol changes

        # self.authkey = md5.new(newauth+seed)
        self.authkey = hashlib.md5(newauth + seed)

    def auth(self, msg):
        """calc authentication hash"""
        h = self.authkey.copy()
        h.update(msg)
        return h.hexdigest()

    def ckauth(self, msg):
        """check authentication hash"""
        h, m = msg.split('\n', 1)
        #        print h; print self.auth(m); print
        return h == self.auth(m)

    def sndmsg(self, msg, addr):
        """send message to address list"""
        if authk != "" and node != "":
            amsg = self.auth(msg) + '\n' + msg
            addrlst = []
            if addr == 'bcast':
                addrlst.append(self.bc_addr)
            else:
                addrlst.append(addr)
            for a in addrlst:
                if a == "": continue
                if a == '0.0.0.0': continue
                if debug: print "send to ", a; print msg
                try:
                    self.skt.sendto(amsg, (a, self.port))
                except socket.error, e:
                    self.send_errs += 1
                    print "error, pkt xmt failed %s %s [%s]" % (now(), e.args, a)

    def send_qsomsg(self, nod, seq, destip):
        """send q record"""
        key = nod + '.' + str(seq)
        if qdb.byid.has_key(key):
            i = qdb.byid[key]
            msg = "q|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % \
                  (i.src, i.seq, i.date, i.band, i.call, i.rept, i.powr, i.oper, i.logr)
            self.sndmsg(msg, destip)

    def bc_qsomsg(self, nod, seq):
        """broadcast new q record"""
        self.send_qsomsg(nod, seq, self.bc_addr)

    def bcast_now(self):
        msg = "b|%s|%s|%s|%s|%s|%s\n" % \
              (self.hostname, self.my_addr, node, now(), mclock.level, version)
        for i in self.si.node_status_list():
            msg += "s|%s|%s|%s|%s|%s\n" % i  # nod,seq,bnd,msc,age
            # if debug: print i
        self.sndmsg(msg, 'bcast')  # broadcast it

    def fillr(self):
        """filler thread requests missing database records"""
        time.sleep(0.2)
        if debug: print "filler thread starting"

        while 1:
            time.sleep(.1)  # periodically check for fills
            if debug: time.sleep(1)  # slow for debug
            r = self.si.fill_requests_list()
            self.fills = len(r)
            if self.fills:
                p = random.randrange(0, len(r))  # randomly select one
                c = r[p]
                msg = "r|%s|%s|%s\n" % (self.my_addr, c[1], c[2])  # (addr,src,seq)
                self.sndmsg(msg, c[0])
                print "req fill", c

    def rcvr(self):
        """receiver thread processes incoming packets"""
        if debug: print "receiver thread starting"
        r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r.bind(('', self.port))
        while 1:
            msg, addr = r.recvfrom(800)
            if addr[0] != self.my_addr:
                self.pkts_rcvd += 1
            # if authk == "": continue             # skip till auth set
            pkt_tm = now()
            host, sip, fnod, stm = '', '', '', ''
            if debug: print "rcvr: %s: %s" % (addr, msg),  # xx
            if not self.ckauth(msg):  # authenticate packet
                # if debug: sms.prmsg("bad auth from: %s"%addr)
                print "bad auth from:", addr
                self.badauth_rcvd += 1
            else:
                lines = msg.split('\n')  # decode lines
                for line in lines[1:-1]:  # skip auth hash, blank at end
                    #                    if debug: sms.prmsg(line)
                    fields = line.split('|')
                    if fields[0] == 'b':  # status bcast
                        host, sip, fnod, stm, stml, ver = fields[1:]
                        td = tmsub(stm, pkt_tm)
                        self.si.ssb(pkt_tm, host, sip, fnod, stm, stml, ver, td)
                        mclock.calib(fnod, stml, td)
                        if abs(td) >= tdwin:
                            print 'Incoming packet clock error', td, host, sip, fnod, pkt_tm
                        if showbc:
                            print "bcast", host, sip, fnod, ver, pkt_tm, td
                    elif fields[0] == 's':  # source status
                        nod, seq, bnd, msc, age = fields[1:]
                        # if debug: print pkt_tm,fnod,sip,stm,nod,seq,bnd,msc
                        self.si.sss(pkt_tm, fnod, sip, nod, seq, bnd, msc, age)
                    elif fields[0] == 'r':  # fill request
                        destip, src, seq = fields[1:]
                        # if debug: print destip,src,seq
                        self.send_qsomsg(src, seq, destip)
                    elif fields[0] == 'q':  # qso data
                        src, seq, stm, b, c, rp, p, o, l = fields[1:]
                        # if debug: print src,seq,stm,b,c,rp,p,o,l
                        self.si.sqd(src, seq, stm, b, c, rp, p, o, l)
                    else:
                        sms.prmsg("msg not recognized %s" % addr)

    def start(self):
        """launch all threads"""
        #        global node
        print "This host:", self.hostname, "IP:", self.my_addr, "Mask:", self.bc_addr
        #        if (self.hostname > "") & (node == 's'):
        #            node = self.hostname             # should filter chars
        #        print "Node ID:",node
        print "Launching threads"
        #        thread.start_new_thread(self.bcastr,())
        thread.start_new_thread(self.fillr, ())
        thread.start_new_thread(self.rcvr, ())
        if debug:
            print "threads launched"
        time.sleep(0.5)  # let em print
        print "Startup complete"
