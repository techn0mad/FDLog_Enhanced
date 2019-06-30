#!/usr/bin/python 
import os
import time
import string
import thread
import threading
import socket
import hashlib
import random
import calendar
import sqlite3
from Tkinter import Tk, END, NORMAL, DISABLED, re, sys, Toplevel, Frame, Label, Entry, Button, \
W, EW, E, NONE, NSEW, NS, StringVar, Radiobutton, Tk, Menu, Menubutton, Text, Scrollbar, Checkbutton, RAISED, IntVar


# This needs to be tested on different networks and cross platform.
# 
# KD4SIR - Will probably work on copy/paste functionality
# KC7SDA - Will check network and platform compatibility and upper/lower case entry 



# Originally "WB6ZQZ's Field Day Logging Program" written in 1984.
# Alan Biocca (as WB6ZQZ) ported it to python with GNU in 2002. 
# Our (SCICSG) code starts from: 
# FDLog 1-149-2 2011/07/11
# Copyright 2002-2013 by Alan Biocca (W6AKB) (www.fdlog.info)
# FDLog is distributed under the GNU Public License
# Additional code included from FDLog v4-1-152i 2014/05/26
# Some code modified from FDLog v4-1-153d Febuary 2017

# Forked & Repository Project
# FDLog_Enhanced at Github.com
# Copyright 2014-2019 South Central Indiana Communications Support Group
# Copyright 2019 Curtis E. Mills (WE7U)
# 
# Our Goals are twofold:
#       1: Improve on fdlog faster with open and directed collaboration.
#               This is now on github as FDLog_Enhanced.
#       2: Increase user friendliness (GUI) and inter-operability with other GNU programs.
#               Future: Adding interoperability with other programs such as HRDeluxe Free,
#               FLDigi, Rigserve etc if we can?

prog = 'FDLog_Enhanced v2019-FD-WE7U\n' \
       'Copyright 2014-2019 by South Central Indiana Communications Support Group \n' \
       'Copyright 2019 by Curtis E. Mills (WE7U) \n' \
       'FDLog is under the GNU Public License v2 without warranty. \n' \
       'The original license file is in the folder. \n'
print prog

about = """

FDLog_Enhanced can be found on www.github.com
GNU Public License V2 - in program folder.
Copyright 2014-2019 South Central Indiana Communications Support Group
Copyright 2019 Curtis E. Mills (WE7U)

"""

version = "v18"
fontsize = 10
fontinterval = 2
typeface = 'Courier 10 pitch'

fdfont = (typeface, fontsize)  # regular fixed width font
fdmfont = (typeface, fontsize + fontinterval)  # medium  fixed width font
fdbfont = (typeface, fontsize + fontinterval * 2)  # large   fixed width font


# Known Bug List
#
# some foreign callsigns not supported properly
#   8a8xx
#   need to change the way this works
#   define a suffix as trailing letters
#   prefix as anything ending in digits
#   bring down a previous suffix with a character such as ' or .
#
#

def fingerprint():
    t = open('FDLog.py').read()
    h = hashlib.md5()
    h.update(t)
    print " FDLog Fingerprint", h.hexdigest()


fingerprint()


def ival(s):
    """return value of leading int"""
    r = 0
    if s != "":
        mm = re.match(r' *(-?[0-9]*)', s)
        if mm and mm.group(1):
            r = int(mm.group(1))
    return r


mclock = clock_class()

def initialize():
    k = "" # keyboard input
    z = "" # answer counter
    kfd = 0 # FD indicator to skip questions
    print "\n \n"
    print "For the person in Charge of Logging:"
    print "*** ONLY ONE PERSON CAN DO THIS ***"
    print "Do you need to set up the event? Y or N"    
    print "       if in doubt select N"
    while z != "1":
        k = string.lower(string.strip(sys.stdin.readline())[:1])
        if k == "y": z = "1"
        if k == "n": z = '1'
        if z != "1": print "Press Y or N please"    
    if k == "y":
        # Field Day or VHF contest
        z = ""
        print "Which contest is this?"
        print "F = FD, W = WFD, and V = VHF"
        while z != "1":
            k = string.lower(string.strip(sys.stdin.readline())[:1])
            if k == "f": z = "1"
            if k == "w": z = "1"
            if k == "v": z = '1'
            if z != "1": print "Press F, W or V please"
        if k == "f":
            kfd = 1 #used later to skip grid square question.SAH
            globDb.put('contst', "FD")
            qdb.globalshare('contst', "FD")  # global to db
            renew_title()
            print "Have a nice Field Day!"
        if k == "w":
            kfd = 2 #used later to skip grid square question
            globDb.put('contst', "WFD")
            qdb.globalshare('contst', "WFD")  # global to db
            renew_title()
            print "Have a nice Field Day!"
        if k == "v":
            globDb.put('contst', "VHF")
            qdb.globalshare('contst', "VHF")  # global to db
            renew_title()
            print "Enjoy the VHF contest!"
        # Name of the club or group
        print "What is the NAME of your club or group?"
        k = string.strip(sys.stdin.readline())
        while k == "":
            print "Please type the name of your club or group"
            k = string.strip(sys.stdin.readline())
        globDb.put('grpnam', k)
        qdb.globalshare('grpnam', k)  # global to db
        renew_title()
        print k, "is a nice name."
        # Club Call
        print "What will be your club call?"
        k = string.strip(sys.stdin.readline())
        while k == "":
            print "Please type the club call."
            k = string.strip(sys.stdin.readline())
        globDb.put('fdcall', k)
        qdb.globalshare('fdcall', k)  # global to db
        renew_title()
        print k, "will be the club call."
        # Gota Call
        if kfd == 1:
            print "What will be your GOTA call?"
            k = string.strip(sys.stdin.readline())
            while k == "":
                print "Please type the GOTA call. (if none type none)"
                k = string.strip(sys.stdin.readline())
            else:
                globDb.put('gcall', k)
                qdb.globalshare('gcall', k)  # global to db
                renew_title()
                print k, "will be the GOTA call."
        # Class
        print "What will be your class? (like 2A)"
        k = string.strip(sys.stdin.readline())
        while k == "":
            print "Please type the class."
            k = string.strip(sys.stdin.readline())
        else:
            globDb.put('class', k)
            qdb.globalshare('class', k)  # global to db
            renew_title()
            print k, "will be the class."
        # Section
        print "What will be your section? (like IN-Indiana)"
        k = string.strip(sys.stdin.readline())
        while k == "":
            print "Please type the section (like KY-Kentucky)."
            k = string.strip(sys.stdin.readline())
        else:
            globDb.put('sect', k)
            qdb.globalshare('sect', k)  # global to db
            renew_title()
            print k, "will be the section."
        if kfd == 0:
            # grid square
            print "What will be your grid square? (if none type none)"
            k = string.strip(sys.stdin.readline())
            while k == "":
                print "Please type the grid square. (For FD type none)"
                k = string.strip(sys.stdin.readline())
                k = k.upper() # changed the init so the grid square will be cap
            else:
                globDb.put('grid', k)
                qdb.globalshare('grid', k)  # global to db
                renew_title()
                print k, "will be the grid."
        if kfd !=2:
            #questions for vhf and fd, skip for wfd
            # Public Place
            z = ""
            print "Will the location be in a public place?"
            print "Y = yes and N = no"
            while z != "1":
                k = string.lower(string.strip(sys.stdin.readline())[:1])
                if k == "y": z = "1"
                if k == "n": z = '1'
                if z == "" : print "Press Y or N please"
            if k == "y":
                globDb.put('public', "A public location")
                qdb.globalshare('public', "A public location")  # global to db
                renew_title()
                print "Enjoy the public place."
            if k == "n":
                globDb.put('public', "")
                qdb.globalshare('public', "")  # global to db
                renew_title()
                print "maybe next year..."
            # Info Booth
            z = ""
            print "Will you have an info booth?"
            print "Y = yes and N = no"
            while z != "1":
                k = string.lower(string.strip(sys.stdin.readline())[:1])
                if k == "y": z = "1"
                if k == "n": z = '1'
                if z == "" : print "Press Y or N please"
            if k == "y":
                globDb.put('infob', "1")
                qdb.globalshare('infob', "1")  # global to db
                renew_title()
                print "Love information tables!"
            if k == "n":
                globDb.put('infob', "0")
                qdb.globalshare('infob', "0")  # global to db
                renew_title()
                print "An information table is easy points"
        #Time Master - oh yeah the big question
        z = ""
        print "\n It is recommended that the first computer"
        print "set up should also be the time master."
        print "\n IS THIS COMPUTER TIME CORRECT??? \n"
        print "Will this computer be the time master?"
        print "Y = yes and N = no"
        while z != "1":
            k = string.lower(string.strip(sys.stdin.readline())[:1])
            if k == "y": z = "1"
            if k == "n": z = '1'
            if z == "" : print "Press Y or N please"
        if k == "y":
            globDb.put('tmast', node)
            qdb.globalshare('tmast', node)  # global to db
            renew_title()
            print "Time travels to you!"
        if k == "n":
            pass                
    return


def exin(op):
    """extract Operator or Logger initials"""
    r = ""
    m = re.match(r'([a-z0-9]{2,3})', op)
    if m:
        r = m.group(1)
    return r


# sqlite database upgrade
# sqlite3.connect(":memory:", check_same_thread = False)
# I found this online to correct thread errors with sql locking to one thread only.
# I'm pretty sure I emailed this fix to Alan Biocca over a year ago. :(
# Scott Hibbs 7/5/2015





