#!/usr/bin/python
import httplib2
from apiclient import errors
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
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
		credentials = run(flow,storage)
	return credentials.authorize(http=httplib2.Http())
	
def getGroups(domain='ieee.metu.edu.tr'):
	page_token = None
	params = {'domain': domain}
	groups = []
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
			print 'An error occurred: %s' % error
			break
	return groups

def getGroupMembers(groupId):
	if groupId in count:
		return count[groupId]
	members=[]
	params = {'groupKey': groupId}
	page_token = None
	while True:
		try:
			if page_token:
				params['pageToken'] = page_token
			current_page = directory_service.members().list(**params).execute()
	
			if 'members' in current_page:
				for member in current_page['members']:
					if member['type'] == "GROUP":
						q=getGroupMembers(member['id'])
						for m in q:
							members.append(m)
					elif member['type']=="USER":
						members.append(member['email'])
			page_token = current_page.get('nextPageToken')
			if not page_token:
				break
		except errors.HttpError as error:
			print 'An error occurred: %s' % error
			break
	count[groupId]=list(set(members))
	return count[groupId]

directory_service = build('admin', 'directory_v1', http=Auth('settings.json'))

groups = getGroups()
count = {}
members=[]
tc = 0
if groups==[]:
	print "No groups found"
for group in groups:
	if group['id'] in count:
		q=count[group['id']]
	else:
		q=getGroupMembers(group['id'])
	members.extend(q)
	print "%-24s%-40s" % (group['name'], group['email']),"%5d" % len(q)
members = list(set(members))
print "Total Members:", len(members)

#for member in members:
#	print member
