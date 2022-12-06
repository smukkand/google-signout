# Author: shafeel.m@gmail.com | version: 1.0

# This python script was developed using simple example from 
# https://developers.google.com/admin-sdk/directory/v1/quickstart/python
#
# Make sure that the user who executes this script already granted access to 
# use the API. Contact GSuite Administrator and Enterprise Security to enable 
# this role.

from __future__ import print_function
from curses.ascii import EM

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from os import path
import pickle,json,sys,signal

# If modifying these scopes, delete the file token.pickle. Please refer to API documentation to set
# specific 
# ------------ DirectoryAPI > Signout:User ----------
# https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list
# https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/signOut

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user.readonly',
    'https://www.googleapis.com/auth/admin.directory.user.security'
    ]

path_prefix = "/opt/cloudSec/ceaser/scripts/google-signout/"
pickleName = path_prefix + 'tokengroup.pickle'
credsName = path_prefix + 'credentials.json'

user_prefix = "usersList/"
ignrList = path_prefix + user_prefix + 'excludeList.txt'
inclList = path_prefix + user_prefix + 'includeList.txt'
wholeList = path_prefix + user_prefix + 'allGoogleUsers.txt'
debug = False

def sigint_handler(signal, frame):
    print ('[-] Interrupted. Quiting...')
    sys.exit(1)

def debugPrint(x):
    if debug:
        if type(x) == str:
            sys.stderr.write(x)
            sys.stderr.write("\n")
            sys.stderr.flush()

##LoginService: Authenticate the credentials and create access/refresh token pickle
def getService():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(pickleName):
        debugPrint('[DEBUG] pickle {0} already exists'.format(pickleName))
        with open(pickleName, 'rb') as token:
            creds = pickle.load(token)
        debugPrint('[DEBUG] creds was loaded from pickle {0}'.format(pickleName))

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            debugPrint('[DEBUG] creds {0} is expired and need to refresh the token.'.format(pickleName))
            creds.refresh(Request())
        else:
            debugPrint('[DEBUG] No active creds. Requesting a new one.')
            flow = InstalledAppFlow.from_client_secrets_file(
                credsName, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(pickleName, 'wb') as token:
            pickle.dump(creds, token)
        debugPrint('[DEBUG] Dumping requested creds to pickle.')

    # refer to this API document if there is a change in SCOPE above 
    # https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build
    __service = build('admin', 'directory_v1', credentials=creds)
    return __service

##List all the users from domain function: Takes the Service input::
def listUsers(serv):
    __results = None
    try:
        print ("[+] Fetching users from google workspace.... \n")
        __results = serv.users().list(customer='my_customer', maxResults=500, orderBy='email').execute()
        users = __results.get('users', [])
        nextPageToken = __results.get('nextPageToken', "")
        while nextPageToken:
            __results = serv.users().list(customer='my_customer', maxResults=500, orderBy='email', pageToken=nextPageToken).execute()
            nextPageToken = __results.get('nextPageToken', "")
            users.extend(__results.get('users', []))
        if not users:
            print('No users in the domain.')
        else:
            with open(wholeList, 'w') as f:
                for user in users:
                    Email =  user['primaryEmail']
                    f.write(Email)
                    f.write('\n')
    except HttpError as err:
        if (err.code): 
            print('the error:  ' + err.resp.reason)
    return __results


##Sign_off function: takes the Service and userList(inlcudeList) input::
def SignOffUser(serv,inputFile):
    __Output = None
    print ("[+] Processing the file /{0}".format(inputFile))
    with open(inputFile, "r") as f:
        line = f.readline()
        num = 1
        while line:
            if (num % 20)==0:
                sys.stderr.write(str(num)+"\n")
                sys.stderr.flush()
            else:
                sys.stderr.write("")
                sys.stderr.flush()
            UserSelected = line.strip()
            debugPrint('[DEBUG] Now signing off the user : ' + UserSelected )
            try:
                # __Logoff = serv.users().get(userKey=UserSelected, projection="full", customFieldMask=None, viewType=None).execute()
                __Logoff = serv.users().signOut(userKey=UserSelected, x__xgafv=None).execute()
                # print (__Logoff)
                print ("[+]Success:: User - " + UserSelected + " has been signed out of google " )
                print('--------------------------')
            except HttpError as err:
                if (err.code): 
                    print('the error:  ' + err.resp.reason)
            # print(__Logoff)
            line = f.readline()
            num = num + 1 
        print('========================================================================================')
    f.close()
    return UserSelected

## Main Function::
def main():
    service = getService()
    if not path.exists(ignrList) or not path.isfile(ignrList):
        print ("[-] {0} is not exists or not a file ".format(ignrList) + "\nprocessing all users")
        sys.exit(1) 

    ## Call listUsers:    
    # results = listUsers(service)

    ## Remove all users mentioned in the excludeList from forcedSignOff
    ## 1- Compare all users with exlude users list and remove them from selected users
    with open(wholeList, 'r') as googleUsers:
        with open(ignrList, 'r') as ignoreList:
            diff = set(googleUsers).difference(ignoreList)
            # debugPrint("ignored Users are: {} ".format(diff))
    diff.discard('\n')

     ## 2- Check if there is an includeList users, if yes, process only it, else add the users to inludeList from step-1
    if os.stat(inclList).st_size == 0:
        print("No Inlcude List found, adding defaults users to include list: \n ")
        with open(inclList, 'w') as file_out:
            for line in diff:
                debugPrint("No Inlcude List found, adding user  to include list: {} \n ".format(line))
                file_out.write(line) 
            file_out.close()
    else:
        print("Performing signOff for the list of users found in includeList \n ")
            # pass


    ## Call SignOff:
    SignOff = SignOffUser(service,inclList)
    # open(inclList, "w").close()


## Call Main::
if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    main()