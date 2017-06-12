#!/usr/bin/python
# coding: utf8
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow,argparser
import argparse
from oauth2client.file import Storage
from apiclient.http import BatchHttpRequest
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import mimetypes

msgKGG="""Merhabalar Sayin %s,
KGG sertifikaniz ektedir, eger fiziksel olarak da istiyorsaniz lutfen
bu maile cevap olarak bu hafta cuma gunune kadar(yani en gec 23 mart 23.59'a kadar) belirtiniz.
Onumuzdeki pazartesi gununden itibaren Elektrik Elektronik A Blok'taki topluluk odamizdan alabilirsiniz."""

parser = argparse.ArgumentParser(parents=[argparser])
flags = parser.parse_args()

def Auth(setFile):
    settings = json.load(open(setFile))
    storage = Storage(settings['STORAGE_FILE'])
    credentials = storage.get()
    if credentials == None or credentials.invalid:
        flow = OAuth2WebServerFlow(settings['CLIENT_ID'], settings['CLIENT_SECRET'], 
                settings['OAUTH_SCOPE'], settings['REDIRECT_URI'])
        credentials = run_flow(flow,storage,flags)
    return credentials.authorize(http=httplib2.Http())

def sendMail(to, msg, path):
    mail = MIMEMultipart()
    mail['to'] = to
    mail['to'] = 'kadir.cetinkaya@ieee.metu.edu.tr'
    mail['from'] = 'info@ieee.metu.edu.tr'
    mail['subject'] = 'KGG Sertifikasi'

    msg = MIMEText(msg)
    mail.attach(msg)

    content_type, encoding = mimetypes.guess_type(path)
    main_type, sub_type = content_type.split('/', 1)
    fp=open(path, 'rb')
    msg=MIMEApplication(fp.read())
    fp.close()
    msg.add_header('Content-Disposition', 'attachment', filename=path)
    mail.attach(msg)
    
    mail = base64.urlsafe_b64encode(bytes(mail.as_string(), 'utf8')).decode('utf8')
    params = {
            'userId': 'me',
            'body': {
                'raw': mail
            }
    }

    try:
        gmail_service.users().messages().send(**params).execute()
    except errors.HttpError as e:
        print('An error occured: %s' % e)

import requests
import subprocess
a=open('kgg17.org').read().split('\n')[1:]
a=[x.split(',') for x in a]
printed=[]

def processUsers():
    global a,b,printed
    #r=requests.get('http://localhost:8080/afterevent/sertifika.php')
    #r=[x.split(',') for x in r.text.split('\n')]
    #r=a.split('\n')
    r=[]
    for i in range(len(a)):
        if len(a[i])<5:
            print(a[i])
            continue
        r.append([a[i][1],i+10000,a[i][5]])
    for user in r:
        #data=user.split(',')
        data=user
        if len(data)<3:
            continue
        if data[2] not in b:
            continue
        printed.append(data[2])
        sed=subprocess.Popen(['/usr/bin/sed', 's/NAME/%s/g'%data[0], 'cert2.tex'], stdout=subprocess.PIPE)
        sed.wait()
        subprocess.Popen(['/usr/bin/pdflatex'], stdin=sed.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        subprocess.Popen(['/usr/bin/mv', 'texput.pdf', 'phy/%s.pdf'%data[1]]).wait()
        sendMail(data[2], msgKGG%data[0], 'phy/%s.pdf'%data[1])
        print("Send",data[0],data[2])
    for x in b:
        if x not in printed:
            print("didn't print",x)

gmail_service = None
def main():
    global gmail_service
    try:
        gmail_service = build('gmail', 'v1', http=Auth('settings.json'))
        processUsers()
    except errors.HttpError as e:
        print('An error occured: %s' % e)

if __name__=='__main__':
    main()
