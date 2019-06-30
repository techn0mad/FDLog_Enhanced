#!/usr/bin/python

class syncmsg:
    """synchronous message printing"""
    lock = threading.RLock()
    msgs = []

    def prmsg(self, msg):
        """put message in queue for printing"""
        self.lock.acquire()
        self.msgs.append(msg)
        self.lock.release()

    def prout(self):
        """get message from queue for printing"""
        # Check to see if the log window has been deleted           
        self.lock.acquire()
        while self.msgs:
            logw.configure(state=NORMAL)
            logw.see(END)
            nod = self.msgs[0][70:81]  # color local entries  
            seq = self.msgs[0][65:69].strip()
            seq = int(seq)
            stn = self.msgs[0][69:].strip()
            if nod == node:
                # Added a check to see if in the log to print blue or not
                bid, dummy, dummy = qdb.cleanlog()  # get a clean log
                stnseq = stn +"|"+str(seq)
                if stnseq in bid:
                    logw.insert(END, "%s\n" % self.msgs[0], "b")
                else:
                    logw.insert(END, "%s\n" % self.msgs[0])
            logw.configure(state=DISABLED)
            del self.msgs[0]
        self.lock.release()
