import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_blogger_service():
    """Shows basic usage of the Blogger API.
    Prints the names and URLs of the user's blogs.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                os.remove('token.json')
                return get_blogger_service()
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('blogger', 'v3', credentials=creds)
    return service

def get_blog_id(service, url="https://atul-lab.blogspot.com/"):
    """Fetches the Blog ID given the Blog URL."""
    try:
        response = service.blogs().getByUrl(url=url).execute()
        return response.get('id')
    except Exception as e:
        raise Exception(f"Could not find blog ID for {url}. Error: {str(e)}")

def publish_post(title: str, content_html: str, labels: list, is_draft: bool = False):
    """
    Publishes a post to Blogger.
    """
    service = get_blogger_service()
    blog_id = get_blog_id(service)
    
    body = {
        "title": title,
        "content": content_html,
        "labels": labels
    }
    
    try:
        request = service.posts().insert(blogId=blog_id, body=body, isDraft=is_draft)
        response = request.execute()
        return response
    except Exception as e:
        raise Exception(f"Failed to publish post: {str(e)}")
