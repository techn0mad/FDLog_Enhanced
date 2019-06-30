#!/usr/bin/python 

class clock_class:
    level = 9  # my time quality level
    offset = 0  # my time offset from system clock, add to system time, sec
    adjusta = 0  # amount to adjust clock now (delta)
    errors = 0  # current error sum wrt best source, in total seconds
    errorn = 0  # number of time values in errors sum
    srclev = 10  # current best time source level
    lock = threading.RLock()  # sharing lock

    def update(self):
        """periodic clock update every 30 seconds"""
        #  Add line to get tmast variable (self.offset=float(gd.get('tmast',0)) from global database
        self.lock.acquire()  # take semaphore
        if node == string.lower(gd.getv('tmast')):
            if self.level != 0: print "Time Master"
            self.offset = 0
            self.level = 0
        else:
            if self.errorn > 0:
                error = float(self.errors) / self.errorn
            else:
                error = 0
            self.adjusta = error
            err = abs(error)
            if (err <= 2) & (self.errorn > 0) & (self.srclev < 9):
                self.level = self.srclev + 1
            else:
                self.level = 9
            if self.srclev > 8: self.adjusta = 0  # require master to function
            if abs(self.adjusta) > 1:
                print "Adjusting Clock %.1f S, src level %d, total offset %.1f S, at %s" % \
                      (self.adjusta, self.level, self.offset + self.adjusta, now())
            self.srclev = 10
        self.lock.release()  # release sem
        ## Add line to put the offset time in global database (gd.put('tmast',self.offset))

    def calib(self, fnod, stml, td):
        "process time info in incoming pkt"
        if fnod == node:
            return
        self.lock.acquire()  # take semaphore
        #    print "time fm",fnod,"lev",stml,"diff",td
        stml = int(stml)
        if stml < self.srclev:
            self.errors, self.errorn = 0, 0
            self.srclev = stml
        if stml == self.srclev:
            self.errorn += 1
            self.errors += td
        self.lock.release()  # release sem

    def adjust(self):
        "adjust the clock each second as needed"
        rate = 0.75931  # delta seconds per second
        adj = self.adjusta
        if abs(adj) < 0.001: return
        if adj > rate:
            adj = rate
        elif adj < -rate:
            adj = -rate
        self.offset += adj
        # or self.offset = float(database.get('tmast',0)) instead of the line above.
        self.adjusta -= adj
        print "Slewing clock", adj, "to", self.offset

