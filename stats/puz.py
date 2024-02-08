import requests
import pymongo
from pymongo.errors import ConnectionFailure
import bcrypt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from dotenv import load_dotenv
import os
from team_mappings import team_mappings
from player_mappings import player_mappings
from season_stats import mlb_stats
from season_stats import nfl_stats
from season_stats import nba_stats
from teamMaps import cbb_mappings
from teamMaps import mlb_mappings
from teamMaps import nba_mappings
from teamMaps import nfl_mappings



#load environment variables
load_dotenv()

# User Registration
def register_user(db):
    username = input("Enter a new username: ")
    password = input("Enter a new password: ")

    # Check if the username already exists
    if db.Accounts.find_one({"username": username}):
        print("Username already exists. Please choose a different username.")
        return

    # Hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store the new user
    db.Accounts.insert_one({"username": username, "password": hashed})
    print("User registered successfully.")

# User Login
def login_user(db):
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Find the user in the database
    user = db.Accounts.find_one({"username": username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        print("Login successful.")
        return True
    else:
        print("Invalid username or password.")
        return False

# User Input for API Data
def get_sport():
    sports_completer = WordCompleter(['MLB', 'Soccer', 'NFL', 'NBA', 'College Basketball'], ignore_case=True)
    return prompt('Select the sport: ', completer=sports_completer)

# Fetch Options for User Input
def fetch_options(api_key, sport, data_type, identifier=None):
    base_url = "https://api.sportsdata.io/v3/"
    soccer_url ="https://api.sportsdata.io/v4"
    team_abbr = team_mappings[sport].get(identifier, "Unknown") if identifier else None

    url = ""
    if data_type == 'Team':
        # Use team abbreviation for team data endpoint
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/AllTeams?key={api_key}"
        elif sport == 'Soccer':
            # Soccer API might need a different approach for team ID
            url = f"{base_url}soccer/scores/json/Teams?key={api_key}"
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/AllTeams?key={api_key}"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/AllTeams?key={api_key}"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/TeamsBasic?key={api_key}"

    elif data_type == 'Player':
        # Directly use identifier for player data endpoint
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/PlayersBasic/{mlb_mappings}?key={api_key}"
        elif sport == 'Soccer':
            url = f"{soccer_url}soccer/scores/json/PlayersByTeam/{team_abbr}?key={api_key}"
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/PlayersBasic/{nfl_mappings}?key={api_key}"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/Players/{nba_mappings}?key={api_key}"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/PlayersBasic/{cbb_mappings}?key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        return [item['Name'] for item in response.json()]
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def display_team_stats(api_key, sport, team_abbr):
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    
    if sport == 'MLB':
        team_stats_url = f"{base_url}mlb/scores/json/TeamSeasonStats/{mlb_stats}?key={api_key}"
    elif sport == 'NFL':
        team_stats_url = f"{base_url}nfl/scores/json/TeamSeasonStats/{nfl_stats}?key={api_key}"
    elif sport == 'NBA':
        team_stats_url = f"{base_url}nba/scores/json/TeamSeasonStats/{nba_stats}?key={api_key}"
    elif sport == 'College Basketball':
        team_stats_url = f"{base_url}cbb/scores/json/TeamSeasonStats/{team_abbr}?key={api_key}"
    # Add conditions for other sports if necessary
    
    response = requests.get(team_stats_url, headers=headers)
    print("Response:", response.status_code, response.json())

    if response.status_code == 200:
        team_stats = response.json()
        # Process and display team stats
        print(f"Stats for {team_abbr}: {team_stats}")  # Modify as per the actual data structure
    else:
        print(f"Error fetching team stats: {response.status_code}")

def display_player_stats(api_key, sport, player_abbr):
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    player_stats_url = f"{base_url}{sport.lower()}/scores/json/PlayerStats/{player_abbr}"
    print("Requesting URL:", player_stats_url)  # Debug print
    response = requests.get(player_stats_url, headers=headers)
    print("Response:", response.status_code, response.json())

    if response.status_code == 200:
        player_stats = response.json()
        # Process and display player stats
        print(f"Stats for {player_abbr}: {player_stats}")  # Modify as per the actual data structure
    else:
        print(f"Error fetching player stats: {response.status_code}")

# User Input Function
# def user_input(api_key, sport):
#     # Fetch and display team options
#     team_options = fetch_options(api_key, sport, 'Team')
#     team_completer = WordCompleter(team_options, ignore_case=True)
#     team_name = prompt("Select the Team: ", completer=team_completer)
#     team_abbr = team_mappings[sport].get(team_name, "Unknown")

#     # Choose between showing team stats or players
#     post_team_selection_completer = WordCompleter(['Show Team Stats', 'Show Players'], ignore_case=True)
#     post_team_selection = prompt("Choose an option: ", completer=post_team_selection_completer)

#     if post_team_selection == 'Show Team Stats':
#         display_team_stats(api_key, sport, team_abbr)
#     elif post_team_selection == 'Show Players':
#         player_options = fetch_options(api_key, sport, 'Player', team_abbr)
#         player_completer = WordCompleter(player_options, ignore_case=True)
#         player_name = prompt("Select the Player: ", completer=player_completer)
#         player_abbr = player_mappings[sport].get(player_name, "Unknown")
#         display_player_stats(api_key, sport, player_abbr)

#     return team_name, post_team_selection
        

# Debugging variation of the function 
def user_input(api_key, sport):
    # Fetch and display team options
    team_options = fetch_options(api_key, sport, 'Team')
    print("Team Options:", team_options)  # Debug print
    team_completer = WordCompleter(team_options, ignore_case=True)
    team_name = prompt("Select the Team: ", completer=team_completer)
    team_abbr = team_mappings[sport].get(team_name, "Unknown")
    print("Selected Team Abbreviation:", team_abbr)  # Debug print

    # Choose between showing team stats or players
    post_team_selection_completer = WordCompleter(['Show Team Stats', 'Show Players'], ignore_case=True)
    post_team_selection = prompt("Choose an option: ", completer=post_team_selection_completer)

    if post_team_selection == 'Show Team Stats':
        display_team_stats(api_key, sport, team_abbr)
    elif post_team_selection == 'Show Players':
        player_options = fetch_options(api_key, sport, 'Player', team_abbr)
        print("Player Options:", player_options)  # Debug print
        if player_options:
            player_completer = WordCompleter(player_options, ignore_case=True)
            player_name = prompt("Select the Player: ", completer=player_completer)
            player_abbr = player_mappings[sport].get(player_name, "Unknown")
            display_player_stats(api_key, sport, player_abbr)
        else:
            print("No players found for the selected team.")

    return team_name, post_team_selection



#Quick Sort Algorithm
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]['totalScore']
    left = [x for x in arr if x['totalScore'] < pivot]
    middle = [x for x in arr if x['totalScore'] == pivot]
    right = [x for x in arr if x['totalScore'] > pivot]
    return quick_sort(left) + middle + quick_sort(right)


#main
def main():
    
    api_keys = {
        'Soccer': os.getenv('SOCCER_API_KEY'),
        'NFL': os.getenv('NFL_API_KEY'),
        'NBA': os.getenv('NBA_API_KEY'),
        'MLB': os.getenv('MLB_API_KEY'),
        'College Basketball': os.getenv('CBB_API_KEY')
    }

    try:
        # Attempt to connect to MongoDB
        print("Attempting to connect to MongoDB...")
        db_client = pymongo.MongoClient("mongodb://root:6376@10.0.1.172:27017/")
        db = db_client["SportsData"]
        print("Connected to MongoDB database:", db.name)

        while True:
            print("1: Register\n2: Login\n3: Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                register_user(db)
            elif choice == '2':
                if login_user(db):
                    break  # Exit the loop if login is successful
            elif choice == '3':
                print("Exiting the program.")
                return
            else:
                print("Invalid choice. Please try again.")
    except ConnectionFailure:
        print("Failed to connect to MongoDB. Please check the connection settings.")
        return

   # After successful login
    sport = get_sport()
    api_key = api_keys.get(sport, "default_api_key_if_not_found")
    team_name, post_team_selection = user_input(api_key, sport)

    # If you have additional logic or functionality you want to implement after this, you can add it here

    # Example of Data Aggregation (modify as needed)
    # aggregation_pipeline = [
    #     {"$match": {"sport": sport}},
    #     {"$group": {"_id": "$teamName", "totalScore": {"$sum": "$score"}}}
    # ]
    # aggregated_data = db[sport].aggregate(aggregation_pipeline)
    # print(list(aggregated_data))

    # Sorting the aggregated data using Quick Sort
    # sorted_data = quick_sort(list(aggregated_data))
    # print(sorted_data)

if __name__ == '__main__':
    main()
