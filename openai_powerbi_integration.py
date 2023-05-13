import os
from app_config import app, SCOPE
import openai
import pandas as pd
from powerbiclient import Report, models
import requests
from msal import PublicClientApplication

result = None
accounts = app.get_accounts()

if accounts:
    result = app.acquire_token_silent(SCOPE, account=accounts[0])

if not result:
    flow = app.initiate_device_flow(scopes=SCOPE)
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    
powerbi_auth_token = result["access_token"]

def fetch_openai_data(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    generated_text = response.choices[0].text.strip()
    return generated_text

def push_data_to_powerbi(api_url, auth_token, dataframe):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    data_json = dataframe.to_json(orient="records")
    response = requests.post(api_url, headers=headers, data=data_json)
    return response.status_code

# Define your OpenAI prompt
prompt = "Summarize the key factors affecting the global economy in 2023."

# Fetch data from OpenAI
openai_data = fetch_openai_data(prompt)

# Create a DataFrame with the data
data = {"OpenAI_Insight": [openai_data]}
dataframe = pd.DataFrame(data)

# Push data to Power BI
api_url = os.getenv("PushURL")
auth_token = powerbi_auth_token
status_code = push_data_to_powerbi(api_url, auth_token, dataframe)

# Print status code for confirmation
print(f"Data push status code: {status_code}")