# modifed  the sect setting regex to accept both lower and upper case
# added additional form fields (also fixed 'from' to 'form') for wfd NOTE: set commands have a max length of 6!
gd = global_data()
for name, desc, default, okre, maxlen in (
        ('class', '<n><A-F>       FD class (eg 2A)', '2A', r'[1-9][0-9]?[a-fihoA-FIHO]$', 3),
        ('contst', '<text>         Contest (FD,WFD,VHF)', 'FD', r'fd|FD|wfd|WFD|vhf|VHF$', 3),
        ('fdcall', '<CALL>         FD call', '', r'[a-zA-Z0-9]{3,6}$', 6),
        ('gcall', '<CALL>         GOTA call', '', r'[a-zA-Z0-9]{3,6}$', 6),
        ('sect', '<CC-Ccccc...>  ARRL section', '<section>', r'[a-zA-Z]{2,3}-[a-zA-Z ]{2,20}$', 24),
        ('grid', '<grid>         VHF grid square', '', r'[A-Z]{2}[0-9]{2}$', 4),
        ('grpnam', '<text>         group name', '', r'[A-Za-z0-9 #.:-]{4,35}$', 35),
        ('fmcall', '<CALL>         entry form call', '', r'[a-zA-Z0-9]{3,6}$', 6),
        ('fmname', '<name>         entry form name', '', r'[A-Za-z0-9 .:-]{0,35}$', 35),
        ('fmad1', '<text>         entry form address line 1', '', r'[A-Za-z0-9 #.,:-]{0,35}$', 35),
        ('fmad2', '<text>         entry form address line 2', '', r'[A-Za-z0-9 #.,:-]{0,35}$', 35),
        ('fmst', '<text>         entry form state', '', r'[a-z]{2,3}$', 3),
        ('fmcity', '<text>         entry form city', '', r'[A-Za-z]{2,35}$', 35),
        ('fmzip', '<text>         entry form zip code', '', r'[0-9]{5}$', 6),
        ('fmem', '<text>         entry form email', '', r'[A-Za-z0-9@.:-]{0,35}$', 35),
        ('public', '<text>         public location desc', '', r'[A-Za-z0-9@.: -]{0,35}$', 35),
        ('infob', '0/1            public info booth', '0', r'[0-1]$', 1),
        ('svego', '<name>         govt official visitor name', '', r'[A-Za-z., -]{0,35}$', 35),
        ('svroa', '<name>         agency site visitor name', '', r'[A-Za-z., -]{0,35}$', 35),
        ('youth', '<n>            participating youth', '0', r'[0-9]{1,2}$', 2),
        ('websub', '0/1            web submission bonus', '0', r'[0-1]$', 1),
        ('psgen', '0/1            using generator power', '0', r'[0-1]$', 1),
        ('pscom', '0/1            using commercial power', '0', r'[0-1]$', 1),
        ('psbat', '0/1            using battery power', '0', r'[0-1]$', 1),
        ('psoth', '<text>         desc of other power', '', r'[A-Za-z0-9.: -]{0,35}$', 35),
        ('fdstrt', 'yymmdd.hhmm    FD start time (UTC)', '020108.1800', r'[0-9.]{11}$', 11),
        ('fdend', 'yymmdd.hhmm    FD end time (UTC)', '990629.2100', r'[0-9.]{11}$', 11),
        ('tmast', '<text>         Time Master Node', '', r'[A-Za-z0-9-]{0,8}$', 8)):
    gd.new(name, desc, default, okre, maxlen)



# global functions

def now():
    """return current time in standard string format"""
    # n = time.localtime(time.time())
    n = time.gmtime(time.time() + mclock.offset)  # time in gmt utc
    # offset to correct to master
    t = time.strftime("%y%m%d.%H%M%S", n)  # compact version YY
    return t

def tmtofl(a):
    """time to float in seconds, allow milliseconds"""
    # Reworked in 152i
    #    return time.mktime((2000+int(a[0:2]),int(a[2:4]),int(a[4:6]),\
    #                       int(a[7:9]),int(a[9:11]),int(a[11:13]),0,0,0))
    return calendar.timegm((2000 + int(a[0:2]), int(a[2:4]), int(a[4:6]),
                            int(a[7:9]), int(a[9:11]), float(a[11:]), 0, 0, 0))

def tmsub(a, b):
    """time subtract in seconds"""
    return tmtofl(a) - tmtofl(b)



def loadglob():
    """load persistent local config to global vars from file"""
    # updated from 152i
    global globDb, node, operator, logger, power, tdwin, debug, authk, timeok
    globDb = GlobalDb()
    node = globDb.get('node', '')
    operator = globDb.get('operator', '')
    logger = globDb.get('logger', '')
    power = globDb.get('power', '0')
    authk = globDb.get('authk', 'tst')
    tdwin = int(globDb.get('tdwin', 5))  # 152i changed from 10 to 5
    debug = int(globDb.get('debug', 0))
    timeok = int(globDb.get('timeok', 0))
    netsync.rem_host = globDb.get('remip', '0.0.0.0')
    if debug: print "  debug:", debug


def saveglob():
    """save persistent local config global vars to file"""
    globDb.put('node', node)
    globDb.put('operator', operator)
    globDb.put('logger', logger)
    globDb.put('power', power)
    globDb.put('authk', authk)
    globDb.put('tdwin', tdwin)
    globDb.put('debug', debug)
    globDb.put('timeok', timeok)
    #    fd = file(globf,"w")
    #    fd.write("|%s|%s|%s|%s|%s|%s|%s|"%(node,operator,logger,power,\
    #                                       authk,tdwin,debug))
    #    fd.close()


# contest log section
def getfile(fn):
    """get file contents"""
    data = ""
    try:
        fd = file(fn, "r")
        data = fd.read()
        fd.close()
    except:
        pass
    if data != "":
        print "Found file", fn
        # print data
    return data


participants = {}


