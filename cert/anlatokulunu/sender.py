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
ODTÜ GÜÇ VE ENERJI KONGRESİ sertifikaniz ektedir, etkinligimize katiliminiz icin cok tesekkur ederiz.
Eger fiziksel olarak da istiyorsaniz lutfen
bu maile cevap olarak bu hafta cuma gunune kadar(yani en gec 16 Haziran 23.59'a kadar) belirtiniz.
Cuma gununden itibaren Elektrik Elektronik A Blok'taki topluluk odamizdan alabilirsiniz."""

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
    mail['from'] = 'info@ieee.metu.edu.tr'
    mail['subject'] = 'ODTÜ GÜÇ VE ENERJI KONGRESİ Sertifikasi'

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

a="""Yana Klavkina
Ayşe Doğan
Rüzgar Tunca Altıncı
Hüseyin Deniz Yılmaz
Ege Tunalı
Mehmet Arda Alper
Baran Üyükuş
Barış Demirel
Bora Yılmaz
Ata Batuhan Kurt
Tomris Karaismailoğlu
Yavuz ERİNÇ
Fatih TOLA
Yaşariye YALÇIN
Ayşe UĞURER TURGUT
Sıla Nur Karaman"""
def processUsers():
    global a
    r=a.split('\n')
    for user in r:
        #data=user.split(',')
        #print(data)
        sed=subprocess.Popen(['/usr/bin/sed', 's/NAME/%s/g'%user, 'cert2.tex'], stdout=subprocess.PIPE)
        sed.wait()
        subprocess.Popen(['/usr/bin/pdflatex'], stdin=sed.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
        subprocess.Popen(['/usr/bin/mv', 'texput.pdf', 'phy/%s.pdf'%user]).wait()
        #sendMail(data[4], msgKGG%(data[0]+" "+data[1]).upper(), 'phy/%s.pdf'%(data[0]+data[1]))
        #print("Send",data[0],data[4])

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
