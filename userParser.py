#!/usr/bin/python
mails = []
try:
	while True:
		mails.append(input())
except(EOFError):
	pass

for i in range(len(mails)):
	if i%3000==0:
		f=open('users/list'+str(i/3000)+'.dat', 'w')
		f.write('list'+str(i/3000)+'@ieee.metu.edu.tr\n')
	f.write(mails[i]+'\n')
		
