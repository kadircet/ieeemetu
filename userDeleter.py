#!/usr/bin/python
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow,argparser
import argparse
from oauth2client.file import Storage
from apiclient.http import BatchHttpRequest
import json

def Auth(setFile):
	settings = json.load(open(setFile))
	storage = Storage(settings['STORAGE_FILE'])
	credentials = storage.get()
	if credentials == None or credentials.invalid:
		flow = OAuth2WebServerFlow(settings['CLIENT_ID'], settings['CLIENT_SECRET'], 
				settings['OAUTH_SCOPE'], settings['REDIRECT_URI'])
		credentials = run_flow(flow,storage,flags)
	return credentials.authorize(http=httplib2.Http())

def getMembersGroups(mId, domain='ieee.metu.edu.tr'):
	groups = []
	page_token = None
	params = {'domain': domain, 'userKey': mId}

	while True:
		try:
			if page_token:
				params['pageToken'] = page_token
			current_page = directory_service.groups().list(**params).execute()
		
			if 'groups' in current_page:
				groups.extend(current_page['groups'])
			page_token = current_page.get('nextPageToken')
			if not page_token:
				break
		except errors.HttpError as error:
			print('An error occurred: %s' % error)
			break
	return groups
	
def deleteMemberFromGroup(mId, gId):
    try:
        params = {'groupKey': gId, 'memberKey': mId}
        current_page = directory_service.members().delete(**params).execute()
        print("Deleted user", mId, "from group", gId)
    except errors.HttpError as error:
        print('An error occured: %s' % error._get_reason())

def deleteMember(mId):
    groups = getMembersGroups(mId)	
    if groups==[]:
        print("Member %s not found in any group" % mId)
        return False

    for group in groups:
        deleteMemberFromGroup(mId, group['email'])
    return True

directory_service = build('admin', 'directory_v1', http=Auth('settings.json'))
def main():
    mId = input().strip()
    deleteMember(mId)

if __name__ == '__main__':
    main()
