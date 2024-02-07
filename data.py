import os
import requests
import pymongo
from pymongo.errors import ConnectionFailure
import bcrypt


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
def get_data(api_key, sport, data_type, name):
    sport_endpoints = {
        'MLB': 'mlb/scores/json',
        'Soccer': 'soccer/scores/json',
        'NFL': 'nfl/scores/json',
        'NBA': 'nba/scores/json',
        'College Basketball': 'college-basketball/scores/json'
    }

    base_url = f"https://api.sportsdata.io/v3/{sport_endpoints[sport]}/{data_type}/{name}"
    headers = {
        "Ocp-Apim-Subscription-Key": api_key
    }
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# User Input for API Data
def user_input():
    print("Select the sport (MLB, Soccer, NFL, NBA, College Basketball):")
    sport = input()
    print("Enter the type of data you want (e.g., 'team', 'player'):")
    data_type = input()
    print(f"Enter the specific {data_type} name:")
    name = input()
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
    api_key = "YOUR API KEY"  # replace with your actual API key

    try:
        # Attempt to connect to MongoDB
        print("Attempting to connect to MongoDB...")
        db_client = pymongo.MongoClient("mongodb://root:6376@10.0.1.172:27017/SportsData")
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