def contestlog(pr):
    """generate contest entry and log forms"""
    w1aw_msg = getfile("w1aw_msg.txt")  # w1aw bulletin copy
    # National Traffic System Messages
    nts_orig_msg = getfile("nts_msg.txt")  # status message
    nts_msg_relay = []
    for i in range(0, 10):  # relayed messages
        fn = "nts_rly%d.txt" % i
        msg = getfile(fn)
        if msg != "":
            nts_msg_relay.append(msg)
    media_copy = getfile("media.txt")  # media activity
    soapbox = getfile("soapbox.txt")  # soapbox commentary
    fd_call = string.upper(gd.getv('fdcall'))  # prep data
    xmttrs = ival(gd.getv('class'))
    gota_call = string.upper(gd.getv('gcall'))
    if xmttrs < 2:
        gota_call = ""
    if pr == 0:
        return  # only define variables return
    # output the entry, adif & cabrillo log file
    datime = now()
    dummy, bycall, gotabycall = qdb.cleanlog()  # get a clean log
    qpb, ppb, qpop, qplg, qpst, dummy, dummy, maxp, cwq, digq, fonq, qpgop, gotaq, nat, sat = \
        qdb.bandrpt()  # and count it
    print "..",
    sys.stdout = file(logfile, "w")  # redirect output to file
    print "Field Day 20%s Entry Form" % datime[:2]
    print
    print "Date Prepared:              %s UTC" % datime[:-2]
    print
    print "1.  Field Day Call:         %s" % fd_call
    if gota_call != "":
        print "    GOTA Station Call:      %s" % gota_call
    print "2.  Club or Group Name:     %s" % gd.getv('grpnam')
    print "3.  Number of Participants: %s" % len(participants)
    print "4.  Transmitter Class:      %s" % xmttrs
    print "5.  Entry Class:            %s" % string.upper(gd.getv('class'))[-1:]
    print
    print "6.  Power Sources Used:"
    if int(gd.getv('psgen')) > 0:
        print "      Generator"
    if int(gd.getv('pscom')) > 0:
        print "      Commercial"
    if int(gd.getv('psbat')) > 0:
        print "      Battery"
    # add solar! xx
    if gd.getv('psoth') != '':
        print "      Other: %s" % (gd.getv('psoth'))
    print
    print "7.  ARRL Section:           %s" % gd.getv('sect')
    print
    print "8.  Total CW QSOs:      %4s  Points: %5s" % (cwq, cwq * 2)
    print "9.  Total Digital QSOs: %4s  Points: %5s" % (digq, digq * 2)
    print "10. Total Phone QSOs:   %4s  Points: %5s" % (fonq, fonq)
    qsop = cwq * 2 + digq * 2 + fonq
    print "11. Total QSO Points:                 %5s" % qsop
    print "12. Max Power Used:     %4s  Watts" % maxp
    powm = 5
    if int(gd.getv('psgen')) > 0 or int(gd.getv('pscom')) > 0: powm = 2
    if maxp > 5:
        powm = 2
    if maxp > 150:
        powm = 1
    if maxp > 1500:
        powm = 0
    print "13. Power Multiplier:                  x %2s" % powm
    qso_scor = qsop * powm
    print "14. Claimed QSO Score:                %5s" % qso_scor
    print
    print "15. Bonus Points:"
    tot_bonus = 0
    emerg_powr_bp = 0
    if gd.getv('pscom') == '0':
        emerg_powr_bp = 100 * xmttrs
        if emerg_powr_bp > 2000:
            emerg_powr_bp = 2000
        tot_bonus += emerg_powr_bp
        print "   %4s 100%s Emergency Power (%s xmttrs)" % (emerg_powr_bp, '%', xmttrs)
    media_pub_bp = 0
    if media_copy > "":
        media_pub_bp = 100
        tot_bonus += media_pub_bp
        print "    %3s Media Publicity (copy below)" % media_pub_bp
    public_bp = 0
    public_place = gd.getv('public')
    if public_place != "":
        public_bp = 100
        tot_bonus += public_bp
        print "    %3s Set-up in a Public Place (%s)" % (public_bp, public_place)
    info_booth_bp = 0
    if int(gd.getv('infob')) > 0 and public_bp > 0:
        info_booth_bp = 100
        tot_bonus += info_booth_bp
        print "    %3s Information Booth (photo included)" % info_booth_bp
    nts_orig_bp = 0
    if nts_orig_msg > "":
        nts_orig_bp = 100
        tot_bonus += nts_orig_bp
        print "    %3s NTS message Originated to ARRL SM/SEC (copy below)" % nts_orig_bp
    n = len(nts_msg_relay)
    nts_msgs_bp = 10 * n
    if nts_msgs_bp > 100:
        nts_msgs_bp = 100
    if nts_msgs_bp > 0:
        tot_bonus += nts_msgs_bp
        print "    %3s Formal NTS messages handled (%s) (copy below)" % (nts_msgs_bp, n)
    sat_qsos = len(sat)
    sat_bp = 0
    if sat_qsos > 0:
        sat_bp = 100
        tot_bonus += sat_bp
        print "    %3s Satellite QSO Completed (%s/1) (list below)" % (sat_bp, sat_qsos)
    natural_q = len(nat)
    natural_bp = 0
    if natural_q >= 5:
        natural_bp = 100
        tot_bonus += natural_bp
        print "    %3s Five Alternate power QSOs completed (%s/5) (list below)" % (natural_bp, natural_q)
    w1aw_msg_bp = 0
    if len(w1aw_msg) > 30:  # ignore short file place holder 152i
        w1aw_msg_bp = 100
        tot_bonus += w1aw_msg_bp
        print "    %3s W1AW FD Message Received (copy below)" % (w1aw_msg_bp)
    site_visited_ego_bp = 0
    if gd.getv('svego') > "":
        site_visited_ego_bp = 100
        tot_bonus += site_visited_ego_bp
        print "    %3s Site Visited by elected govt officials (%s)" % (site_visited_ego_bp, gd.getv('svego'))
    site_visited_roa_bp = 0
    if gd.getv('svroa') > "":
        site_visited_roa_bp = 100
        tot_bonus += site_visited_roa_bp
        print "    %3s Site Visited by representative of agency (%s)" % (site_visited_roa_bp, gd.getv('svroa'))
    gota_max_bp = 0
    if gotaq >= 100:
        gota_max_bp = 100
        tot_bonus += gota_max_bp
        print "    %3s GOTA Station 100 QSOs bonus achieved" % (gota_max_bp)
    youth_bp = 0
    if int(gd.getv('youth')) > 0:
        youth_bp = 20 * int(gd.getv('youth'))
        if youth_bp > 5 * 20:
            youth_bp = 5 * 20
        tot_bonus += youth_bp
        print "    %3s Youth Participation Bonus" % (youth_bp)
    # keep this last
    web_sub_bp = 0
    if gd.getv('websub') == "1":
        web_sub_bp = 50
        tot_bonus += web_sub_bp
        print "    %3s Web Submission Bonus" % (web_sub_bp)
    print
    print "    Total Bonus Points Claimed: %5s" % tot_bonus
    print
    tot_scor = qso_scor + tot_bonus
    print "    Total Claimed Score:        %5s" % tot_scor
    print
    print "16. We have observed all competition rules as well as all regulations"
    print "    for amateur radio in our country. Our report is correct and true"
    print "    to the best of our knowledge. We agree to be bound by the decisions"
    print "    of the ARRL Awards Committee."
    print
    print "Submitted By:"
    print
    print "    Date:     %s UTC" % datime[:-2]
    print "    Call:     %s" % string.upper(gd.getv('fmcall'))
    print "    Name:     %s" % gd.getv('fmname')
    print "    Address:  %s" % gd.getv('fmad1')
    print "    Address:  %s" % gd.getv('fmad2')
    print "    Email:    %s" % gd.getv('fmem')
    print
    print
    print "Field Day Call: %s" % string.upper(fd_call)
    print
    print "17. QSO Breakdown by Band and Mode"
    print
    print "        ----CW----  --Digital-  ---Phone--"
    print "  Band  QSOs   PWR  QSOs   PWR  QSOs   PWR"
    print
    qsobm, pwrbm = {}, {}
    for b in (160, 80, 40, 20, 15, 10, 6, 2, 220, 440, 1200, 'sat', 'gota'):
        if b == 'gota' and gota_call == "":
            continue
        print "%6s" % b,
        for m in 'cdp':
            bm = "%s%s" % (b, m)
            print "%5s %5s" % (qpb.get(bm, 0), ppb.get(bm, 0)),
            qsobm[m] = qsobm.get(m, 0) + qpb.get(bm, 0)
            pwrbm[m] = max(pwrbm.get(m, 0), ppb.get(bm, 0))
        print
    print
    print "Totals",
    print "%5s %5s" % (qsobm['c'], pwrbm['c']),
    print "%5s %5s" % (qsobm['d'], pwrbm['d']),
    print "%5s %5s" % (qsobm['p'], pwrbm['p'])
    print
    print
    if gota_call:
        print "18. Callsigns and QSO counts of GOTA Operators"
        print
        print "      Call  QSOs"
        for i in qpgop.keys():
            print "    %6s   %3s" % (i, qpgop[i])
        print "    %6s   %3s" % ("Total", gotaq)
        print
        print
    print "Dupe Lists sorted by Band, Mode and Call:"
    print
    print "  Main Station(s) Dupe List (%s)" % fd_call
    l = []
    for i in bycall.values():
        l.append("    %4s %s" % (i.band, i.call))
    l.sort()
    b2, n = "", 0
    for i in l:
        b, c = i.split()
        if (b == b2) & (n < 5):  # same band, 5 per line
            print "%-10s" % c,
            n += 1
        else:
            print
            print "    %4s   %-10s" % (b, c),
            b2 = b
            n = 1
    print
    print
    print
    if gota_call > "":
        print "  GOTA Station Dupe List (%s)" % gota_call
        l = []
        for i in gotabycall.values():
            l.append("    %4s %s" % (i.band, i.call))
        l.sort()
        b2, n = "", 0
        for i in l:
            b, c = i.split()
            if (b == b2) & (n < 5):  # same band
                print "%-10s" % c,
                n += 1
            else:
                print
                print "    %4s   %-10s" % (b, c),
                b2 = b
                n = 1
        print
        print
        print
    if w1aw_msg != "":
        print "W1AW FD Message Copy"
        print
        print "%s" % w1aw_msg
        print
        print
    if nts_orig_msg != "":
        print "Originated NTS Message"
        print
        print nts_orig_msg
        print
        print
    if len(nts_msg_relay) > 0:
        print "RELAYED NTS Messages"
        print
        for i in nts_msg_relay:
            print i
            print
        print
    if media_copy != "":
        print "Media Copy"
        print
        print media_copy
        print
        print
    if len(nat) > 0:
        print "Natural Power QSOs (show first 10 logged)"
        print
        l = []
        for i in nat:
            ln = "%8s %5s %-10s %-18s %4s %-6s %-6s %4s %s" % \
                 (i.date[4:11], i.band, i.call, i.rept[:18], i.powr, i.oper, i.logr, i.seq, i.src)
            l.append(ln)
        l.sort()
        j = 0
        for i in l:
            print i
            j += 1
            if j > 9:
                break
        print
        print
    if len(sat) > 0:
        print "Satellite QSOs (show 5)"
        print
        l = []
        for i in sat:
            ln = "%8s %5s %-10s %-18s %4s %-6s %-6s %4s %s" % \
                 (i.date[4:11], i.band, i.call, i.rept[:18], i.powr, i.oper, i.logr, i.seq, i.src)
            l.append(ln)
        l.sort()
        j = 0
        for i in l:
            print i
            j += 1
            if j > 4:
                break
        print
        print
    if soapbox != "":
        print "Soapbox Comments"
        print
        print soapbox
        print
        print
    print "Logging and Reporting Software Used:\n"
    print prog
    print "===================== CLIP HERE ============================"
    print
    print "(do not include below in ARRL submission)"
    print
    print "Submission Notes"
    print """
    email files as attachments to FieldDay@arrl.org within 30 days!!!
    web entry at www.b4h.net/cabforms
        fdlog.log log file, less log detail below 'CLIP HERE'
        proof of bonus points, as needed:
            public info booth picture, visitor list, info
            visiting officials pictures
            media visiting pictures
            natural power pictures
            demo stations pictures
        plus other interesting pictures
    """
    print "Participant List"
    print
    l = []
    for i in participants.values():
        l.append(i)
    l.sort()
    n = 0
    for i in l:
        n += 1
        print "  %4s %s" % (n, i)
    print
    print
    print "QSO breakdown by Station"
    print
    for i in qpst.keys():
        print "  %4s %s" % (qpst[i], i)
    print
    print
    print "QSO breakdown by Operator"
    print
    for i in qpop.keys():
        print "  %4s %s" % (qpop[i], i)
    print
    print
    print "QSO breakdown by Logger"
    print
    for i in qplg.keys():
        print "  %4s %s" % (qplg[i], i)
    print
    print
    print "Worked All States during FD Status"
    print
    r = qdb.wasrpt()
    for i in r:
        print i
    print
    print
    print "Detailed Log"
    print
    print "  Date Range", gd.getv('fdstrt'), "-", gd.getv('fdend'), "UTC"
    print
    qdb.prlog()
    print
    print
    print "ADIF Log"
    print
    qdb.pradif()
    print
    print "VHF Cabrillo"
    print
    qdb.vhf_cabrillo()
    print
    print
    print "Winter Field day"
    print
    qdb.winter_fd()
    print
    print "eof"
    sys.stdout = sys.__stdout__  # revert print to console
    print
    print "entry and log written to file", logfile

# setup for phonetics printout  ## to get phonetics on bottom of gui?
# d = {"a":"alpha ","b":"bravo ","c":"charlie ","d":"delta ","e":"echo ", \
#     "f":"foxtrot ","g":"golf ","h":"hotel ","i":"india ","j":"juliett ", \
#     "k":"kilo ","l":"lima ","m":"mike ","n":"november ","o":"oscar ", \
#     "p":"papa ","q":"quebec ","r":"romeo ","s":"sierra ","t":"tango ", \
#     "u":"uniform ","v":"victor ","w":"whiskey ","x":"x-ray ","y":"yankee ", \
#     "z":"zulu ","-":"dash ", "/":"dash ", "0":"Zero ", "1":"One ", "2":"Two ", "3":"Three ", \
#     "4":"Four ", "5":"Five ", "6":"Six ", "7":"Seven ", "8":"Eight ", "9":"Nine "}
# phonetics = "ab9cde" #string.lower(gd.getv('fdcall'))
# let:char = d
# phocall = ""
# for char in phonetics:
#    if char in d:
#        phocall = phocall.join(char)

# band set buttons
# this can be customized -Only here customizing this in program will break from compatibility with
# original fdlog.py
bands = ('160', '80', '40', '20', '15', '10', '6', '2', '220', '440', '900', '1200', 'sat', 'off')
modes = ('c', 'd', 'p')
bandb = {}  # band button handles


def bandset(b):
    global band, tmob
    if node == "":
        b = 'off'
        txtbillb.insert(END, "err - no node\n")
    if operator == "":
        b = 'off'
        txtbillb.insert(END, "err - no Operator\n")
    if b != 'off':
        s = net.si.nod_on_band(b)
        if s: txtbillb.insert(END, " Already on [%s]: %s\n" % (b, s))
    txtbillb.see(END)
    if band != b: tmob = now()  # reset time on band
    band = b
    bandb[b].select()
    renew_title()

