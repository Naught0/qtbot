import json
from pathlib import Path
from nltk.metrics import edit_distance as ed


class LeagueUtils():
    def foundChampFile():
        """ Checks for valid league file and returns T/F """
        try:
            with open("data/champ_data.json", "r") as f:
                _ = json.load(f)
        except:
            return False

        return True

    def getChampID(champ) -> dict:
        with open("data/champ_data.json", "r") as f:
            champ_dict = json.load(f)            
        if champ in champ_dict["data"]:
            return champ_dict["data"][champ]["id"]
        else:
            corrected_champ = DictManip.getClosest(champ_dict["data"], champ)
            print("Corrected champ: {}".format(corrected_champ))
            return {"original" : champ, "corrected" : champ_dict["data"][corrected_champ]["id"]}

    def getSummonerID(summoner_name):

class UserFileManip():
    def foundUserFile():
        """ Checks for user file and returns T/F """
        return Path("data/user_data.json").is_file()

    def getUserInfo(member, key):
        """ Finds user and prints value of key """
        with open("data/user_data.json", "r") as user_file:
            user_data = json.load(user_file)

        if (member in user_data) and (key in user_data[member]):
            return user_data[member][key]
        else:
            raise KeyError("User not found.")

    def updateUserInfo(member, key, info):  
        # Open file
        with open("data/user_data.json", "r") as f:
            user_data = json.load(f)
        
        # If found user, update
        if member in user_data: 
            user_data[member][key] = info
            
            with open("data/user_data.json", "w") as user_file:
                json.dump(user_data, user_file)
            
            user_file.close()
        
        # Create user if not found
        else:
            with open("data/user_data.json", "r") as user_file:
                    user_data = json.load(user_file)
            
            user_file = open("data/user_data.json", "r+")

            user_data[member] = {
                key : info
            }

            json.dump(user_data, user_file)

            user_file.close()

    # Creates user file based on input
    def createUserFile(member, key, info):
        new_user = {
            member : 
                {
                    key : info
                }
            }
        f = open("data/user_data.json", "w+")
        json.dump(new_user, f)
        f.close()
        return

class DictManip():
    def getClosest(word_dict, word):
        """ returns the key which matches most closely to 'word' """
        # stores keys and their edit distance values
        distance_dict = {}

        for key in word_dict:
            distance_dict[key] = ed(key, word)

        # return key w/ least edits
        return min(distance_dict, key=distance_dict.get)

    def keywithmaxval(d):
        """ 
        a) create a list of the dict's keys and values; 
        b) return the key with the max value
        Shamelessly taken from:
        http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        """ 
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(max(v))]   

    def keywithminval(d):
        """ 
        a) create a list of the dict's keys and values; 
        b) return the key with the max value
        Shamelessly taken from:
        http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
        """ 
        v = list(d.values())
        k = list(d.keys())
        return k[v.index(min(v))]