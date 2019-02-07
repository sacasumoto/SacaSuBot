import discord
import asyncio
import PlayerClass as pc
from PlayerClass import alt_names_dict
import TournamentClass as tc
import scraping_functions as sf
import re
import os
filepath = os.getcwd()

def split_message(string):
    string = string.strip('```')
    lines = string.split('\n')
    final = '```'
    final_list = []
    for line in lines:
        if len(final+line) < 1990:
            final += line +'\n'
            if line == lines[-1]:
                final.strip('\n')
                final += '```'
                final_list.append(final)
        else:
            final.strip('\n')
            final += '```'
            final_list.append(final)
            final = '```'
    return(final_list)

client = discord.Client()
M = tc.MasterTournament([])
M.loadFromFile('LoadIn.txt')


@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
@asyncio.coroutine
def on_message(message):
    if message.content.startswith('!test'):
        counter = 0
        tmp = yield from client.send_message(message.channel, 'Calculating messages...')
        logs = yield from client.logs_from(message.channel, limit=100)
        for log in logs:
            if log.author == message.author:
                counter += 1

        yield from client.edit_message(tmp, 'You have {} messages.'.format(counter))

    elif message.content.startswith('!sleep'):
        yield from asyncio.sleep(5)
        yield from client.send_message(message.channel, 'Done sleeping')

    elif message.content.startswith('!activitytournaments'):
        final = '```'
        for tournament in sorted(M.getActivityTournaments(), reverse=True):
            final += tournament[1]+'\n'
        final.strip('\n')
        final += '```'
        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)

    elif message.content.startswith('!playertournaments'):
        txt = re.sub("!playertournaments ", "", message.content)
        player = sf.normalize_name(txt)
        final = "```All of {}'s tournaments:\n".format(player)
        tournaments = M.getPlayerTournaments(player)
        
        for tournament in tournaments:
            final += tournament+'\n'
        final += '{} has entered {} tournaments\n'.format(player, len(tournaments))
        final.strip('\n')
        final += '```'
        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)


    
    elif message.content.startswith('!h2h'):
        txt = re.sub("(!h2h )", "", message.content)
        txt = txt.split("-")
        player1 = sf.normalize_name(txt[1])
        player2 = sf.normalize_name(txt[2])
        recordDict = M.getPlayerWinsLossDict(player1)
        if player2 in recordDict:      
            record = recordDict[player2]
            final = '```Record: {} {}-{} {}'.format(player1,record[0],record[1],player2)


            final += '\n\n'

            
            player1Tournaments  = M.getPlayerTournaments(player1)
            player2Tournaments = M.getPlayerTournaments(player2)
            tournaments = sorted(set(player1Tournaments) & set(player2Tournaments))
            for tournament in M.tournamentList:
                on = 0
                if tournament.name in tournaments:
                    setTuple  = tournament.sets
                    for set1 in setTuple:
                        if [player1,player2] == set1 or [player2,player1] == set1:
                            if on == 1:
                                final += '{} - {}\n'.format(set1[0],set1[1])
                            else:
                                final += '{}:\n'.format(tournament.name)
                                final += '{} - {}\n'.format(set1[0],set1[1])
                                on = 1
                    final += '\n'
            final += '```'
        else:
            final = '```{} has no record v.s. {}```'.format(player1, player2)

        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)



    elif message.content.startswith('!compare'):
        txt = re.sub("(!compare )", "", message.content)
        txt = txt.split("-")
        player1 = sf.normalize_name(txt[1])
        player2 = sf.normalize_name(txt[2])
        file = open('relevant.txt','r')
        L = file.readlines()
        file.close()
        relevant = []
        for line in L:
            relevant.append(sf.normalize_name(line.strip('\n')))
        player1Record = M.getPlayerWinsLossDict(player1)
        player2Record = M.getPlayerWinsLossDict(player2)

        dic = set(player1Record.keys()) & set(player2Record.keys())
        common = []
        for element in dic:
            if element not in relevant:
                common.append(element)
        common = sorted(common)
        enemyList = relevant + common

        value = 10
        for name in enemyList:
            if len(name) > value:
                value = len(name)
        final = '```'
        fermat = '{:<%d}\t{:<%d}\t{:<%d}\n' % (value,len(player1),len(player2))
        final += fermat.format('Comparing:',player1,player2)

        for enemy in enemyList:
            if enemy in player1Record.keys():
                p1WinLoss = player1Record[enemy]
                p1Record = '{}-{}'.format(p1WinLoss[0],p1WinLoss[1])
            else:
                p1Record = 'n/a'
            if enemy in player2Record.keys():
                p2WinLoss = player2Record[enemy]
                p2Record = '{}-{}'.format(p2WinLoss[0],p2WinLoss[1])
            else:
                p2Record = 'n/a'
            final += fermat.format(enemy,p1Record,p2Record)
        final += '```'

        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)
        
        
    elif message.content.startswith('!activity'):
        txt = message.content[10:]
        player1 = sf.normalize_name(txt)
        final = "```{}'s Tournaments:\n".format(player1)
        activeTournaments = M.getPlayerActivityTournaments(player1)
        if len(activeTournaments ) != 0:
            for tournament in sorted(activeTournaments):
                final += tournament+'\n'
            final += "{} has {} tournaments for activity```".format(player1, len(activeTournaments))
        else:
            final = '```{} has no tournaments for activity```'.format(player1)


        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)

    elif message.content.startswith('!alt_names'):
        txt = re.sub("!alt_names ", "", message.content)
        player = sf.normalize_name(txt)
        if player in alt_names_dict:
            alt_names = alt_names_dict[player]
            final = "```{}'s alts: {}```".format(player,alt_names)
        else:
            final = "```{} player does not have alternates```".format(player)
        yield from client.send_message(message.channel, final)

    elif message.content.startswith('!add_alt'):
        txt = re.sub("(!add_alt )", "", message.content)
        txt = txt.split("-")
        player = sf.normalize_name(txt[1])
        alt_name = txt[2]
        if player in alt_names_dict:
            pc.add_alt_name_to_dict(player, alt_name)
            
            alt_names = alt_names_dict[player]
            final = "```{}'s alts: {}```".format(player,alt_names)       
        else:
            alt_names_dict[player] = alt_name

            alt_names = alt_names_dict[player]
            final = "```{}'s alts: {}```".format(player,alt_names)
        pc.save_alt_names_dict()
        M.normalizeNamesAgain()
        yield from client.send_message(message.channel, final)

    elif message.content.startswith('!results'):
        txt = re.sub("(!results )", "", message.content)
        player = sf.normalize_name(txt)
        player_record_dict = M.getPlayerWinsLossDict(player)
        enemies = sorted(player_record_dict,key=lambda x:(len,x[0]),reverse=False)
        'enemy: (1,2)'
        final = "```"
        final += "{}'s Record:\n".format(player)
        for enemy in enemies:
            win, loss = player_record_dict[enemy]
            final += '{} {}-{}\n'.format(enemy,win,loss)
        final.strip('\n')
        final += '```'

        if len(final) < 2000:
            yield from client.send_message(message.channel, final)
        else:
            final_list = split_message(final)
            for final in final_list:
                yield from client.send_message(message.channel, final)


