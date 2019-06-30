#!/usr/bin/python

# new participant setup
class NewParticipantDialog():
    """ this is the new participant window that pops up"""

    def dialog(self):
        if node == "":
            txtbillb.insert(END, "err - no node\n")
            return
        s = NewParticipantDialog()
        s.t = Toplevel(root)
        s.t.transient(root)
        s.t.title('Add New Participant')
        fr1 = Frame(s.t)
        fr1.grid(row=0, column=0)
        Label(fr1, text='Initials   ', font=fdbfont).grid(row=0, column=0, sticky=W)
        s.initials = Entry(fr1, width=3, font=fdbfont, validate='focusout', validatecommand=s.lookup)
        s.initials.grid(row=0, column=1, sticky=W)
        s.initials.focus()
        Label(fr1, text='Name', font=fdbfont).grid(row=1, column=0, sticky=W)
        s.name = Entry(fr1, width=20, font=fdbfont)
        s.name.grid(row=1, column=1, sticky=W)
        Label(fr1, text='Call', font=fdbfont).grid(row=2, column=0, sticky=W)
        s.call = Entry(fr1, width=6, font=fdbfont)
        s.call.grid(row=2, column=1, sticky=W)
        Label(fr1, text='Age', font=fdbfont).grid(row=3, column=0, sticky=W)
        s.age = Entry(fr1, width=2, font=fdbfont)
        s.age.grid(row=3, column=1, sticky=W)
        Label(fr1, text='Visitor Title', font=fdbfont).grid(row=4, column=0, sticky=W)
        s.vist = Entry(fr1, width=20, font=fdbfont)
        s.vist.grid(row=4, column=1, sticky=W)
        fr2 = Frame(s.t)
        fr2.grid(row=1, column=0, sticky=EW, pady=3)
        fr2.grid_columnconfigure((0, 1), weight=1)
        Label(fr2, text='<Enter>=Save', font=fdbfont, foreground='red').grid(row=3, column=0, sticky=W)
        #Button(fr2, text='Save', font=fdbfont, command=s.applybtn) .grid(row=3, column=1, sticky=EW, padx=3)
        Button(fr2, text='Dismiss', font=fdbfont, command=s.quitbtn) .grid(row=3, column=2, sticky=EW, padx=3)
        # Bound enter key to save entries
        s.t.bind('<Return>', lambda event: s.applybtn)

    def lookup(self):
        # constrain focus to initials until they are ok
        initials = string.lower(self.initials.get())
        if not re.match(r'[a-zA-Z]{2,3}$', initials):
            # self.initials.delete(0,END)
            self.initials.configure(bg='gold')
            self.initials.focus()
        else:
            self.initials.configure(bg='white')
            dummy, name, call, age, vist = string.split(participants.get(initials, ', , , , '), ', ')
            self.name.delete(0, END)
            self.name.insert(END, name)
            self.call.delete(0, END)
            self.call.insert(END, call)
            self.age.delete(0, END)
            if age == 0:
                pass
            else:
                self.age.insert(END, age)
            self.vist.delete(0, END)
            if vist == "":
                pass
            else:
                self.vist.insert(END, vist)
        return 1
    
    @property   #This added so I can use the <Return> binding
    def applybtn(self):
        global participants
        # print "store"
        initials = self.initials.get().lower()
        name = self.name.get()
        call = string.lower(self.call.get())
        age = string.lower(self.age.get())
        vist = string.lower(self.vist.get())
        self.initials.configure(bg='white')
        self.name.configure(bg='white')
        self.call.configure(bg='white')
        self.age.configure(bg='white')
        self.vist.configure(bg='white')
        if not re.match(r'[a-zA-Z]{2,3}$', initials):
            txtbillb.insert(END, "error in initials\n")
            txtbillb.see(END)
            topper()
            self.initials.focus()
            self.initials.configure(bg='gold')
        elif not re.match(r'[A-Za-z ]{4,20}$', name):
            txtbillb.insert(END, "error in name\n")
            txtbillb.see(END)
            topper()
            self.name.focus()
            self.name.configure(bg='gold')
        elif not re.match(r'([a-zA-Z0-9]{3,6})?$', call):
            txtbillb.insert(END, "error in call\n")
            txtbillb.see(END)
            topper()
            self.call.focus()
            self.call.configure(bg='gold')
        elif not re.match(r'([0-9]{1,2})?$', age):
            txtbillb.insert(END, "error in age\n")
            txtbillb.see(END)
            topper()
            self.age.focus()
            self.age.configure(bg='gold')
        elif not re.match(r'([a-zA-Z0-9]{4,20})?$', vist):
            txtbillb.insert(END, "error in title\n")
            txtbillb.see(END)
            topper()
            self.vist.focus()
            self.vist.configure(bg='gold')
        else:
            # Enter the Participant in the dictionary
            initials
            nam = "p:%s" % initials
            v = "%s, %s, %s, %s, %s" % (initials, name, call, age, vist)
            participants[initials] = v
            dummy = qdb.globalshare(nam, v)  # store + bcast
            txtbillb.insert(END, "\a New Participant Entered.")
            print "\a"
            txtbillb.see(END)
            topper()
            self.initials.delete(0, END)
            self.name.delete(0, END)
            self.call.delete(0, END)
            self.age.delete(0, END)
            self.vist.delete(0, END)
            self.initials.focus()
            buildmenus()

    def quitbtn(self):
        self.t.destroy()