def bandoff():
    """ To set the band to off"""
    bandset('off')



newpart = NewParticipantDialog()
# property dialogs


cf = {}


def renew_title():
    """renew title and various, called at 10 second rate"""
    if node == 'gotanode':
        call = string.upper(gd.getv('gcall'))
    else:
        call = string.upper(gd.getv('fdcall'))
    clas = string.upper(gd.getv('class'))
    sec = gd.getv('sect')
    t = now()
    sob = tmsub(t, tmob)
    mob = sob / 60
    h = mob / 60
    m = mob % 60
    # Added port to the heading
    root.title('  FDLOG %s %s %s (Node: %s Time on Band: %d:%02d) %s:%s UTC %s/%s Port:%s' % \
               (call, clas, sec, node, h, m, t[-6:-4], t[-4:-2], t[2:4], t[4:6], port_base))
    net.bcast_now()  # this is periodic bcast...

def setnode(new):
    global node
    bandoff()
    node = string.lower(new)
    qdb.redup()
    renew_title()
    lblnode.configure(text="My Node: %s" % node, font=fdfont, foreground='royalblue', background='lightgrey')
    # Had to add the above so that the new lblnode could be updated

def applyprop(e=''):
    """apply property"""
    global operator, logger, power, node
    new = cf['e'].get()
    if re.match(cf['vre'], new):
        #        if   cf['lab'] == 'Operator': operator = new
        #        elif cf['lab'] == 'Logger':   logger = new
        #        elif cf['lab'] == 'Power':    power = new
        if cf['lab'] == 'Node':
            setnode(new)
        #        elif cf['lab'] == 'AuthKey':  reauth(new)    #net.setauth(new)
        else:
            print 'error, no such var'
        saveglob()
        renew_title()
        cf['p'].destroy()
    else:
        print 'bad syntax', new

def pdiag(label, value, valid_re, wid):
    "property dialog box"
    cf['p'] = Toplevel(root)
    cf['p'].transient(root)
    Label(cf['p'], text=label, font=fdbfont).grid(sticky=E, pady=20)
    if label == 'AuthKey':
        cf['e'] = Entry(cf['p'], width=wid, font=fdbfont, show='*')
    else:
        cf['e'] = Entry(cf['p'], width=wid, font=fdbfont)
    cf['e'].grid(row=0, column=1, sticky=W)
    cf['e'].insert(END, value)
    Button(cf['p'], text="Apply", command=applyprop, font=fdbfont) \
        .grid(sticky=W, padx=20)
    Button(cf['p'], text="Cancel", command=cf['p'].destroy, font=fdbfont) \
        .grid(padx=20, pady=20, row=1, column=1, sticky=E)
    cf['vre'] = valid_re
    cf['lab'] = label
    cf['e'].bind('<Return>', applyprop)
    cf['p'].bind('<Escape>', lambda e: (cf['p'].destroy()))
    cf['e'].focus()

def noddiag():
    pdiag('Node', node, r'[A-Za-z0-9-]{1,8}$', 8)
    #def authdiag():
    #    pdiag('AuthKey',authk,r'.{3,12}$',12)


# view textdocs

def viewprep(ttl=''):
    "view preparation core code"
    w = Toplevel(root)
    ##    w.transient(root)
    w.title("FDLOG - %s" % ttl)
    t = Text(w, takefocus=0, height=20, width=85, font=fdfont, \
             wrap=NONE, setgrid=1)
    s = Scrollbar(w, command=t.yview)
    t.configure(yscrollcommand=s.set)
    t.grid(row=0, column=0, sticky=NSEW)
    s.grid(row=0, column=1, sticky=NS)
    w.grid_rowconfigure(0, weight=1)
    w.grid_columnconfigure(0, weight=1)
    t.bind('<KeyPress>', kevent)
    return t


def viewtextv(txt, ttl=''):
    "view text variable"
    w = viewprep(ttl)
    w.insert(END, txt)
    w.configure(state=DISABLED)


def viewtextl(l, ttl=''):
    "view text list"
    w = viewprep(ttl)
    for i in l:
        w.insert(END, "%s\n" % i)
    w.configure(state=DISABLED)


def viewtextf(fn, ttl=''):
    "view text file"
    if ttl == "": ttl = "file %s" % fn
    try:
        fd = file(fn, 'r')
        l = fd.read()
        viewtextv(l, ttl)
        fd.close()
    except:
        viewtextv("read error on file %s" % fn)


def viewlogf(bandm):
    "view log filtered by bandmode"
    lg = qdb.filterlog2(bandm)
    viewtextl(lg, "Log Filtered for %s" % bandm)


def viewlogfs(nod):
    "view log filtered by node"
    lg = qdb.filterlogst(nod)
    viewtextl(lg, "Log Filtered for %s" % nod)

def viewwasrpt():
    r = qdb.wasrpt()
    viewtextl(r, "Worked All States Report")


def updatebb():
    """update band buttons"""
    # Added Who's on the bands functionality with a mouse over event
    # Tried and tried to get wof to return only one result for the mouse over. If you can, you're awesome!
    global wof
    r, cl, vh, go = net.si.nod_on_bands()
    anytext = "VHF "


    def whosonfirst(event):
        # Cleaned up whos on band (with section of .ba report)
        d = {}
        txtbillb.insert(END,"\n--node-- band opr lgr pwr  ----- last\n")
        for t in net.si.nodinfo.values():
            dummy, dummy, age = d.get(t.nod, ('', '', 9999))
            if age > t.age: d[t.nod] = (t.bnd, t.msc, t.age)
        for t in d:
            txtbillb.insert(END,"%8s %4s %-18s %4s\n" % (t, d[t][0], d[t][1], d[t][2]))  # t.bnd,t.msc,t.age)
        topper()
        txtbillb.see(END)



    def whosonsecond(event):
        global wof
        wof = ""
		#tkMessageBox.destroy

    for i in bands:
        dummy = 0
        for j in modes:
            bm = "%s%s" % (i, j)
            if i == 'off':
                continue
            bc = 'lightgray'
            sc = 'white'
            n = len(r.get(bm, ''))
            bandb[bm].bind("<Enter>", lambda e: None)
            bandb[bm].bind("<Leave>", lambda e: None)
            if n == 0:
                bc = 'lightgrey'
                bandb[bm].bind("<Enter>", lambda e: None)
                bandb[bm].bind("<Leave>", lambda e: None)
            elif n == 1:
                bc = 'gold'
                bandb[bm].bind("<Enter>", whosonfirst)
                bandb[bm].bind("<Leave>", whosonsecond)
            else:
                bc = 'darkorange'; sc = 'red'
                bandb[bm].bind("<Enter>", whosonfirst)
                bandb[bm].bind("<Leave>", whosonsecond)
            bandb[bm].configure(background=bc, selectcolor=sc)

    cltg = ival(gd.getv('class'))  # class target
    if cltg > 1:
        vhfree = 1  # handle free vhf xmttr
        ts = cl - vhfree
        if vh == 0:
            ts = cl
        else:
            ts = cl - vhfree
        if ts <= -1:
            ts = 0
    else:
        vhfree = 0
        ts = cl
    #ts = cl + max(0, vh-vhfree)  # total sta = class + excess vhf stations
    # Fixed VHF to reflect a free transmitter and warn if two vhf rigs are used
    clc = 'gold'
    if ts == cltg:
        clc = 'palegreen'
    if ts > cltg:
        clc = 'pink2'
    bandb['Class'].configure(text='Class %s/%s' % (ts, cltg), background=clc)

    vhc = 'gold'
    if vh - vhfree == 0:
        vhc = 'palegreen'  # for 1D Class correction
        anytext = "VHF "
    if vh < 0:
        vhc = 'pink2'
        anytext = "VHF "
    if vh > vhfree:
        vhc = 'darkorange'  # 2 vhf is okay, only 1 is free...
        anytext = "VHF taking HF "
    bandb['VHF'].configure(text='%s%s/%s' % (anytext, vh, vhfree), background=vhc)

    if cltg > 1:
        gotatg = 1
    else:
        gotatg = 0
    goc = 'gold'
    if go == gotatg: goc = 'palegreen'
    if go > gotatg: goc = 'pink2'
    bandb['GOTA'].configure(text='GOTA %s/%s' % (go, gotatg), background=goc)

def updateqct():
    "update contact count"
    dummy, dummy, qpop, qplg, dummy, dummy, dummy, dummy, cwq, digq, fonq, dummy, gotaq, dummy, dummy = \
        qdb.bandrpt()  # xx reduce processing here
    for i, j in (('FonQ', 'Phone %5s' % fonq),
                 ('CW/D', 'CW&Dig %4s' % (cwq + digq)),
                 ('GOTAq', 'GOTA %6s' % gotaq)):
        bandb[i].configure(text=j, background='lightgrey')
        # Update for the operator OpQ - for fd 2014
        if operator == "":
            coin2 = "Operator"
            opmb.config(text=coin2, background='pink2')
            opds.config(text="<Select Operator>", background='pink2')
        else:
            coin = exin(operator)
            if coin in qpop:
                coin2 = qpop['%s' % coin]
                opmb.config(text='ConQ %2s' % coin2, background='lightgrey')
                opds.config(text=operator, background='lightgrey')
            else:
                coin2 = "0"
                opmb.config(text='ConQ %2s' % coin2, background='lightgrey')
                opds.config(text=operator, background='lightgrey')
        # Update for the logger LoQ - for fd 2014
        if logger == "":
            coil2 = "Logger"
            logmb.config(text=coil2, background='pink2')
            logds.config(text="<Select Logger>", background='pink2')
        else:
            coil = exin(logger)
            if coil in qplg:
                coil2 = qplg['%s' % coil]
                logmb.config(text='LogQ %2s' % coil2, background='lightgrey')
                logds.config(text=logger, background='lightgrey')
            else:
                coil2 = "0"
                logmb.config(text='LogQ %2s' % coil2, background='lightgrey')
                logds.config(text=logger, background='lightgrey')
    t = ""  # check for net config trouble
    if net.fills: t = "NEED FILL"
    if net.badauth_rcvd:
        net.badauth_rcvd = 0
        t = "AUTH FAIL"
    if net.pkts_rcvd:
        net.pkts_rcvd = 0
    else:
        t = "Alone? Not receiving data from others. Firewall?"
    if net.send_errs:
        t = "SEND FAIL - Not sending data to others. Firewall?"; net.send_errs = 0
    if authk == '':
        t = "NO AUTHKEY SELECTED"
    if node == '':
        t = "NO NODE SELECTED"
    if t:
        lblnet.configure(text=t, background='gold')
    else:
        lblnet.configure(text="Network OK", background='lightgrey')

