# imports 
import requests
import pymongo
from pymongo.errors import ConnectionFailure
import bcrypt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from dotenv import load_dotenv
import os
from mlb import mlb_teams as mlb_teams
from mlb import mlb_seasons as mlb_seasons

# load env
load_dotenv()

# user registration 
def register_user(db):
    username = input("Enter username: ")
    password = input("Enter password: ")

    # check to see it the username already exists
    if db.Accounts.find_one({"username": username}):
        print("User already exists")
        return
    
    # hash the password and store it 
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db.Accounts.insert_one({"username": username, "password": hashed})

# user login 
def login_user(db):
    username = input("Enter username: ")
    password = input("Enter password: ")

    # check to see if the user exists
    user = db.Accounts.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print("Login successful")
    else:
        print("Login failed")
        return False

# fetch options for the mlb 
def fetch_options(api_key, data_type, identifier=None):
    base_url = "https://api.sportsdata.io/v3/"
    team_abbr = mlb_teams.get_team_abbr()
    url = ""

    if data_type == "teams":
        url = f"{base_url}mlb/scores/json/Teams"
    if data_type == "players":
        url = f"{base_url}mlb/scores/json/Players"

# display team stats
    

# display player stats 
    
# user input 

# quicksort 

# main function 
    # api keys 
    # connect to db 
    # get data after user input