import requests
import pandas as pd
import os

# FPL API endpoint
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

# Fetch data
response = requests.get(FPL_API_URL)
data = response.json()

# Save dataframes to CSV
os.makedirs("data", exist_ok=True)
players = pd.DataFrame(data['elements'])
players.to_csv("data/players.csv", index=False)

teams = pd.DataFrame(data['teams'])
teams.to_csv("data/teams.csv", index=False)

fixtures = pd.DataFrame(data['events'])
fixtures.to_csv("data/fixtures.csv", index=False)

print("Data fetched and saved to 'data/' folder.")