def BandButtons(w):
    "create band buttons"
    global sv
    a = 0
    sv = StringVar()
    sv.set(band)
    mac = os.name == 'posix'  # detect the mac added 152i
    for i in bands:
        b = 0
        for j in modes:
            bm = "%s%s" % (i, j)
            if i == 'off':
                bm = 'off'
                # indicatoron = 0 makes square button with text inside but doesn't work well on mac, with value 1 it makes a
                # circle alongside the text and works on both so detect mac and change it for mac only
                bandb[bm] = Radiobutton(master=w, text=bm, font=fdfont, background='lightgrey', indicatoron=mac, \
                                        variable=sv, value=bm, selectcolor='pink2',
                                        command=lambda b=bm: (bandset(b)))
            else:
                bandb[bm] = Radiobutton(master=w, text=bm, font=fdfont, background='pink2', indicatoron=mac, \
                                        variable=sv, value=bm, selectcolor='white',
                                        command=lambda b=bm: (bandset(b)))
            bandb[bm].grid(row=b, column=a, sticky=NSEW)
            b += 1
        a += 1
    for i, j, dummy in (('Class', 0, 5),
                     ('VHF', 1, 13),
                     ('GOTA', 2, 9)):
        bandb[i] = Button(w, text=i, font=fdfont)
        bandb[i].grid(row=j, column=a, sticky=NSEW)
    w.grid_columnconfigure(a, weight=1)
    a += 1
    for i, j in (('FonQ', 0),
                 ('CW/D', 1),
                 ('GOTAq', 2)):
        bandb[i] = Button(w, text=i, font=fdfont)
        bandb[i].grid(row=j, column=a, sticky=NSEW)
    w.grid_columnconfigure(a, weight=1)


def rndlet():
    return chr(random.randrange(ord('a'), ord('z') + 1))


def rnddig():
    return chr(random.randrange(ord('0'), ord('9') + 1))


def testqgen(n):
    # added if authk protection so that .testqgen only operates with a 'tst' database.
    # no funny business with the contest log
    if authk == "tst":
        while n:
            call = rndlet() + rndlet() + rnddig() + rndlet() + rndlet() + rndlet()
            rpt = rnddig() + rndlet() + ' ' + rndlet() + rndlet() + ' testQ'
            print call, rpt
            n -= 1
            qdb.qsl(now(), call, band, rpt)
            time.sleep(0.1)
    else:
        txtbillb.insert(END, "This command only available while testing with tst.")


# global section, main program
# setup persistent globals before GUI

suffix = ""
call = ""
band = "off"
power = "0"
operator = ""
logger = ""
age = 0
vist = ""
node = ""
authk = ""
port_base = 7373
tmob = now()  # time started on band in min
tdwin = 10  # time diff window on displaying node clock diffs
showbc = 0  # show broadcasts
debug = 0
logdbf = "fdlog.fdd"  # persistent file copy of log database
logfile = "fdlog.log"  # printable log file (contest entry)
globf = "fdlog.dat"  # persistent global file
kbuf = ""  # keyboard line buffer
goBack = "" # needed to print the last line entered with up arrow
loadglob()  # load persistent globals from file
print
if node == "":
    # Revised for 8 characters so the log lines up nicely
    print "  Enter the station name"
    print "  Please be 7 characters! (I will add letters to be unique)"
    print "  (Use 'gota' for get on the air station)"
    #    print "  (Previous Node ID: '%s')"%node
    print "  (7 characters}"
    k = string.lower(string.strip(sys.stdin.readline())[:8])
    if len(k) == 8:
        print "That's too many.. (Marc? is that you?)" # Thanks to Marc Fountain K9MAF for the correction.
        k = k[:7]
    z = len(k)
    if k != 'gota':
        while z != 7:
            if k == 'gota':
                print "please restart the program."
                sys.exit()
            else:              
                if z < 4:
                    print "um yeah.. 7 characters....    (restart if your gota)"
                    k = string.lower(string.strip(sys.stdin.readline())[:8])
                    z = len(k)
                else:
                    for z in range(z, 7):
                        print "close enough (Ken? is that you?)"
                        k = k + random.choice('abcdefghijklmnopqrstuvwxyz')
                        print k
                        z = len(k)
                        ## 1. if there is more than four characters
                        ## 2. add the rest with randoms
                    
        else:
            print "Thank You!!"
            node = k + random.choice('abcdefghijklmnopqrstuvwxyz')
            print
    else:
        print "Thank You for being gota!!"
        node = 'gotanode'
        print
print "Using Node ID: '%s' " % node
print
# get auth key  auth xxxpppzzz..  fdlogxxx.fdd  port ppp   hashkey (all)
# allow user to select new one, or re-use previous
print "Enter Authentication Key (Return to re-use previous '%s')" % authk
print "  (use 'tst' for testing, two digit year for contest):"
k = string.strip(sys.stdin.readline())
if k != "":
    print "New Key entered, Operator and Logger cleared"
    authk = k
    operator = ""
    logger = ""
    print
print "Using Authentication Key: '%s'" % authk
print "Using", authk[0:3], "for setting port, file"
port_offset = ival(authk[3:6]) * 7
if port_offset == 0: port_offset = ival(authk[0:3]) * 7
# for each char in port_offset:  xxx
# port_offset = ((port_offset << 3) + (char & 15)) & 0x0fff
port_base += port_offset
print "Using Network Port:", port_base
logdbf = "fdlog%s.fdd" % (authk[0:3])
print "Writing Log Journal file:", logdbf
print "Starting Network"
net = netsync()  # setup net
net.setport(port_base)
net.setauth(authk)
print "Saving Persistent Configuration in", globf
saveglob()
print "Time Difference Window (tdwin):", tdwin, "seconds"
print "Starting GUI setup"
root = Tk()  # setup Tk GUI
# root.withdraw()  # This was removed in the last beta without explanation
menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Save Entry File", command=lambda: contestlog(1))
filemenu.add_command(label="PreView Saved Entry File",
                     command=lambda: viewtextf('fdlog.log'))
filemenu.add_command(label="View Log Data File",
                     command=lambda: viewtextf(logdbf))
filemenu.add_command(label="Exit", command=root.quit)
propmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="Properties", menu=propmenu)
propmenu.add_command(label="Set Node ID", command=noddiag)
propmenu.add_command(label="Add Participants", command=newpart.dialog)
logmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="Logs", menu=logmenu)
logmenu.add_command(label='Full Log', command=lambda: viewlogf(""))
logmenu.add_command(label='QSTs', command=lambda: viewlogf(r"[*]QST"))
logmenu.add_command(label='GOTA', command=lambda: viewlogfs("gota"))
logmenu.add_command(label='WAS', command=viewwasrpt)
for j in modes:
    m = Menu(logmenu, tearoff=0)
    if j == 'c':
        lab = 'CW'
    elif j == 'd':
        lab = 'Digital'
    elif j == 'p':
        lab = 'Phone'
    logmenu.add_cascade(label=lab, menu=m)
    for i in bands:
        if i == 'off': continue
        bm = "%s%s" % (i, j)
        m.add_command(label=bm, command=lambda x=bm: (viewlogf(x)))
#  Added Resources Menu Item to clean up the menu
resourcemenu = Menu(menu, tearoff=0)
menu.add_cascade(label="Resources", menu=resourcemenu)
# Changed this from fdrules to just Rules to get away from fd name in file folder
resourcemenu.add_command(label="ARRL FD Rules (pdf)", command=lambda: os.startfile('Rules.pdf'))
# Changed this to a .dat file to remove the duplicate txt file
resourcemenu.add_command(label="ARRL Sections", command=lambda: viewtextf('Arrl_sect.dat', 'ARRL Sections'))
resourcemenu.add_command(label="ARRL Band Chart (pdf)", command=lambda: os.startfile('Bands.pdf'))
resourcemenu.add_command(label="ARRL Band Plan", command=lambda: viewtextf('ARRL_Band_Plans.txt', "ARRL Band Plan"))
# This is not needed with the band chart giving the same info
#resourcemenu.add_command(label="FD Frequency List", command=lambda: viewtextf('frequencies.txt', "FD Frequency List"))
# Removed the propagation report. We don't use it
#resourcemenu.add_command(label="Propagation Info", command=lambda: viewtextf('propagation.txt', "Propagation Info"))
# Created a W1AW menu
W1AWmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="W1AW", menu=W1AWmenu)
W1AWmenu.add_command(label="W1AW Schedule", command=lambda: viewtextf('w1aw.txt', 'W1AW Schedule'))
W1AWmenu.add_command(label="NTS Message", command=lambda: os.startfile('NTS_eg.txt'))


# Time Conversion Chart

tzchart = """
 UTC       PDT  CDT  EDT
 GMT  PST  CST  EST
"""
for g in range(0, 2400, 100):
    p = g - 800
    if (p < 0): p += 2400
    c = p + 100
    if (c < 0): c += 2400
    e = c + 100
    if (e < 0): e += 2400
    x = e + 100
    if (x < 0): x += 2400
    tzchart += "%04d %04d %04d %04d %04d\n" % (g, p, c, e, x)
resourcemenu.add_command(label="Time Conversion Chart", command=lambda: viewtextv(tzchart, "Time Conversion Chart"))
helpmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Quick Help", command=lambda: viewtextf('Keyhelp.txt'))
helpmenu.add_command(label="Set Commands", command=gd.sethelp)
helpmenu.add_command(label="The Manual", command=lambda: viewtextf('Manual.txt', "Manual"))
helpmenu.add_command(label="Release Log", command=lambda: viewtextf('Releaselog.txt'))
helpmenu.add_command(label="GitHub ReadMe", command=lambda: viewtextf('readme.txt'))
helpmenu.add_command(label="About FDLOG", command=lambda: viewtextv(about, "About"))

# Band Buttons
f1 = Frame(root, bd=1)
BandButtons(f1)
f1.grid(row=0, columnspan=2, sticky=NSEW)


