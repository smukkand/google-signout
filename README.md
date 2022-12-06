# Google SignOut Script
`An automation script that wil signoff the users based on filters, the logic follows as below:` \n 
    `1- Script will fetch and store all users from gsuite to file "usersList/allGoogleUsers.txt" ` \n 
    `2- Check if there are users mentioned in excludeList.txt, if yes, remove those and add the all other users to inludeList.txt` \n 
    `3- Check if there are users in includeList.txt, if yes - process only it, else add the all users to inludeList from step-1` \n 


# Requirements
# Install the Google client library
  pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
  pip3 install pandas

# Administrative Access to Google workspace
To use this script, you need to have a proper role assigned to your GSuite account. Most of the scopes require GSuite Administrator role.

You also need a file named **credential.json**. Please contact your GSuite Administrator to have it downloaded it for you. 
The file needs to download from GCP project as a OAuth credentail for desktop applications, The Oauth credentail also must have proper scopes assigned on google workspace.

