from flask import Flask, render_template, request
import requests
import pandas as pd
import os

app = Flask(
    __name__, 
    template_folder=os.path.join(os.path.dirname(__file__), "../templates")
)

# Fetch team data for a specific gameweek
def fetch_team_data(team_id, gameweek):
    url = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{gameweek}/picks/"
    response = requests.get(url)
    if response.status_code == 200:
        picks = response.json()["picks"]
        return pd.DataFrame(picks)
    else:
        print(f"Error fetching team data: {response.status_code}")
        return None

# Fetch all player data
def fetch_player_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    if response.status_code == 200:
        players = response.json()["elements"]
        return pd.DataFrame(players)
    else:
        print(f"Error fetching player data: {response.status_code}")
        return None

# Fetch fixtures data for upcoming games
def fetch_fixtures():
    url = "https://fantasy.premierleague.com/api/fixtures/"
    response = requests.get(url)
    if response.status_code == 200:
        fixtures = response.json()
        return pd.DataFrame(fixtures)
    else:
        print(f"Error fetching fixture data: {response.status_code}")
        return None

# Check if a player is healthy (not injured or suspended)
def is_player_healthy(player_id, player_data):
    player = player_data[player_data['id'] == player_id]  # Select the player by ID
    if player.empty:
        return False  # If no player found, consider them not healthy
    status = player.iloc[0]['status']  # Get the status of the player
    return status not in ['Injured', 'Suspended']

# Recommend transfers based on team and player data
def recommend_transfers(team_data, player_data, budget_remaining, fixtures):
    # Merge team data with player stats
    team = team_data.merge(player_data[['id', 'first_name', 'second_name', 'form', 'now_cost', 'team']], left_on='element', right_on='id')

    # Convert 'form' to numeric, coercing errors (non-numeric) to NaN
    team['form'] = pd.to_numeric(team['form'], errors='coerce')

    # Fill NaN values in 'form' with 0 (or choose another strategy, e.g., drop NaN)
    team['form'] = team['form'].fillna(0)

    # Ensure player_data 'form' is also numeric
    player_data['form'] = pd.to_numeric(player_data['form'], errors='coerce')

    # Find players with low form (below 2)
    underperforming_players = team[team['form'] < 2]

    recommendations = []
    for _, player in underperforming_players.iterrows():
        # Check if the player is healthy
        if not is_player_healthy(player['id'], player_data):
            continue  # Skip if player is injured or suspended
        
        # Get player's team and next opponent's team
        player_team = player['team']
        next_opponent = fixtures[fixtures['team_a'] == player_team].iloc[0] if fixtures[fixtures['team_a'] == player_team].shape[0] > 0 else None
        if next_opponent is not None:
            opponent_team = next_opponent['team_h']  # Example for home fixture, adjust as necessary
            difficulty = 3 if opponent_team in ['Manchester City', 'Liverpool'] else 1  # Difficulty: 3 = Hard, 1 = Easy
        else:
            continue  # No upcoming fixture found

        # Find potential replacements within budget
        replacements = player_data[
            (player_data['form'] > player['form']) & 
            (player_data['now_cost'] <= player['now_cost'] + budget_remaining * 10)  # Budget check
        ]
        
        # Sort by form and suggest the best replacement
        if not replacements.empty:
            best_replacement = replacements.sort_values('form', ascending=False).iloc[0]
            recommendations.append({
                "player_out": f"{player['first_name']} {player['second_name']}",
                "player_in": f"{best_replacement['first_name']} {best_replacement['second_name']}",
                "form_in": best_replacement["form"],
                "cost_in": best_replacement["now_cost"] / 10,  # Cost is stored as x10 in API
                "difficulty": difficulty
            })

    return recommendations

# Flask route to display the form and results
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team_id = int(request.form["team_id"])
        gameweek = int(request.form["gameweek"])
        budget_remaining = float(request.form["budget_remaining"])

        # Fetch team, player, and fixture data
        team_data = fetch_team_data(team_id, gameweek)
        player_data = fetch_player_data()
        fixtures = fetch_fixtures()

        if team_data is not None and player_data is not None and fixtures is not None:
            # Recommend transfers
            transfers = recommend_transfers(team_data, player_data, budget_remaining, fixtures)
            return render_template("index.html", transfers=transfers)
        else:
            return render_template("index.html", error="Error fetching data")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
