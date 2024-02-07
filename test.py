import requests
import pymongo
from pymongo.errors import ConnectionFailure
import bcrypt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from dotenv import load_dotenv
import os


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



def fetch_options(api_key, sport, data_type, identifier=None):
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    url = ""
    if data_type == 'Team':
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/AllTeams"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/Teams"  # Add necessary parameter if required
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/AllTeams"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/AllTeams"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/TeamsBasic"
        # Add conditions for other sports if necessary

    elif data_type == 'Player' and identifier:
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/Players/{identifier}"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/PlayersByTeamBasic/{identifier}"
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/PlayersBasic/{identifier}"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/Players/{identifier}"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/PlayersBasic/{identifier}"
        # Add conditions for other sports with proper identifier

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [item['Name'] for item in data]
    else:
        print(f"Error fetching data: {response.status_code}")
        return []


def display_team_stats(api_key, sport, team_name):
    # Assuming you have an API endpoint that gives you team stats based on the team name or ID
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    team_stats_url = f"{base_url}{sport.lower()}/scores/json/TeamStats/{team_name}"  # Modify URL as per your API

    response = requests.get(team_stats_url, headers=headers)
    if response.status_code == 200:
        team_stats = response.json()
        # Process and display team stats
        print(f"Stats for {team_name}: {team_stats}")  # Modify as per the actual data structure
    else:
        print(f"Error fetching team stats: {response.status_code}")

def display_player_stats(api_key, sport, player_name):
    # Assuming you have an API endpoint that gives you player stats based on the player name or ID
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    player_stats_url = f"{base_url}{sport.lower()}/scores/json/PlayerStats/{player_name}"  # Modify URL as per your API

    response = requests.get(player_stats_url, headers=headers)
    if response.status_code == 200:
        player_stats = response.json()
        # Process and display player stats
        print(f"Stats for {player_name}: {player_stats}")  # Modify as per the actual data structure
    else:
        print(f"Error fetching player stats: {response.status_code}")



def user_input(api_key, sport):
    # Choose Team
    team_options = fetch_options(api_key, sport, 'Team')
    team_completer = WordCompleter(team_options, ignore_case=True)
    team_name = prompt("Select the Team: ", completer=team_completer)

    # Choose between showing team stats or players
    post_team_selection_completer = WordCompleter(['Show Team Stats', 'Show Players'], ignore_case=True)
    post_team_selection = prompt("Choose an option: ", completer=post_team_selection_completer)

    if post_team_selection == 'Show Team Stats':
        # Logic to fetch and display team stats
        display_team_stats(api_key, sport, team_name)
    elif post_team_selection == 'Show Players':
        # Fetch and show players
        player_options = fetch_options(api_key, sport, 'Player', team_name)
        player_completer = WordCompleter(player_options, ignore_case=True)
        player_name = prompt("Select the Player: ", completer=player_completer)

        # Logic to fetch and display player stats
        display_player_stats(api_key, sport, player_name)

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

# Main Function
def main():
    load_dotenv()
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
    api_key = api_keys.get(sport, "default_api_key_if_not_found")  # Handle the case where the API key is not found
    data_type, name = user_input(api_key, sport)
    
    team_name, post_team_selection = user_input(api_key, sport)
    # Fetch data from API
    data = get_data(api_key, sport, data_type, name)

    if data:
        collection = db[sport]
        # Check if data is a list of dictionaries before inserting
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            collection.insert_many(data)
            print("Data inserted successfully.")
        else:
            print("Data format is not as expected.")
    else:
        print("No data to insert.")

    # Example of Data Aggregation
    aggregation_pipeline = [
        {"$match": {"sport": sport}},
        {"$group": {"_id": "$teamName", "totalScore": {"$sum": "$score"}}}
    ]
    aggregated_data = collection.aggregate(aggregation_pipeline)
    print(list(aggregated_data))

    # Sort the aggregated data using Quick Sort
    sorted_data = quick_sort(list(aggregated_data))  # Make sure to convert cursor to list
    print(sorted_data)

if __name__ == '__main__':
    main()