#!/usr/bin/python

class global_data:
    """Global data stored in the journal"""
    byname = {}

    def new(self, name, desc, defaultvalue, okgrammar, maxlen):
        i = global_data()  # create
        i.name = name  # set
        i.val = defaultvalue
        i.okg = okgrammar
        i.maxl = maxlen
        i.ts = ""
        i.desc = desc
        self.byname[name] = i
        return i

    def setv(self, name, value, timestamp):
        if node == "":
            txtbillb.insert(END, "error - no node id\n")
            return
        if name[:2] == 'p:':  # set oper/logr
            i = self.byname.get(name, self.new(name, '', '', '', 0))
        else:
            if not self.byname.has_key(name):  # new
                return "error - invalid global data name: %s" % name
            i = self.byname[name]
            if len(value) > i.maxl:  # too long
                return "error - value too long: %s = %s" % (name, value)
            if name == 'grid':
                value = value.upper() # added to properly format grid (ie CN88 not cn88)
            if not re.match(i.okg, value):  # bad grammar
                return "set error - invalid value: %s = %s" % (name, value)
        if timestamp > i.ts:  # timestamp later?
            i.val = value
            i.ts = timestamp
            if name[:2] == 'p:':
                ini, name, dummy, dummy, dummy = string.split(value, ', ')
                participants[ini] = value
                if name == 'delete':
                    del (participants[ini])
                buildmenus()
                # else: print "set warning - older value discarded"

    def getv(self, name):
        if not self.byname.has_key(name):  # new
            return "get error - global data name %s not valid" % name
        return self.byname[name].val

    def sethelp(self):
        l = ["   Set Commands\n   For the Logging Guru In Charge\n   eg: .set <parameter> <value>\n"]  # spaced for sort
        for i in self.byname.keys():
            if i[:2] != 'p:':  # skip ops in help display
                l.append("  %-6s  %-43s  '%s'" % (i, self.byname[i].desc, self.byname[i].val))
        l.sort()
        viewtextl(l)
