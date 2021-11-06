import os
import discord
import json
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.typing = False
intents.presences = False

load_dotenv()
client = discord.Client()

BASED_EMOJI = '\U0001f60e'
CRINGE_EMOJI = '\U0001f62c'



def flush():
    with open("data.json", "w") as write_file:
        json.dump(d, write_file)

def load():
    if(os.path.exists("data.json")):
        with open("data.json", "r") as read_file:
            return json.load(read_file)
    else:
        f = open("data.json", "x")
        f.close()
        return None

#Takes User as a discord User object
def shitlist(user, isBased):
    key = user.mention
    if (not key.startswith('<@!')):
        key = key[:2] + '!' + key[2:]
    if(not key in d):
        d[key] = [1,0,user.name] if isBased else [0,1,user.name]
    else:
        d[key] = [d[key][0] + 1, d[key][1], user.name] if isBased else [d[key][0], d[key][1] + 1, user.name]
    flush()

#Takes uid as mention id
def getScore(uid):
    if(uid not in d):
        return [-1,-1,-1,-1] #Failure Code
    basedNum = d[uid][0]
    cringeNum = d[uid][1]
    username = d[uid][2]
    score = basedNum - cringeNum
    return [score, basedNum, cringeNum, username]

#takes user as a mention id
def printBased(uid):
    score = getScore(uid)
    if(score == [-1,-1,-1,-1]):
        return 'The user in question does not currently have a social credit score.'
    return ('The user {0} has a social credit score of {1}, with a number of based votes totaling {2} and a number of cringe votes totaling {3}!').format(score[3], score[0], score[1], score[2])

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    
@client.event
async def on_reaction_add(reaction, user):
    if(user.mention != reaction.message.author.mention):
        if str(reaction.emoji) == BASED_EMOJI:
            #print("based")
            #print(d)
            shitlist(reaction.message.author, True)
        elif str(reaction.emoji) == CRINGE_EMOJI:
            #print("cring")
            shitlist(reaction.message.author, False)


@client.event
async def on_message(message):
    if message.content.startswith('$based'):
        msgCont = message.content.split()
        #print(msgCont)
        if(msgCont[1].startswith('<@')):
            await message.channel.send(printBased(msgCont[1]))
    if message.content.startswith('$balls'):
        await message.channel.send('Hello!')
        #print(message.content)
        #print(message.author.name)
        #print(message.author.id)
        #print(message.author.mention)


d = load()

client.run(os.getenv('TOKEN'))