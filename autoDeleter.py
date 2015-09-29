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
import userDeleter
import base64
from email.mime.text import MIMEText

table = {
    'ş': 's', 'Ş': 'S', 'ı': 'i', 'İ': 'I', 'ç': 'c', 'Ç': 'C',
    'ü': 'u', 'Ü': 'U', 'ö': 'o', 'Ö': 'O', 'ğ': 'g', 'Ğ': 'G'
}
table = {ord(a):ord(b) for a,b in table.items()}

msgSuccess = "Your mail address has been deleted from our mail list successfully."
msgError = "The mail address you provided does not seem to be in our mail list, please make sure that you send your unsubscribe request from the address you are receiving the mail, not from a forwarded address."

def Auth(setFile):
	settings = json.load(open(setFile))
	storage = Storage(settings['STORAGE_FILE'])
	credentials = storage.get()
	if credentials == None or credentials.invalid:
		flow = OAuth2WebServerFlow(settings['CLIENT_ID'], settings['CLIENT_SECRET'], 
				settings['OAUTH_SCOPE'], settings['REDIRECT_URI'])
		credentials = run_flow(flow,storage,flags)
	return credentials.authorize(http=httplib2.Http())

def getUsersMails(uId='me', query=''):
	mails = []
	page_token = None
	params = {'userId': uId, 'q': query}

	while True:
		try:
			if page_token:
				params['pageToken'] = page_token
			current_page = gmail_service.users().messages().list(**params).execute()
		
			if 'messages' in current_page:
				mails.extend(current_page['messages'])
			page_token = current_page.get('nextPageToken')
			if not page_token:
				break
		except errors.HttpError as error:
			print('An error occurred: %s' % error)
			break
	return mails

def getMailHeaders(mId, uId='me'):
    params = {'id': mId, 'userId': uId}
    res = {}
    
    try:
        resp = gmail_service.users().messages().get(**params).execute()
        headers = resp['payload']['headers']
        for header in headers:
            res[header['name'].lower()] = header['value'].translate(table)
    except errors.HttpError as e:
        print('An error occured: %s' % e)
    
    return res

def processMail(mId, uId='me'):
    params = {
            'id': mId, 
            'userId': uId, 
            'body': {
                'removeLabelIds':['UNREAD', 'INBOX'],
                'addLabelIds':['Label_1']
            }
    }
    try:
        gmail_service.users().messages().modify(**params).execute()
    except errors.HttpError as e:
        print('An error occured: %s' % e)

def sendMail(to, msg):
    msg = MIMEText(msg)
    msg['to'] = to
    msg['from'] = 'info@ieee.metu.edu.tr'
    msg['subject'] = 'Unsubscribe Request'
    msg = base64.urlsafe_b64encode(bytes(msg.as_string(), 'utf8')).decode('utf8')
    params = {
            'userId': 'me',
            'body': {
                'raw': msg
            }
    }

    try:
        gmail_service.users().messages().send(**params).execute()
    except errors.HttpError as e:
        print('An error occured: %s' % e)

gmail_service = None
def main():
    global gmail_service
    try:
        gmail_service = build('gmail', 'v1', http=Auth('settings.json'))
        for mail in getUsersMails(uId='me', query='is:unread'):
            headers = getMailHeaders(mail['id'])
            if headers['subject'].lower() in ('cikis', 'quit'):
                processMail(mail['id'])
                user = headers['from']
                user = user[user.rfind('<')+1:-1]
                res = userDeleter.deleteMember(user)
                if res:
                    sendMail(user, msgSuccess)
                else:
                    sendMail(user, msgError)
    except errors.HttpError as e:
        print('An error occured: %s' % e)

if __name__=='__main__':
    main()