def testcmd(name, rex, value):
    """set global from command, return value and change status"""
    global kbuf
    value = default  # added in 152i
    s = "%s +(%s)$" % (name, rex)
    m = re.match(s, kbuf)
    if m:
        value = m.group(1)
        txtbillb.insert(END, "\n%s set to %s\n" % (name, value))
        kbuf = ""
    return value, default != value

def setoper(op):
    "set operator"
    global operator
    # print "setoper",op
    ini, name, call, age, vist = string.split(op, ', ')
    operator = "%s: %s, %s, %s, %s" % (ini, name, call, age, vist)
    # Adding red to the display
    ocolor = 'lightgrey'
    opds.config(text=operator, background=ocolor)
    opmb.config(background='gold')
    saveglob()


def setlog(logr):
    """set logger"""
    global logger
    # print "setlog",logr
    ini, name, call, age, vist = string.split(logr, ', ')
    logger = "%s: %s, %s, %s, %s" % (ini, name, call, age, vist)
    lcolor = 'lightgrey'
    logds.config(text=logger, background=lcolor)
    logmb.config(background='gold')
    saveglob()


f1b = Frame(root, bd=0)  # oper logger power and network windows
#  Changed the color of the user buttons to red until assigned
ocolor = 'pink2'
lcolor = 'pink2'
pcolor = 'pink2'
# Add "who" button to display messagebox with operators on band when clicked.
# Determined that this is not needed now that the mouse over report is cleaner.
#opwho = Menubutton(f1b, text='WHO ', font=fdfont, relief='raised',
#                   background='lightgrey', foreground='royalblue')
#opwho.grid(row=0, column=0, sticky=NSEW)

# Operator
opmb = Menubutton(f1b,text='Operator',font=fdfont,relief='raised', background=ocolor)
opmb.grid(row=0,column=1,sticky=NSEW)
opmu = Menu(opmb,tearoff=0)
opmb.config(menu=opmu,direction='below')
opmu.add_command(label="Add New Operator",command=newpart.dialog)
opds = Menubutton(f1b, text='<select Operator>',font=fdfont,relief='raised',background=ocolor)
opds.grid(row=0,column=0,sticky=NSEW)
opdsu = Menu(opds,tearoff=0)
opds.config(menu=opdsu,direction='below')
f1b.grid_columnconfigure(0,weight=1)
# Logger
logmb = Menubutton(f1b,text="Logger",font=fdfont,relief='raised',background=lcolor)
logmb.grid(row=0,column=4,sticky=NSEW)
logmu = Menu(logmb,tearoff=0)
logmb.config(menu=logmu,direction='below')
logmu.add_command(label="Add New Logger",command=newpart.dialog)
logds = Menubutton(f1b,text='<Select Logger>',font=fdfont,relief='raised',background=lcolor)
logds.grid(row=0,column=3,sticky=NSEW)
f1b.grid_columnconfigure(3,weight=1)
logdsu = Menu(logds,tearoff=0)
logds.config(menu=logdsu,direction='below')
logdsu.add_command(label="Add New Logger",command=newpart.dialog)

def buildmenus():
    opdsu.delete(0, END)
    logdsu.delete(0, END)
    l = participants.values()
    l.sort()
    for i in l:
        # had to take out the $ which looks for the end of value
        # Decided non-hams can be in operator field but will check for license before logging
        # m = re.match(r'[a-z0-9]+, [a-zA-Z ]+, ([a-z0-9]+)',i)
        #if m: opdsu.add_command(label=i, command=lambda n=i: (setoper(n)))
        opdsu.add_command(label=i, command=lambda n=i: (setoper(n)))
        logdsu.add_command(label=i, command=lambda n=i: (setlog(n)))
    opdsu.add_command(label="Add New Operator", command=newpart.dialog)
    logdsu.add_command(label="Add New Logger", command=newpart.dialog)


# power
def ckpowr():
    global power
    pwr = ival(pwrnt.get())
    if pwr < 0:
        pwr = "0"
    elif pwr > 1500:
        pwr = "1500"
    pwrnt.delete(0, END)
    pwrnt.insert(END, pwr)
    if natv.get():
        pwr = "%sn" % pwr
    else:
        pwr = "%s" % pwr
    power = pwr
    if power == "0":
        pcolor = 'pink2'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    else:
        pcolor = 'lightgray'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    if power == "0n":
        pcolor = 'pink2'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    else:
        pcolor == 'lightgray'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    print 'power', power
    return 1


def setpwr(p):
    global power
    pwr = ival(p)
    pwrnt.delete(0, END)
    pwrnt.insert(END, pwr)
    if p[-1:] == 'n':
        powcb.select()
    else:
        powcb.deselect()
    power = p
    if power == "0":
        pcolor = 'pink2'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    else:
        pcolor = 'lightgray'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    if power == "0n":
        pcolor = 'pink2'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)
    else:
        pcolor == 'lightgray'
        pwrmb.config(background=pcolor)
        pwrnt.config(background=pcolor)
        powcb.config(background=pcolor)
        powlbl.config(background=pcolor)

        
pwrmb = Menubutton(f1b, text="Power", font=fdfont, relief='raised',
                   background=pcolor)
pwrmb.grid(row=0, column=6, sticky=NSEW)
pwrmu = Menu(pwrmb, tearoff=0)
pwrmb.config(menu=pwrmu, direction='below')
pwrmu.add_command(label='     0 Watts', command=lambda: (setpwr('0')))
pwrmu.add_command(label='     5 Watts', command=lambda: (setpwr('5')))
pwrmu.add_command(label='    50 Watts', command=lambda: (setpwr('50')))
pwrmu.add_command(label='  100 Watts', command=lambda: (setpwr('100')))
pwrmu.add_command(label='  150 Watts', command=lambda: (setpwr('150')))
pwrmu.add_command(label='  200 Watts', command=lambda: (setpwr('200')))
pwrmu.add_command(label='  500 Watts', command=lambda: (setpwr('500')))
pwrmu.add_command(label='1000 Watts', command=lambda: (setpwr('1000')))
pwrmu.add_command(label='1500 Watts', command=lambda: (setpwr('1500')))
pwrmu.add_command(label='     5W Natural', command=lambda: (setpwr('5n')))
pwrmu.add_command(label='   50W Natural', command=lambda: (setpwr('50n')))
pwrmu.add_command(label=' 100W Natural', command=lambda: (setpwr('100n')))
pwrmu.add_command(label=' 150W Natural', command=lambda: (setpwr('150n')))
pwrnt = Entry(f1b, width=4, font=fdfont, background=pcolor, validate='focusout', validatecommand=ckpowr)
pwrnt.grid(row=0, column=7, sticky=NSEW)
powlbl = Label(f1b, text="W", font=fdfont, background=pcolor)
powlbl.grid(row=0, column=8, sticky=NSEW)
natv = IntVar()
powcb = Checkbutton(f1b, text="Natural", variable=natv, command=ckpowr,
                    font=fdfont, relief='raised', background=pcolor)
powcb.grid(row=0, column=9, sticky=NSEW)
setpwr(power)
f1b.grid(row=1, columnspan=2, sticky=NSEW)
# Network window
lblnet = Label(f1b, text="Network Status", font=fdfont, foreground='royalblue', background='gold')
lblnet.grid(row=2, column=0, columnspan=9, sticky=NSEW)
# Node window
lblnode = Label(f1b, text="My Node: %s" % node, font=fdfont, foreground='royalblue', background='lightgrey')
lblnode.grid(row=2, column=9, columnspan=1, sticky=NSEW)
# Whos on First Window to display operators on bands
# lblwof = Label(f1b, text="", font=fdfont, foreground='royalblue', background='lightgrey')
# lblwof.grid(row=2, column=0, columnspan=9, sticky=NSEW)
# Port window
# lblport = Label(f1b, text="Port: %s" % port_base, font=fdfont, foreground='royalblue', background='lightgrey')
# lblport.grid(row=3, column=9, columnspan=1, sticky=NSEW)
# log window
logw = Text(root, takefocus=0, height=11, width=80, font=fdmfont,
            background='lightgrey', wrap=NONE, setgrid=1)
# logw.configure(cursor='arrow')
scroll = Scrollbar(root, command=logw.yview, background='lightgrey')
logw.configure(yscrollcommand=scroll.set)
logw.grid(row=2, column=0, sticky=NSEW)
scroll.grid(row=2, column=1, sticky=NS)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
# txtbillb = dialog window
txtbillb = Text(root, takefocus=1, height=10, width=80, font=fdmfont,
                wrap=NONE, setgrid=1, background='lightgrey')
scrollt = Scrollbar(root, command=txtbillb.yview)
txtbillb.configure(yscrollcommand=scrollt.set)
txtbillb.grid(row=3, column=0, sticky=NSEW)
scrollt.grid(row=3, column=1, sticky=NS)
root.grid_rowconfigure(3, weight=1)
logw.tag_config("b", foreground="royalblue")
logw.insert(END, "          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", ("b"))
logw.insert(END, "                            DATABASE DISPLAY WINDOW\n", ("b"))
logw.insert(END, "          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", ("b"))
logw.insert(END, "%s\n" % prog, ("b"))
#     Add a bottom window for station information
# f1c = Frame(root, bd=1)
# f1c.grid(row=4,columnspan=4,sticky=NSEW)
#     Add entry box for entering data
# entqsl = Entry(f1c,font=fdfont,background='lightgrey')
# entqsl.grid(row=4,column=0,sticky=NSEW)
# txtentry = Text(f1c,takefocus=1,height=2,width=39,font=fdmfont,\
# wrap=NONE,setgrid=1)
# txtentry.grid(row=4,column=4,sticky=NSEW)
# root.grid_rowconfigure(4,weight=1)
# txtentry.insert(END,"Call-Class-Sect- \n")
# fth2lbl = Label(f1c,text="-\n<",font=fdfont,background='lightgrey')
# fth2lbl.grid(row=4,column=3,sticky=NSEW)
# Phonetics box
# fthw2 = Text(f1c,takefocus=0,height=2,width=40,font=fdmfont,\
#            background='lightgrey',wrap=NONE,setgrid=1)
# fthw2.configure(cursor='arrow')
# fthw2.grid(row=4,column=2,sticky=NSEW)
# root.grid_rowconfigure(4,weight=1)
# fthw2.insert(END,"phonetics box")
# txtentry.insert(END,"\n")
# startup
contestlog(0)  # define globals
buildmenus()
sms = syncmsg()  # setup sync message service
qdb = qsodb()  # init qso database
qdb.loadfile()  # read log file
print "Showing GUI"
print
if node == gd.getv('tmast'):
    print "This Node is the TIME MASTER!!"
    print "THIS COMPUTER'S CLOCK BETTER BE RIGHT (preferably GPS locked)"
    print "User should Insure that system time is within 1 second of the"
    print "  correct time and that the CORRECT TIMEZONE is selected (in the OS)"
    print
