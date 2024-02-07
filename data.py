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

# API Interaction
# def get_data(api_key, sport, data_type, name):
#     sport_endpoints = {
#         'MLB': 'mlb/scores/json',
#         #players by team endpoint: https://api.sportsdata.io/v3/mlb/scores/json/Players/%7Bteam%7D?key=4062184fd0e7475cb86d2832e63064c5
#         #Teams (all) endpoint: https://api.sportsdata.io/v3/mlb/scores/json/AllTeams?key=4062184fd0e7475cb86d2832e63064c5
#         'Soccer': 'soccer/scores/json',
#         #players by team endpoint: https://api.sportsdata.io/v4/soccer/scores/json/PlayersByTeamBasic/%7Bcompetition%7D/%7Bteamid%7D?key=598b84cd809749a586e7a480ca1eaa04
#         #teams endpoint: https://api.sportsdata.io/v4/soccer/scores/json/Teams/%7Bcompetition%7D?key=598b84cd809749a586e7a480ca1eaa04
#         'NFL': 'nfl/scores/json',
#         #players by team endpoint: https://api.sportsdata.io/v3/nfl/scores/json/PlayersBasic/%7Bteam%7D?key=a268f97f6a4d4c8ba60c26eb9b725464
#         #teams endpoint: https://api.sportsdata.io/v3/nfl/scores/json/AllTeams?key=a268f97f6a4d4c8ba60c26eb9b725464
#         'NBA': 'nba/scores/json',
#         #players by team endpoint: https://api.sportsdata.io/v3/nba/scores/json/Players/%7Bteam%7D?key=04f5903db2524c31a41890c2b17cff75
#         #teams endpoint: https://api.sportsdata.io/v3/nba/scores/json/AllTeams?key=04f5903db2524c31a41890c2b17cff75
#         'College Basketball': 'college-basketball/scores/json'
#         #players by team endpoint: https://api.sportsdata.io/v3/cbb/scores/json/PlayersBasic/%7Bteam%7D?key=7454dddc0831496d90a59b35a9aa4c54
#         #teams endpoint: https://api.sportsdata.io/v3/cbb/scores/json/TeamsBasic?key=7454dddc0831496d90a59b35a9aa4c54
#     }

#     base_url = f"https://api.sportsdata.io/v3/{sport_endpoints[sport]}/{data_type}/{name}"
#     headers = {
#         "Ocp-Apim-Subscription-Key": api_key
#     }
#     response = requests.get(base_url, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error fetching data: {response.status_code}")
#         return None
def get_data(api_key, sport, data_type, identifier):
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    url = ""
    if data_type == 'Team':
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/AllTeams"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/Teams/{identifier}"  # Replace {identifier} with competition ID
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/AllTeams"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/AllTeams"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/TeamsBasic"
        # Add more sports and their corresponding team endpoints as needed

    elif data_type == 'Player':
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/Players/{identifier}"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/PlayersByTeamBasic/{identifier}"  # Replace {identifier} with team ID
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/PlayersBasic/{identifier}"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/Players/{identifier}"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/PlayersBasic/{identifier}"
        # Add more sports and their corresponding player endpoints as needed

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None


# User Input for API Data
# def user_input():
#     sports_completer = WordCompleter(['MLB', 'Soccer', 'NFL', 'NBA', 'College Basketball'], ignore_case=True)
#     data_type_completer = WordCompleter(['Team', 'Player'], ignore_case=True)

#     print("Select the sport:")
#     sport = prompt('Sport: ', completer=sports_completer)
#     print("Enter the type of data you want:")
#     data_type = prompt('Data Type: ', completer=data_type_completer)
#     name = input(f"Enter the specific {data_type} name: ")
#     return sport, data_type, name

# Fetch Options for User Input
def fetch_options(api_key, sport, data_type):
    base_url = "https://api.sportsdata.io/v3/"
    headers = {"Ocp-Apim-Subscription-Key": api_key}

    url = ""
    if data_type == 'Team':
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/AllTeams"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/Teams"  # Replace {identifier} with competition ID
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/AllTeams"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/AllTeams"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/TeamsBasic"
        # Add more sports and their corresponding team endpoints as needed

    elif data_type == 'Player':
        if sport == 'MLB':
            url = f"{base_url}mlb/scores/json/AllPlayers"
        elif sport == 'Soccer':
            url = f"{base_url}soccer/scores/json/Players"  # Replace {identifier} with team ID
        elif sport == 'NFL':
            url = f"{base_url}nfl/scores/json/AllPlayers"
        elif sport == 'NBA':
            url = f"{base_url}nba/scores/json/AllPlayers"
        elif sport == 'College Basketball':
            url = f"{base_url}cbb/scores/json/PlayersBasic"
        # Add more sports and their corresponding player endpoints as needed

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data_type == 'Team':
            return [team['Name'] for team in data]
        elif data_type == 'Player':
            return [player['Name'] for player in data]
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def user_input(api_key):
    sports_completer = WordCompleter(['MLB', 'Soccer', 'NFL', 'NBA', 'College Basketball'], ignore_case=True)
    data_type_completer = WordCompleter(['Team', 'Player'], ignore_case=True)

    sport = prompt('Select the sport: ', completer=sports_completer)
    data_type = prompt('Enter the type of data you want: ', completer=data_type_completer)
    options = fetch_options(api_key, sport, data_type)
    option_completer = WordCompleter(options, ignore_case=True)
    name = prompt(f"Select the specific {data_type}: ", completer=option_completer)

    return sport, data_type, name

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
    soccer_api_key = os.getenv('SOCCER_API_KEY')
    nfl_api_key = os.getenv('NFL_API_KEY')
    nba_api_key = os.getenv('NBA_API_KEY')
    mlb_api_key = os.getenv('MLB_API_KEY')
    cbb_api_key = os.getenv('CBB_API_KEY')

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
    sport, data_type, name = user_input()
    data = get_data(api_key, sport, data_type, name)

    if data:
        collection = db[sport]
        collection.insert_many(data)  # Assuming data is a list of dictionaries
        print("Data inserted successfully.")
    else:
        print("No data to insert.")

    # Example of Data Aggregation
    # Modify this based on your specific needs and data structure
    aggregation_pipeline = [
        {"$match": {"sport": sport}},
        {"$group": {"_id": "$teamName", "totalScore": {"$sum": "$score"}}}
    ]
    aggregated_data = collection.aggregate(aggregation_pipeline)
    print(list(aggregated_data))

    # Sort the aggregated data using Quick Sort
    sorted_data = quick_sort(aggregated_data)
    print(sorted_data)

if __name__ == '__main__':
    main()
