import os
import discord
import json
import re
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.typing = False
intents.presences = False

load_dotenv()
client = discord.Client()


#Both of these can be changed to your liking. For reference, \U0001f60e is the :sunglasses: emote, and \U0001f62c is the :grimacing: emote.
BASED_EMOJI = '\U0001f60e'
CRINGE_EMOJI = '\U0001f62c'


#Write the shitlist to the data.json file
def flush():
    with open("data.json", "w") as write_file:
        json.dump(d, write_file)

#Load the shitlist from the data.json file. If a file doesn't exist, this means no shitlist, so one must be created.
def load():
    if(os.path.exists("data.json")):
        with open("data.json", "r") as read_file:
            return json.load(read_file)
    else:
        f = open("data.json", "x")
        f.close()
        return {}

#Takes User as a discord User object
def shitlist(user, isBased):
    key = user.id

    #If user doesn't have a score yet, their vote count is exactly 1,0 or 0,1 depending on the vote being processed.
    if(not key in d):
        d[key] = [1,0,user.name] if isBased else [0,1,user.name]

    #Otherwise, add one to the correct vote count. The ternary statement is kind of bulky here, but I felt it was less clunky than doing a full if else.
    else:
        d[key] = [d[key][0] + 1, d[key][1], user.name] if isBased else [d[key][0], d[key][1] + 1, user.name]

    #Oh boy, this is a doozy right here. The idea is that dictionaries retain insertion order. So, when this line is ran,
    #we copy the shitlist (d) into a dictionary which is sorted by social credit score. I'll parse this line to make it easier to understand.
    #The curly bracket notation makes a dictionary, and populates it with the values for 'uid' and 'entry', which are the returns of a for each loop.
    #Said foreach loop iterates over every index of dict.items(), which returns a list of the dictionary entries as a (key, value) tuple.
    #This dict.items() list is sorted by python's built in sorted() function, which takes the list to be ordered, a key to sort by (in this case, social credit,
    #which is found by taking the first index of the value side of the items() tuple -- item[1][0] -- and subtracting the second index -- item[1][1] from it.
    #Finally, the list is ordered in reverse (or descending) order. Then, we set d to the copy we made. Dear lord.
    d = {uid: entry for uid, entry in sorted(d.items(), key = lambda item: item[1][0] - item[1][1], reverse = True)}
    
    #Flush the buffer to write the changes to the JSON, so no votes are lost if the program unexpectedly quits.
    flush()

#Takes uid as mention id
def getScore(uid):
    if(uid not in d):
        return [-1,-1,-1,-1] #Failure Code, returned so the bot can say the user's score doesn't exist.
    basedNum = d[uid][0]
    cringeNum = d[uid][1]
    username = d[uid][2]
    score = basedNum - cringeNum
    return [score, basedNum, cringeNum, username]

#Takes user id, returns the formatted string to be posted, containing a specific user's name, score, and both vote numbers
def printBased(uid):
    score = getScore(uid)
    
    #This only happens if the user doesn't have a score.
    if(score == [-1,-1,-1,-1]):
        return 'The user in question does not currently have a social credit score.'

    return ('The user {0} has a social credit score of {1}, with a number of based votes totaling {2} and a number of cringe votes totaling {3}!').format(score[3], score[0], score[1], score[2])

#Returns a formatted string to be posted as a list of the 3 users with the highest social credit.
def printTop():
    #Start building the message body
    msg = "The 3 users with the highest social credit score are: \n\n"
    #Temporary dict, so as not to run d.items() 12 times
    temp = d.items()
    msg += ("1: {0} with a social credit score of {1}, based votes totaling {2}, and cringe votes totaling {3}. \n").format(temp[0][2], temp[0][0]-temp[0][1], temp[0][0], temp[0][1])
    msg += ("2: {0} with a social credit score of {1}, based votes totaling {2}, and cringe votes totaling {3}. \n").format(temp[0][2], temp[0][0]-temp[0][1], temp[0][0], temp[0][1])
    msg += ("3: {0} with a social credit score of {1}, based votes totaling {2}, and cringe votes totaling {3}.").format(temp[1][2], temp[1][0]-temp[1][1], temp[1][0], temp[1][1])
    return msg

#Returns a string to be posted, detailing the ranking of a specific user.
def printRank(uid):
    i = 1 #Keeps track of a user's index within the dictionary, and thus their ranking
    msg = "" #Start building the message body.
    for entry in d.items():
        #If user ID matches, we found them
        if(entry[0] == uid):
            msg += ("{0} is currently ranked #{1} in this server, with a social credit score of {2}.").format(entry[1][2], i, entry[1][0] - entry[1][1])
            break #Breaking is gross, but done here so the rest of the dictionary is not iterated over.
        #If not a match, increment the index and try again.
        else:
            i += 1
    #msg being empty means the for loop didn't find a match, meaning the user doesn't have a score.
    if(msg == ""):
        msg += "The user in question currently does not have a social credit score on this server, and as such is not ranked."
    return msg

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    
@client.event
async def on_reaction_add(reaction, user):
    if(user.mention != reaction.message.author.mention):
        if str(reaction.emoji) == BASED_EMOJI:
            shitlist(reaction.message.author, True)
        elif str(reaction.emoji) == CRINGE_EMOJI:
            shitlist(reaction.message.author, False)


@client.event
async def on_message(message):
    #Split command into its arguments
    msgCont = message.content.split()

    #Command to check a user's social credit score
    if(msgCont[0] =='$based'):
        if(len(msgCont) == 1):
            await message.channel.send("This command requires a mention. Tag someone like this: '$based @username'")
        elif(msgCont[1].startswith('<@')):
            msgCont[1] = re.sub("[^0-9]", "", msgCont[1])
            await message.channel.send(printBased(msgCont[1]))
        else:
            await message.channel.send("The given argument was not understood. Tag someone like this: '$based @username'")

    #Command to print the list of the 3 most based people.
    elif(msgCont[0] =='$top'):
        await message.channel.send(printTop())

    #Command to print the rank of a given user
    elif(msgCont[0] =='$rank'):
        if(len(msgCont) == 1):
            await message.channel.send("This command requires a mention. Tag someone like this: '$rank @username'")
        elif(msgCont[1].startswith('<@')):
            msgCont[1] = re.sub("[^0-9]", "", msgCont[1])
            await message.channel.send(printRank(msgCont[1]))
        else:
            await message.channel.send("The given argument was not understood. Tag someone like this: '$rank @username'")
    
    #I have the sense of humor of a 12 year old
    elif(msgCont[0] == "$ligma"):
        await message.channel.send("ligma balls ha lmao gottem")


d = load()

client.run(os.getenv('TOKEN'))