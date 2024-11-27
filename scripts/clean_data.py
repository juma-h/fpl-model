import pandas as pd

# Load player data
players = pd.read_csv("data/players.csv")

# Select key columns
key_columns = [
    "first_name", "second_name", "now_cost", "total_points", "form",
    "minutes", "team", "element_type"
]
players = players[key_columns]

# Convert cost to millions
players["now_cost"] = players["now_cost"] / 10

# Filter active players
players = players[players["minutes"] > 0]

# Save cleaned data
players.to_csv("data/cleaned_players.csv", index=False)
print("Cleaned data saved.")