##    elif message.content.startswith('!alltournaments'):
##        tournaments = M.tournamentsAdded()
##        final = '```'
##        final += 'All tournaments:\n'
##        for tournament in tournaments:
##            final += tournament+'\n'
##        final.strip('\n')
##        final += '```'
##        if len(final) < 2000:
##            yield from client.send_message(message.channel, final)
##        else:
##            final_list = split_message(final)
##            for final in final_list:
##                yield from client.send_message(message.channel, final)

    elif message.content.startswith('!addurl'):
        url = re.sub("(!addurl )", "", message.content)
        tmp = yield from client.send_message(message.channel, '```Adding tournament```')
        try:
            M.addTournament(url)
            M.saveToFile('LoadIn.txt')
            yield from client.edit_message(tmp, '```Tournament has been added```')

        except:
            yield from client.edit_message(tmp, '```There was an error```')


    elif message.content.startswith('!addurl'):
        url = re.sub("(!addurl )", "", message.content)
        tmp = yield from client.send_message(message.channel, '```Adding tournament```')
        try:
            M.addTournament(url)
            M.saveToFile('LoadIn.txt')
            yield from client.edit_message(tmp, '```Tournament has been added```')

        except:
            yield from client.edit_message(tmp, '```There was an error```')


    elif message.content.startswith('!uploadloadin'):
        yield from client.send_file(message.channel,filepath+'/LoadIn.txt',filename='LoadIn.txt',content="Here's the saved data")
    elif message.content.startswith('!upload_alt_names'):
        yield from client.send_file(message.channel,filepath+'/Names.txt',filename='Names.txt',content="Here's the alt names file")
    elif message.content.startswith("!uploadentrants"):
        M.saveEntrantsToFile("Entrants.txt")
        yield from client.send_file(message.channel,filepath+'/Entrants.txt',filename='Entrants.txt',content="Here's the entrants file")
    elif message.content.startswith("!uploadtournaments"):
        M.saveTournamentsToFile("Tournaments.txt")
        yield from client.send_file(message.channel,filepath+'/Tournaments.txt',filename='Tournaments.txt',content="Here's the tournaments file")


        
        
        
        
    elif message.content.startswith('!commands'):
        final = '```List of commands:\n'
        final += "!playertournaments {player}: returns all player's tournaments\n"
        final += '!activitytournaments: returns the tournaments that count for activity\n'
        final += '!activity {player}: returns the activity tournaments for player\n'

        final += '!alt_names {player}: returns the alt names for a player\n'
        final += "!add_alt -{player} -{replacement}: adds the replacement to a player's alts\n"

        final += '!h2h -{player1} -{player2}: returns the h2h record between player1 and player2\n'
        final += '!compare -{player1} -{player2}: returns the record vs PR + extras and vs both have played against\n'

        final += "!results {player}: returns player's results\n"
        
##        final += "!alltournaments: returns all tournaments in the database... it's going to be long\n"


        final += "!addurl {url}: adds tournament and saves it. Challonge or Smash.gg have to include http section\n"


        final += "!uploadloadin: uploads the LoadIn.txt file\n"
        final += "!uploadtournaments: uploads the file with all tournament info\n"
        final += "!uploadentrants: uploads the entrant list file\n"
        final += "!upload_alt_names: uploads the alt names file\n"

        

        final += "!commands: returns commands\n"
        final += "```"
        yield from client.send_message(message.channel, final)



            

client.run('####USE UR OWN BOT KEY####')#SacaSuBot
