#!/usr/bin/python
# coding: utf8
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from oauth2client.file import Storage
from apiclient.http import BatchHttpRequest
import json
import userDeleter

table = {
    u'ş': u's', u'Ş': u'S', u'ı': u'i', u'İ': u'I', u'ç': u'c', u'Ç': u'C',
    u'ü': u'u', u'Ü': u'U', u'ö': u'o', u'Ö': u'O', u'ğ': u'g', u'Ğ': u'G'
}
table = {ord(a):ord(b) for a,b in table.iteritems()}
def Auth(setFile):
	settings = json.load(open(setFile))
	storage = Storage(settings['STORAGE_FILE'])
	credentials = storage.get()
	if credentials == None or credentials.invalid:
		flow = OAuth2WebServerFlow(settings['CLIENT_ID'], settings['CLIENT_SECRET'], 
				settings['OAUTH_SCOPE'], settings['REDIRECT_URI'])
		credentials = run(flow,storage)
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

    resp = gmail_service.users().messages().get(**params).execute()
    headers = resp['payload']['headers']
    res = {}
    for header in headers:
        res[header['name'].lower()] = header['value'].translate(table)
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
    gmail_service.users().messages().modify(**params).execute()

gmail_service = build('gmail', 'v1', http=Auth('settings.json'))
for mail in getUsersMails(uId='me', query='is:unread'):
    headers = getMailHeaders(mail['id'])
    if headers['subject'].lower() in ('cikis', 'quit'):
        processMail(mail['id'])
        user = headers['from']
        user = user[user.rfind('<')+1:-1]
        userDeleter.deleteMember(user)