else:
    print "User should Insure that System Time is within a few seconds of the"
    print "  correct time and that the CORRECT TIMEZONE is selected (in the OS)"
print "To change system time, stop FDLog, change the time or zone, then restart"
print
# These root commands were removed without an explanation in the beta.
# but will leave them in.
root.update()
root.deiconify()
net.start()  # start threads
renew_title()
txtbillb.insert(END, "          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", ("b"))
txtbillb.insert(END, "                              Dialogue Window\n", ("b"))
txtbillb.insert(END, "          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n", ("b"))
txtbillb.insert(END, "Please select the Operator, Logger, Power and Band/Mode in pink above.\n\n")
txtbillb.insert(END, "-Call-Class-Sect- \n")
txtbillb.config(insertwidth=3)
txtbillb.focus_set()


def topper():
    """This will reset the display for input"""
    txtbillb.insert(END, "\n")
    txtbillb.insert(END, "-Call-Class-Sect- \n")


def showthiscall(call):
    "show the log entries for this call"
    p = call.split('/')
    #    print p[0]
    findany = 0
    m, dummy, dummy = qdb.cleanlog()
    #    print m.values()
    for i in m.values():
        #        print i.call
        q = i.call.split('/')
        if p[0] == q[0]:
            if findany == 0: txtbillb.insert(END, "\n")
            txtbillb.insert(END, "%s\n" % i.prlogln(i))
            findany = 1
    return findany


# added this to take out the keyhelp from the code
def mhelp():
    viewtextf('Keyhelp.txt')

secName = {}

def readSections():
    """this will read the Arrl_sect.dat file for sections"""
    # This modified from Alan Biocca version 153d
    try:
        fd = file("Arrl_sect.dat","r")  # read section data
        while 1:
            ln = fd.readline().strip()          # read a line and put in db
            if not ln: break
            if ln[0] == '#': continue
            try:
                sec, dummy, dummy, dummy = string.split(ln,None,3)
                secName[sec] = sec
            except ValueError,e:
                print "rd arrl sec dat err, itm skpd: ",e
        fd.close()
    except IOError,e:
        print "read error during readSections", e

readSections()


def proc_key(ch):
    "process keystroke"
    global kbuf, power, operator, logger, debug, band, node, suffix, tdwin, goBack  # timeok
    testq = 0
    if ch == '?' and (kbuf == "" or kbuf[0] != '#'):  # ? for help
        mhelp()
        return
    # Adding a statement to check for uppercase. Previously unresponsive while capped locked
    # Thanks to WW9A Brian Smith for pointing out that the program isn't randomly frozen and not requiring a restart.
    if ch.isupper():
        txtbillb.insert(END, " LOWERCAPS PLEASE \n")
        kbuf = ""
        topper()
        return
    if ch == '\r':  # return, may be cmd or log entry
        if kbuf[:1] == '#':
            qdb.qst(kbuf[1:])
            kbuf = ""
            txtbillb.insert(END, '\n')
            return
        # check for valid commands
        if re.match(r'[.]h$', kbuf):  # help request
            m = """
                .band 160/80/40/20/15/10/6/2/220/440/900/1200/sat c/d/p
                .off               change band to off
                .pow <dddn>        power level in integer watts (suffix n for natural)
                .node <call-n>     set id of this log node
                .testq <n>         generate n test qsos (only in test mode)
                .tdwin <sec>       display node bcasts exceeding this time skew
                .st                this station status
                .re                summary band report
                .ba                station band report
                .pr                generate entry and log files"""
            viewtextv(m, 'Command Help')
            kbuf = ""
            txtbillb.insert(END, '\n')
            return
        pwr, s = testcmd(".pow", r"[0-9]{1,4}n?", power)
        if s is True:
            power = pwr
            setpwr(power)
        netsync.rem_host, s = testcmd('.remip', r'([0-9]{1,3}[.]){3}[0-9]{1,3}', netsync.rem_host)
        if s: globDb.put('remip', netsync.rem_host)
        # This change was made below for debug, tdwin, and testq
        v, s = testcmd(".debug", r"[0-9]+", debug)
        if s is True: debug = int(v)
        v, s = testcmd(".tdwin", r"[0-9]{1,3}", tdwin)
        if s is True: tdwin = int(v)
        v, s = testcmd(".testq", r"[0-9]{1,2}", testq)
        if s is True: testq = int(v)
        if testq: testqgen(testq)
        saveglob()
        renew_title()
        m = re.match(r"[.]set ([a-z0-9]{3,6}) (.*)$", kbuf)
        if m:
            name, val = m.group(1, 2)
            r = gd.setv(name, val, now())
            if r:
                txtbillb.insert(END, "\n%s\n" % r)
            else:
                txtbillb.insert(END, "\n")
                qdb.globalshare(name, val)  # global to db
            kbuf = ""
            renew_title()
            return
        m = re.match(r"[.]band (((160|80|40|20|15|10|6|2|220|440|900|1200|sat)[cdp])|off)", kbuf)
        if m:
            print
            nb = m.group(1)
            kbuf = ""
            txtbillb.insert(END, "\n")
            bandset(nb)
            return
        if re.match(r'[.]off$', kbuf):
            bandoff()
            kbuf = ""
            txtbillb.insert(END, "\n")
            return
        if re.match(r'[.]ba$', kbuf):
            qdb.bands()
            kbuf = ""
            txtbillb.insert(END, "\n")
            return
        if re.match(r'[.]pr$', kbuf):
            contestlog(1)
            txtbillb.insert(END, " Entry/Log File Written\n")
            txtbillb.insert(END, "\n")
            kbuf = ""
            return
        p = r'[.]edit ([a-z0-9]{1,6})'
        if re.match(p, kbuf):
            m = re.match(p, kbuf)
            call = m.group(1)
            #  qdb.delete(nod,seq,reason)
            kbuf = ""
            txtbillb.insert(END, "To edit: click on the log entry\n")
            return
        #Found that .node needed fixing. Reworked
        if re.match(r'[.]node', kbuf):
            if band != 'off':
                txtbillb.insert(END, "\nSet band off before changing node id\n")
                kbuf = ""
                return
            else:
                nde, s = testcmd(".node", r"[a-z0-9-]{1,8}", node)
                if s is True:
                    node = nde
                    setnode(node)
            kbuf = ""
            txtbillb.insert(END, "\n")
            topper()                
            return
        if re.match(r'[.]st$', kbuf):  # status  xx mv to gui
            print
            print
            print "FD Call   %s" % string.upper(gd.getv('fdcall'))
            print "GOTA Call %s" % string.upper(gd.getv('gcall'))
            print "FD Report %s %s" % (string.upper(gd.getv('class')), gd.getv('sect'))
            print "Band      %s" % band
            print "Power     %s" % power
            print "Operator  %s" % operator
            print "Logger    %s" % logger
            print "Node      %s" % node
            if authk != "" and node != "":
                print "Net       enabled"
            else:
                print "Net       disabled"
            print
            kbuf = ""
            txtbillb.insert(END, "\n")
            return
        if re.match(r'[.]re$', kbuf):  # report  xx mv to gui
            print
            print "  band  cw q   pwr dig q   pwr fon q   pwr"
            qpb, ppb, dummy, dummy, dummy, tq, score, maxp, dummy, dummy, dummy, dummy, dummy, dummy, dummy = qdb.bandrpt()
            for b in (160, 80, 40, 20, 15, 10, 6, 2, 220, 440, 1200, 'sat', 'gota'):
                print "%6s" % b,
                for m in 'cdp':
                    bm = "%s%s" % (b, m)
                    print "%5s %5s" % (qpb.get(bm, 0), ppb.get(bm, 0)),
                print
            print
            print "%s total Qs, %s QSO points," % (tq, score),
            print maxp, "watts maximum power"
            kbuf = ""
            txtbillb.insert(END, "\n")
            topper()
            return
        if kbuf and kbuf[0] == '.':  # detect invalid command
            txtbillb.insert(END, " Invalid Command\n")
            kbuf = ""
            txtbillb.insert(END, "\n")
            topper()
            return
        # check for valid contact
        if (ch == '\r'):
            stat, ftm, dummy, sfx, call, xcall, rept = qdb.qparse(kbuf)
            goBack = "%s %s" % (call, rept)# for the up arrow enhancement
            if stat == 5:  # whole qso parsed
                kbuf = ""
                if len(node) < 3:
                    txtbillb.insert(END, " ERROR, set .node <call> before logging\n")
                    topper()
                elif qdb.dupck(xcall, band):  # dup check
                    txtbillb.insert(END, "\n\n ***DUPE*** on band %s ***DUPE***\n" % band)
                    topper()
                elif qdb.partck(xcall): # Participant check
                    txtbillb.insert(END, "\n Participant - not allowed \n")
                    topper()
                elif xcall == string.lower(gd.getv('fdcall')):
                    txtbillb.insert(END, "\n That's us - not allowed \n")
                    topper()
                elif xcall == string.lower(gd.getv('gcall')):
                    txtbillb.insert(END, "\n That's us - not allowed \n")
                    topper()
                else:
                    # Added database protection against no band, no power,
                    # no op, and no logger
                    # Added warning against 1D to 1D contacts being
                    # logged but not counting points
                    # Checking Operator or Logger has a license
                    legal = 0
                    if re.match(r'[a-z :]+ [a-zA-Z ]+, ([a-z0-9]+)',operator):
                        #print "%s has a license" % operator
                        legal = legal + 1
                    if re.match(r'[a-z :]+ [a-zA-Z ]+, ([a-z0-9]+)',logger):
                        #print "%s has a license" % logger
                        legal = legal + 1
                    if legal == 0:
                        txtbillb.insert(END, "\n\n  The Operator or the logger needs a license.\n")
                        txtbillb.insert(END, "  Please Try Again\n")
                        topper()
                        return
                    # checking for band, power, operator or logger
                    em = ''
                    if band == "off": em += " Band "
                    if power == 0: em += " Power "
                    if len(operator) < 2: em += " Operator "
                    if len(logger) < 2: em += " Logger "
                    if em != '':
                        txtbillb.insert(END, " - WARNING: ( %s ) NOT SET" % em)
                        txtbillb.insert(END, "  Please Try Again\n")
                        topper()
                        return
                    if em == '':
                        # This checks 1D to 1D contacts
                        clas = string.upper(gd.getv('class'))
                        rept1 = string.upper(rept)
                        if clas == '1D':
                            if clas in rept1:
                                txtbillb.insert(END, "\n 1D to 1D contacts are logged, but zero points! \n")
                                topper()
                        # check the report for valid fd or wfd classes:
                        # note according to the cheat sheet, \d is a digit
                        reptclass, dummy = rept.split(" ")
                        m = ""
                        if gd.getv('contst') == "fd":
                            # field day, report in: #+a-f
                            m = re.match(r'[\d][a-fA-F]', rept)
                        elif gd.getv('contst') == "wfd":
                            # WFD
                            m = re.match(r'[\d][ihoIHO]', rept)
                        else:
                            # vhf or other contest
                            # allow everything
                            m = "something"
                        if m == None: # match failed, do not allow and abort logging
                            txtbillb.insert(END, " - ERROR: Bad exchange ( %s ) Please Try Again\n" % rept)
                            topper()
                            return
                        # Check for valid section in report
                        aaaaa = len(rept1)
                        #print "aaaaa is %s" % aaaaa
                        rept2 = rept1[3:aaaaa].strip()
                        #print "rept2 is %s" % rept2
                        if rept2 in secName:
                            pass
                        else:
                            print "\n Use one of these for the section:"
                            kk = ""
                            nx = 0
                            ny = 0
                            for k in sorted(secName):
                                if ny == 0:
                                    kk += "\n  "
                                    ny = ny + 1
                                kk += str(k) + ", "
                                nx = nx + 1
                                if nx == 17:  # how many sections to the line
                                    ny = ny + 1
                                    if ny < 6:  # last line gets the rest
                                        kk += "\n  "
                                        nx = 0
                            print kk
                            #print('\n'.join("{} : {}".format(k, v) for k, v in secName.items()))
                            txtbillb.insert(END, kk)
                            txtbillb.insert(END, "\n  Please try one of the sections above.")
                            topper()
                            return
                        # The entry is good and ready to log
                        txtbillb.insert(END, " - QSL!  May I have another?")
                        txtbillb.insert(END, "\n")
                        topper()
                        tm = now()
                        if ftm:  # force timestamp
                            tm = tm[0:4] + ftm[0:8] + tm[11:]  # yymmdd.hhmmss
                        qdb.qsl(tm, xcall, band, rept)
            elif stat == 4:
                kbuf = ""
                # Added participant check here too
                if qdb.partck(xcall): # Participant check
                    txtbillb.insert(END, "\n Participant - not allowed \n")
                    topper()
                elif showthiscall(call) == 0:
                    txtbillb.insert(END, " none found\n")
                    topper()
            return
    if ch == '\x1b':  # escape quits this input line
        txtbillb.insert(END, " ESC -aborted line-\n")
        topper()
        kbuf = ""
        return
    if ch == '\b':  # backspace erases char
        if kbuf != "":
            kbuf = kbuf[0:-1]
            txtbillb.delete('end - 2 chars')
        return
    if ch == '\u1p':  # up arrow reprints the input line
        if goBack != "":
            if kbuf == "":
                txtbillb.insert(END, goBack) #print goBack info
                kbuf = goBack
            else: 
                return
        else:
            kbuf = ""
        return
    if ch == ' ':  # space, check for prefix/suffix/call
        stat, tm, dummy, sfx, call, xcall, rept = qdb.qparse(kbuf)
        if stat == 2:  # suffix, dup check
            suffix = kbuf
            kbuf = ""
            r = qdb.sfx2call(suffix, band)
            if not r: r = 'None'
            txtbillb.insert(END, ": %s on band '%s'\n" % (r, band))
            return
        if stat == 3:  # prefix, combine w suffix
            stat, tm, dummy, sfx, call, xcall, rept = qdb.qparse(kbuf + suffix)
            if stat == 4:  # whole call
                kbuf += suffix
                txtbillb.insert(END, sfx)  # fall into call dup ck
        if stat == 4:  # whole call, dup chk
            if qdb.dupck(xcall, band):
                txtbillb.insert(END, "\n\n ***DUPE*** on band %s ***DUPE***" % band)
                showthiscall(call)
                kbuf = ""
                topper()
            elif qdb.partck(xcall): # Participant check
                txtbillb.insert(END, "\n Participant - not allowed \n")
                showthiscall(call)
                kbuf = ""
                topper()
            else:
                kbuf += ' '
                txtbillb.insert(END, ch)
                if showthiscall(call):  # shows the previous contacts with this station
                    txtbillb.insert(END, "%s " % xcall)
            return
    buf = kbuf + ch  # echo & add legal char to kbd buf
    if len(buf) < 50:
        if buf[0] == '.':
            if re.match(r'[ a-zA-Z0-9.,/@-]{0,45}$', ch):
                kbuf = buf
                txtbillb.insert(END, ch)
        elif buf[0] == '#':
            if re.match(r'#[ a-zA-Z0-9.,?/!@$;:+=%&()-]{0,40}$', buf):
                kbuf = buf
                txtbillb.insert(END, ch)
        else:
            stat, tm, dummy, sfx, call, xcall, rept = qdb.qparse(buf)
            if stat > 0 and len(buf) < 50:
                kbuf = buf
                txtbillb.insert(END, ch)


