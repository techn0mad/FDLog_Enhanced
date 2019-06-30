#!/usr/bin/python 

class Edit_Dialog(Toplevel):
    """edit log entry dialog"""
    """Added functionality to check for dupes and change the title to show the error"""
    # Had to add variables for each text box to know if they changed to do dupe check.
    global editedornot 
    editedornot = StringVar
    crazytxt = StringVar()
    crazytxt.set('Edit Log Entry')
    crazyclr = StringVar()
    crazyclr.set('lightgrey')
    crazylbl = Label

    def __init__(self, parent, node, seq):
        s = '%s.%s' % (node, seq)
        self.node, self.seq = node, seq
        if qdb.byid[s].band[0] == '*': return
        top = self.top = Toplevel(parent)
        # Toplevel.__init__(self,parent)
        # self.transient(parent)     # avoid showing as separate item
        self.crazytxt.set('Edit Log Entry')
        self.crazyclr.set('lightgrey')
        self.crazylbl = tl = Label(top, text=self.crazytxt.get(), font=fdbfont, bg=self.crazyclr.get(), relief=RAISED)
        # tl = Label(top, text='Edit Log Entry', font=fdbfont, bg='lightgrey', relief=RAISED)
        tl.grid(row=0, columnspan=2, sticky=EW)
        tl.grid_columnconfigure(0, weight=1)
        Label(top, text='Date', font=fdbfont).grid(row=1, sticky=W)
        # Label(top,text='Time',font=fdbfont).grid(row=2,sticky=W)
        Label(top, text='Band', font=fdbfont).grid(row=3, sticky=W)
        # Label(top,text='Mode',font=fdbfont).grid(row=4,sticky=W)
        Label(top, text='Call', font=fdbfont).grid(row=5, sticky=W)
        Label(top, text='Report', font=fdbfont).grid(row=6, sticky=W)
        Label(top, text='Power', font=fdbfont).grid(row=7, sticky=W)
        # Label(top,text='Natural',font=fdbfont).grid(row=8,sticky=W)
        Label(top, text='Operator', font=fdbfont).grid(row=9, sticky=W)
        Label(top, text='Logger', font=fdbfont).grid(row=10, sticky=W)
        self.de = Entry(top, width=13, font=fdbfont)
        self.de.grid(row=1, column=1, sticky=W, padx=3, pady=2)
        self.de.insert(0, qdb.byid[s].date)
        self.chodate = qdb.byid[s].date
        self.be = Entry(top, width=5, font=fdbfont)
        self.be.grid(row=3, column=1, sticky=W, padx=3, pady=2)
        # self.be.configure(bg='gold') # test yes works
        self.be.insert(0, qdb.byid[s].band)
        self.choband = qdb.byid[s].band
        self.ce = Entry(top, width=11, font=fdbfont)
        self.ce.grid(row=5, column=1, sticky=W, padx=3, pady=2)
        self.ce.insert(0, qdb.byid[s].call)
        self.chocall = qdb.byid[s].call
        self.re = Entry(top, width=24, font=fdbfont)
        self.re.grid(row=6, column=1, sticky=W, padx=3, pady=2)
        self.re.insert(0, qdb.byid[s].rept)
        self.chorept = qdb.byid[s].rept
        self.pe = Entry(top, width=5, font=fdbfont)
        self.pe.grid(row=7, column=1, sticky=W, padx=3, pady=2)
        self.pe.insert(0, qdb.byid[s].powr)
        self.chopowr = qdb.byid[s].powr
        self.oe = Entry(top, width=3, font=fdbfont)
        self.oe.grid(row=9, column=1, sticky=W, padx=3, pady=2)
        self.oe.insert(0, qdb.byid[s].oper)
        self.chooper = qdb.byid[s].oper
        self.le = Entry(top, width=3, font=fdbfont)
        self.le.grid(row=10, column=1, sticky=W, padx=3, pady=2)
        self.le.insert(0, qdb.byid[s].logr)
        self.chologr = qdb.byid[s].logr
        bf = Frame(top)
        bf.grid(row=11, columnspan=2, sticky=EW, pady=2)
        bf.grid_columnconfigure((0, 1, 2), weight=1)
        db = Button(bf, text=' Delete ', font=fdbfont, command=self.dele)
        db.grid(row=1, sticky=EW, padx=3)
        sb = Button(bf, text=' Save ', font=fdbfont, command=self.submit)
        sb.grid(row=1, column=1, sticky=EW, padx=3)
        qb = Button(bf, text=' Dismiss ', font=fdbfont, command=self.quitb)
        qb.grid(row=1, column=2, sticky=EW, padx=3)
        # self.wait_window(top)

    def submit(self):
        """submit edits"""
        global editedornot
        error = 0
        changer = 0 # 0 = no change. 1= change except band and call. 2 = change in call or band
        t = self.de.get().strip()  # date time
        if self.chodate != t:
            #print "The date has changed."
            changer = 1
        self.de.configure(bg='white')
        m = re.match(r'[0-9]{6}\.[0-9]{4,6}$', t)
        if m:
            newdate = t + '00'[:13 - len(t)]
            #print newdate
        else:
            self.de.configure(bg='gold')
            error += 1
        t = self.be.get().strip()  # band mode
        if self.choband != t:
            #print "the band has changed"
            changer = 2
        self.be.configure(bg='white')
        m = re.match(r'(160|80|40|20|15|10|6|2|220|440|900|1200|sat)[cdp]$', t)
        if m:
            newband = t
            #print newband
        else:
            self.be.configure(bg='gold')
            error += 1
        t = self.ce.get().strip()  # call
        if self.chocall != t:
            #print "the call has changed"
            changer = 2
        self.ce.configure(bg='white')
        m = re.match(r'[a-z0-9/]{3,11}$', t)
        if m:
            newcall = t
            #print newcall
        else:
            self.ce.configure(bg='gold')
            error += 1
        t = self.re.get().strip()  # report
        if self.chorept != t:
            print "the section is not verified - please check."
            changer = 1
        self.re.configure(bg='white')
        m = re.match(r'.{4,24}$', t)
        if m:
            newrept = t
            #print newrept
        else:
            self.re.configure(bg='gold')
            error += 1
        t = self.pe.get().strip().lower()  # power
        if self.chopowr != t:
            #print "the power has changed."
            changer = 1
        self.pe.configure(bg='white')
        m = re.match(r'[0-9]{1,4}n?$', t)
        if m:
            newpowr = t
            #print newpowr
        else:
            self.pe.configure(bg='gold')
            error += 1
        t = self.oe.get().strip().lower()  # operator
        if self.chooper != t:
            #print "the Operator has changed."
            changer = 1
        self.oe.configure(bg='white')
        if participants.has_key(t):
            newopr = t
            #print newopr
        else:
            self.oe.configure(bg='gold')
            error += 1
        t = self.le.get().strip().lower()  # logger
        if self.chologr != t:
            #print "the logger has changed."
            changer = 1
        self.le.configure(bg='white')
        if participants.has_key(t):
            newlogr = t
            #print newlogr
        else:
            self.le.configure(bg='gold')
            error += 1
        if error == 0:
            # There was no dupe check on the edited qso info. This was added.
            if changer == 0:
                print 'Nothing changed. No action performed.'
                self.crazytxt.set('nothing changed?')
                self.crazyclr.set('pink2')
                self.crazylbl.configure(bg=self.crazyclr.get(), text=self.crazytxt.get())
                error += 1
            if changer == 1:
                # delete and enter new data because something other than band or call has changed. 
                # print "no errors, enter data"
                reason = "edited"
                qdb.delete(self.node, self.seq, reason)
                qdb.postnew(newdate, newcall, newband, newrept, newopr, newlogr, newpowr)
                self.top.destroy()
                txtbillb.insert(END, " EDIT Successful\n")
                topper()
            if changer == 2:
                #band or call changed so check for dupe before submitting to log.
                if qdb.dupck(newcall, newband):  # dup check for new data
                    print 'Edit is a DUPE. No action performed.'
                    self.crazytxt.set("This is a DUPE")
                    self.crazyclr.set('pink2')
                    self.crazylbl.configure(bg=self.crazyclr.get(), text=self.crazytxt.get())
                    error += 1
                else:
                    # delete and enter new data
                    # print "no errors, enter data"
                    reason = "edited"
                    qdb.delete(self.node, self.seq, reason)
                    qdb.postnew(newdate, newcall, newband, newrept, newopr, newlogr, newpowr)
                    self.top.destroy()
                    editedornot = "1"
                    txtbillb.insert(END, " EDIT Successful\n")
                    topper()

    def dele(self):
        print "delete entry"
        reason = 'deleteclick'
        qdb.delete(self.node, self.seq, reason)
        self.top.destroy()

    def quitb(self):
        print 'dismiss - edit aborted'
        self.top.destroy()

