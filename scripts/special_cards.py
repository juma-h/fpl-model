import pandas as pd

def suggest_special_cards(team_data, player_data, fixtures):
    """
    Suggests whether to use special cards based on team performance and fixtures.
    """
    # Merge team data with player data for analysis
    team = team_data.merge(player_data, left_on="element", right_on="id")
    
    # Identify underperforming or non-playing players
    non_playing = team[team["minutes"] == 0]
    underperformers = team[team["form"] < 2]  # Example threshold for underperforming

    # Fixture difficulty analysis
    next_fixtures = fixtures[fixtures["team"].isin(team["team"])]
    tough_fixtures = next_fixtures[next_fixtures["difficulty"] > 3]  # Difficult fixtures threshold

    # Suggestions logic
    suggestions = []

    # Wildcard
    if len(underperformers) > 4 or len(non_playing) > 3:
        suggestions.append("Consider using your Wildcard: Too many underperforming or non-playing players.")

    # Free Hit
    if len(non_playing) > 5:
        suggestions.append("Consider using your Free Hit: Many players missing for this gameweek.")

    # Bench Boost
    bench_players = team[team["position"].isin(["GKP", "DEF", "MID", "FWD"]) & (team["form"] > 2)]
    if len(bench_players) >= 4 and all(bench_players["minutes"] > 0):
        suggestions.append("Consider using your Bench Boost: Strong bench players available.")

    # Triple Captain
    potential_captains = team[(team["form"] > 6) & (team["minutes"] > 60)]
    if not potential_captains.empty:
        suggestions.append(f"Consider using Triple Captain: {potential_captains.iloc[0]['second_name']} is in great form.")

    if not suggestions:
        suggestions.append("No special card recommendation for this gameweek.")
    
    return suggestions


# Example usage
team_data = pd.DataFrame([...])  # Replace with actual team data from API
player_data = pd.DataFrame([...])  # Replace with player stats
fixtures = pd.DataFrame([...])  # Replace with fixtures data

recommendations = suggest_special_cards(team_data, player_data, fixtures)
print("\n".join(recommendations))