def kevent(event):
    "keyboard event handler"
    global goBack
    #    print "event '%s' '%s' '%s'"%(event.type,event.keysym,event.keysym_num)
    k = event.keysym_num
    if 31 < k < 123:  # space to z
        proc_key(chr(event.keysym_num))
    elif k == 65362:  # up arrow
        proc_key('\u1p')
    elif k == 65288:  # backspace
        proc_key('\b')
    elif k == 65307:  # ESC
        proc_key('\x1b')
    elif k == 65293:  # return
        proc_key('\r')
    txtbillb.see(END)  # Ensure that it stays in view
    return "break"  # prevent further processing on kbd events


def focevent(e):
    txtbillb.mark_set('insert', END)
    return "break"



def edit_dialog(node, seq):
    'edit log entry'
    dummy = Edit_Dialog(root, node, seq)

    
def log_select(e):
    'process mouse left-click on log window'
    #    print e.x,e.y
    t = logw.index("@%d,%d" % (e.x, e.y))
    #    print t
    line, dummy = t.split('.')
    line = int(line)
    #    print line
    logtext = logw.get('%d.0' % line, '%d.82' % line)
    # print logtext
    dummy = logtext[0:8].strip()
    seq = logtext[65:69].strip()
    bxnd = logtext[8:14].strip()
    cxll = logtext[15:22].strip()
    #  In case user clicks on a deleted log entry
    baddd = logtext[23:24].strip()
    if baddd == '*':
        print "Can't edit a delete entry"
        return 'break'
    if len(seq) == 0: return 'break'
    #    In case user clicks on tildes
    if seq == '~~~~': return 'break'
    # fixed clicking on the copywrite line gave a valueerror
    try:
        seq = int(seq)
        stn = logtext[69:].strip()
        if len(stn) == 0: return 'break'
    except ValueError:
        return 'break'
    print stn, seq, bxnd, cxll
    if stn == node:  # only edit my own Q's
        # Also check to make sure the call isn't previously deleted
        if qdb.dupck(cxll, bxnd):
            # Now we check to see if the entry is still in the log
            bid, dummy, dummy = qdb.cleanlog()  # get a clean log
            stnseq = stn +"|"+str(seq)
            if stnseq in bid:
                edit_dialog(stn, seq)
            else:
                print "Previously edited contact - Not in the log."
                return
        else:
            print "This is not a log entry."
    else:
        print "Cannot edit another person's contact."
    return 'break'

updatect = 0


# This function updated from 152i
def update():
    "timed updater"
    global updatect
    root.after(1000, update)  # reschedule early for reliability
    sms.prout()  # 1 hz items
    updatebb()
    net.si.age_data()
    mclock.adjust()
    #   if mclock.level == 0:  # time master broadcasts time more frequently
    #   net.bcast_time()
    updatect += 1
    # if (updatect % 5) == 0:         # 5 sec
    # net.bcast_now()
    if (updatect % 10) == 0:  # 10 sec
        updateqct()  # this updates rcv packet fail
        renew_title()  # this sends status broadcast
    if (updatect % 30) == 0:  # 30 sec
        mclock.update()
    if updatect > 59:  # 60 sec
        updatect = 0
root.bind('<ButtonRelease-1>', focevent)
txtbillb.bind('<KeyPress>', kevent)
logw.bind('<KeyPress>', kevent)  # use del key for?xx
logw.bind('<Button-1>', log_select)  # start of log edit
root.after(1000, update)  # 1 hz activity
root.mainloop()  # gui up
print "\nShutting down"
# the end was updated from 152i
band = 'off'  # gui down, xmt band off, preparing to quit
net.bcast_now()  # push band out
time.sleep(0.2)
saveglob()  # save globals
print "  globals saved"
print "\n\nFDLog has shut down."
time.sleep(0.5)
# os._exit(1)  # kill the process somehow?
exit(1)

# Suggestions/To Do:
#
#  Grab out of order entry from Alan Biocca's FDLog. 
#
#  Change Participant entry so the name is on top. (It's odd to ask their initials first.)
#
#  Would love another file to use for the "InfoNode" computer
        # It will allow visitors/participants to log in
        # It will show top 5 operators and top 5 loggers
        # It will show worked all states
        # Provide info on Amateur Radio (video and/or short articles to print?)
        # Provide info on the local club
        # fool-proof - no logging from this node.
#
#  add node list display after db read during startup?
#
#  add phonetic alphabet display (started: some code commented out)
#
#  Weo suggested making Control-C text copy/paste work. (suggestion from original group - FDLog)
#
#  Tried and tried to get wof (whoseonfirst) to return only one value for the mouse over.
#    I don't have the python skilz... If you can awesome!!!
#
# eof
