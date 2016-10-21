from Tkinter import *
import tkFont
from random import random as rand
from time import sleep

idu=0
def randUser(i=0,n=300):
    global idu
    if i==0:
        root.after_cancel(idu)
        userLb.config(fg="white")
    elif i==-1:
        userTx.set(userTx.get()[3:-3])
        idu=root.after(300, randUser, n)
        return
    elif i==n:
        userLb.config(fg="red")
        userTx.set("***"+userTx.get()+"***")
        idu=root.after(300, randUser, -1)
        return
    userTx.set(int(rand()*n)+1)
    root.after(int(2**(i*8./n)), randUser, i+1)

idg = 0
def randGift(i=0, n=300):
    global idg
    gifts=["a", "b", "c", "d"]
    
    if i==0:
        root.after_cancel(idg)
        giftLb.config(fg="white")
    elif i==-1:
        giftTx.set(giftTx.get()[3:-3])
        idg = root.after(300, randGift, n)
        return
    elif i==n:
        giftLb.config(fg="red")
        giftTx.set("***"+giftTx.get()+"***")
        idg = root.after(300, randGift, -1)
        return
    giftTx.set(gifts[int(rand()*len(gifts))])
    root.after(int(2**(i*8./n)), randGift, i+1)

root = Tk()

customFont = tkFont.Font(family="Helvetica", size=50)
userTx = StringVar()
giftTx = StringVar()
userLb = Label(root, textvariable=userTx, width=20, height=2, font=customFont)
giftLb = Label(root, textvariable=giftTx, width=20, height=2, font=customFont)
randUsr=Button(root, text="Choose User", command=randUser)
randGft=Button(root, text="Choose Gift", command=randGift)

userLb.pack()
giftLb.pack()
randUsr.pack(side=LEFT)
randGft.pack(side=RIGHT)

root.mainloop()
