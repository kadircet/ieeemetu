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

def insertMember(reqId, resp, exception):
    global c
    if exception:
        if "Member already exists" not in exception._get_reason():
            print("Failed to add", reqId, exception._get_reason())
    else:
        c+=1
        print("Succesfully added", reqId)
    return
    
def addMember(gId, email, hideExist=False):
    params = {'groupKey': gId, 'body': {'email':email}}
    try:
        #directory_service.members().insert(**params).execute()
        #print(email, "successfully added.")
        batch.add(directory_service.members().insert(**params),callback=insertMember)
    except errors.HttpError as error:
        print(email, error._get_reason())
        
def createGroup(gId):
    params = {'body': {'email': gId}}
    res=None
    try:
        res = directory_service.groups().insert(**params).execute()
    except errors.HttpError as error:
        print(gId, error._get_reason())
    try:
        params = {'groupUniqueId': gId, 
                    'body': {'whoCanPostMessage': 'ALL_MANAGERS_CAN_POST', 
                            'whoCanViewMembership': 'ALL_MANAGERS_CAN_VIEW'}
                }
        serv.groups().update(**params).execute()
    except errors.HttpError as error:
        print(gId, error._get_reason())
    return res

http = Auth('settings.json')
directory_service = build('admin', 'directory_v1', http=http)
serv = build('groupssettings', 'v1', http=http)
batch = BatchHttpRequest()
c=0
i=0
try:
    gId = input()
    createGroup(gId)
    addMember('genelduyuru@ieee.metu.edu.tr', gId, True)
    user = input()
    while True:
        user = user.strip()
        if len(user)>0:
            addMember(gId, user)
        user = input()
        i+=1
        if i==500:
            try:
                batch.execute()
                print("Done a batch")
            except errors.HttpError as error:
                print(gId, error._get_reason())
            batch = BatchHttpRequest()
            i=0
except EOFError as e:
    try:
        batch.execute()
        #pass
    except errors.HttpError as error:
        print(gId, error._get_reason())

print(c, "users added to group", gId)

