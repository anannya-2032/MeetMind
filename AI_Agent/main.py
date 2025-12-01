#!/usr/bin/env python
# coding: utf-8

# In[38]:


from dotenv import load_dotenv
import os
load_dotenv("api.env")
my_api_key = os.getenv("my_api_key")

if my_api_key is None:
    print("API key not found. Ensure .env file exists and contains MY_API_KEY.")
else:
    # Use your API key in your code
    print(f"API key loaded: {api_key[:5]}...")


# In[43]:


from google.genai import types

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool, FunctionTool

print("✅ ADK components imported successfully.")


# In[46]:


import os
import json
import tempfile
import base64
import re
from typing import Dict, Any, List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# In[12]:


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


# In[13]:


def ensure_creds():
    """Local-machine OAuth flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


# In[14]:


creds=ensure_creds()


# In[15]:


def gmail_send_email(to, subject, body, creds_path="token.json"):
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import base64

    creds = Credentials.from_authorized_user_file(creds_path)
    service = build("gmail", "v1", credentials=creds)

    msg = f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}"
    raw = base64.urlsafe_b64encode(msg.encode()).decode()

    return service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()


# In[16]:


def drive_upload_file(filename, content, creds_path="token.json"):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(creds_path)
    service = build("drive", "v3", credentials=creds)

    media = MediaInMemoryUpload(
        content.encode(), mimetype="text/plain"
    )

    return service.files().create(
        body={"name": filename},
        media_body=media,
        fields="id,webViewLink"
    ).execute()


# In[17]:


def drive_search_file(query, creds_path="token.json"):
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(creds_path)
    service = build("drive", "v3", credentials=creds)

    results = service.files().list(
        q=query,
        fields="files(id,name)"
    ).execute()

    return results.get("files", [])


# In[18]:


def drive_download_file(file_id, creds_path="token.json"):
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(creds_path)
    service = build("drive", "v3", credentials=creds)

    data = service.files().get_media(fileId=file_id).execute()
    return data.decode("utf-8")


# In[19]:


def calendar_add_event(summary, date, creds_path="token.json"):
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(creds_path)
    service = build("calendar", "v3", credentials=creds)

    body = {
        "summary": summary,
        "start": {"date": date},
        "end": {"date": date}
    }

    return service.events().insert(
        calendarId="primary",
        body=body
    ).execute()


# In[20]:


# from google.generativeai import GenerativeModel
# from google.adk import Agent

# llm = GenerativeModel("gemini-2.0-pro")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)


# In[21]:


transcript_fetch_agent = LlmAgent(
    name="transcript_fetch_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Use Drive search to find transcript file of the meeting.

Search rule:
filename contains meeting_id AND ends with .vtt or .txt

IF FOUND:
download the file using drive download tool

IF NOT FOUND:
retry 3 times
then ask user to upload manually

OUTPUT:
{
  "status": "OK",
  "transcript_raw": "..."
}
""",
    tools=[drive_search_file, drive_download_file]
)


# In[22]:


transcript_cleanup_agent = LlmAgent(
    name="transcript_cleanup_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Clean messy transcript:
- Remove timestamps
- Label speakers
- Fix sentence breaks
- Remove repetitions

Return clean text.
"""
)


# In[23]:


mom_generator_agent = LlmAgent(
    name="mom_generator_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Generate a professional MoM:

FORMAT:
1. Meeting Summary
2. Agenda
3. Key Highlights
4. Decisions Taken
5. Discussion Notes
6. Action Items

Handle incomplete or messy transcripts.
"""
)


# In[24]:


action_extractor_agent = LlmAgent(
    name="action_extractor_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Extract actionable tasks as JSON:

[
  {
    "task": "...",
    "owner": "...",
    "due": "YYYY-MM-DD",
    "context": "..."
  }
]

If owner or due date missing → ask orchestrator for clarification.
"""
)


# In[25]:


drive_storage_agent = LlmAgent(
    name="drive_storage_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Store MoM to Drive using the drive_upload tool.

Return:
{
  "mom_file_url": "..."
}
""",
    tools=[drive_upload_file]
)


# In[26]:


email_dispatch_agent = LlmAgent(
    name="email_dispatch_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
Send the MoM link to recipients using gmail_send tool.

If recipient missing or invalid → ask user.
""",
    tools=[gmail_send_email]
)


# In[27]:


calendar_action_agent = LlmAgent(
    name="calendar_action_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
For each action item:
- Create a Calendar task/event
- Use calendar_add_event tool

Handle missing dates, owner emails.
""",
    tools=[calendar_add_event]
)


# In[28]:


orchestrator_agent = LlmAgent(
    name="orchestrator",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
You coordinate the entire MoM generation workflow.

INPUT FORMAT:
{
  "meeting_id": "...",
  "recipients": "a@b.com,b@c.com"
}

PROCESS:
1. Validate meeting_id
2. Call transcript_fetch agent
3. Call transcript_cleanup agent
4. Call mom_generator agent
5. Call action_extractor agent
6. Call drive_storage agent
7. Call email_dispatch agent
8. Call calendar_action agent
9. Return Drive link + status summary

Handle all IF-AND-BUT cases:
- Missing transcript
- Missing owner emails
- Missing due dates
- Conflicting tasks
- Duplicate transcripts
"""

    ,
    sub_agents=[
        transcript_fetch_agent,
        transcript_cleanup_agent,
        mom_generator_agent,
        action_extractor_agent,
        drive_storage_agent,
        email_dispatch_agent,
        calendar_action_agent
    ]
)

runner = InMemoryRunner(agent=orchestrator_agent)
response = await runner.run_debug("Generae MOM for meeting abc-xyz-123")

print(response)