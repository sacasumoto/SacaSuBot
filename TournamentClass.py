import requests
import scraping_functions as sf
import pytz as pytz
from datetime import datetime
import parse
"""
Copyright (c) 2015 Andrew Nestico

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

"""
Thanks to Andrew Nestico

"""


tournament_events_url = "https://api.smash.gg/tournament/%s?expand[0]=event" #% slug
event_url = "https://api.smash.gg/tournament/%s/event/%s?expand[0]=groups&expand[1]=phase"#% (slug,event_slug)
phase_url = "http://api.smash.gg/phase_group/%s?expand[0]=sets&expand[1]=entrants" #% event_slug

'''Smash.GG Code'''

def get_tournament_slug_from_smashgg_urls(url):
    return(url.split("/")[4])

typical_event_slugs = ['melee-singles','smash-melee','singles','tmt-top-8','ladder']


def get_tournament_event_slugs(slug):
    tournament_data = requests.get(tournament_events_url % slug,
                                   verify="cacert.pem").json()
    event_slugs = []
    event_dict = {}
    for event in tournament_data["entities"]["event"]:
##        event_slugs.append(event["slug"].split("/")[-1])
        event_dict[event["name"]] = event["slug"].split("/")[-1]
    return(event_dict)

def get_tournament_info(slug):
    tournament_url = "https://api.smash.gg/tournament/" + slug
    t = requests.get(tournament_url, verify='cacert.pem')
    tournament_data = t.json()
    tournament_name = tournament_data["entities"]["tournament"]["name"]
    tournament_event_slugs = get_tournament_event_slugs(slug)
    
    timezone = tournament_data["entities"]["tournament"]["timezone"]
    if timezone != True:
        timezone = 'America/Los_Angeles'
    counter = 0
    for typical_slug in typical_event_slugs:
        if typical_slug in tournament_event_slugs.values():
            counter += 1
            url = event_url % (slug,typical_slug)
            e = requests.get(url, verify='cacert.pem')
            event_data = e.json()
            event_id = event_data["entities"]["event"]["id"]
    if counter == 0:
        print(tournament_event_slugs.values(), 'These values are not in typical slugs')


    timestamp = event_data["entities"]["event"]["endAt"]
    if not timestamp:
        timestamp = tournament_data["entities"]["tournament"]["endAt"]
    # Get local date
    date = datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).date()
    date = str(date)
    count = None
##
##    ## Get standings
##    if 'training-mode-tuesdays' in slug:
##        attendee_url = 'https://api.smash.gg/tournament/'+slug+'/attendees?filter=%7B"eventIds"%3A'+str(event_id)+'%7D'
##        a_data = requests.get(attendee_url, verify='cacert.pem').json()
##        count = a_data["total_count"]
##    else:
##        try:
##            standing_string = "/standings?expand[]=attendee&per_page=100"
##            standing_url = event_url + standing_string
##            s = requests.get(standing_url,verify='cacert.pem')
##            s_data = s.json()
##            count = s_data["total_count"]
##        except:
##            attendee_url = 'https://api.smash.gg/tournament/'+slug+'/attendees?filter=%7B"eventIds"%3A'+str(event_id)+'%7D'
##            a_data = requests.get(attendee_url, verify='cacert.pem').json()
##            count = a_data["total_count"]
    return([tournament_name,event_id,count,str(date)])
    
def create_smashgg_api_urls(slug):
    """from master url creates list of api urls for pools and bracket"""
    urlList = []
    tournament_event_slugs = get_tournament_event_slugs(slug)
    for typical_slug in typical_event_slugs:
        if typical_slug in tournament_event_slugs.values():
            url = event_url % (slug, typical_slug)
            data = requests.get(url,verify='cacert.pem').json()
            try:
                groups = data["entities"]["groups"]
                
                for i in range(len(groups)):
                    iD = str(groups[i]["id"])
                    urlList.append("http://api.smash.gg/phase_group/" + iD + "?expand[0]=sets&expand[1]=entrants")
            except:
                print(typical_slug + " has been skipped")

    if len(urlList) == 0:
        print(tournament_event_slugs.values(), 'These values are not in typical slugs')

    return(urlList)

def parse_smashgg_set(set,entrant_dict):
    winnerId = set["winnerId"]
    entrant1Id = set["entrant1Id"]
    entrant1Score = set["entrant1Score"]
    entrant2Id = set["entrant2Id"]
    entrant2Score = set["entrant2Score"]

    if entrant1Id and entrant2Id:
        entrant1Name = sf.normalize_name(entrant_dict[entrant1Id])
        entrant2Name = sf.normalize_name(entrant_dict[entrant2Id])

        if entrant1Name != '' or entrant2Name != '':
            if type(entrant1Score) is int and type(entrant2Score) is int:
                if entrant1Score > -1 and entrant2Score > -1:
                    if entrant1Id == winnerId:
                        return entrant1Name + "," + entrant2Name
                    else:
                        return entrant2Name + "," + entrant1Name
            else:
                if entrant1Id == winnerId:
                    return entrant1Name + "," + entrant2Name
                elif entrant2Id == winnerId:
                    return entrant2Name + "," + entrant1Name
        else:
            print("Error adding players")
            return('error1,error2')


def write_txt_from_smashgg(slug):
    """Writes smash.gg bracket data to a file."""
    urlList = create_smashgg_api_urls(slug)
    strTuple = ''
    entrantCountedDict = {}
    
    for url in urlList:
        try:
            data = requests.get(url,verify='cacert.pem').json()
            entrants = data["entities"]["entrants"]
            entrant_dict = {}
            for entrant in entrants:
                name = entrant["name"]
                iD = entrant["id"]
                entrant_dict[iD] = name
                if name not in entrantCountedDict.values():
                    entrantCountedDict[iD] = name
                    
                
            sets = data["entities"]["sets"]
            set_data = ""
            grand_finals = ""
            for set in sets:
                parsed_set = parse_smashgg_set(set, entrant_dict)
                if parsed_set:
                    if set["isGF"]:
                        grand_finals += parsed_set + "\n"
                    else:
                        set_data += parsed_set + "\n"
            parsed_matches = set_data + grand_finals
            strTuple += parsed_matches
            
        except:
            print("An Error.. is it non-started event?")
            continue

    entrantcount = len(entrantCountedDict)
    return(strTuple, entrantcount)

def setTuple(strTuple):
    sets = strTuple.split('\n')
    setTuple = []
    for match in sets:
        if len(match) > 0:
            if len(match.split(",")) == 2:
                setTuple.append(match.split(","))
    return(setTuple)

def playerWins(player,setTuple):
    winList = []
    for p1,p2 in setTuple:
        if p1 == player:
            winList.append(p2)  
    return(winList)

def playerLoss(player,setTuple):
    lossList = []
    for p1,p2 in setTuple:
        if p2 == player:
            lossList.append(p1)
    return(lossList)

def entrantList(setTuple):
    EntrantList = []
    for p1,p2 in setTuple:
        if p1 not in EntrantList:
            EntrantList.append(p1)
        if p2 not in EntrantList:
            EntrantList.append(p2)
    return(EntrantList)

def entrantCount(setTuple):
    return(len(entrantList(setTuple)))
    

'''

Challonge

'''


def getTournamentSlug(url):
    L = url.split('/')
    p1 = L[2]
    p2 = L[3]
    if p1 == 'challonge.com':
        slug = p2
    else:
        p1 = p1.split('.')[0]
        slug = p1+'-'+p2
    return(slug)

def getTournamentInfo(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'.json?api_key='+key
    data = requests.get(url,verify='cacert.pem').json()
    Name = data['tournament']['name']
    ID = data['tournament']['id']
    EntrantCount = data['tournament']['participants_count']
    Date = data['tournament']['started_at'][:10]

    return([Name,ID,EntrantCount,Date])

def getParticipantIDs(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'/participants.json?api_key='+key
    data = requests.get(url,verify='cacert.pem').json()
    D = {}
    for entrant in data:
        if entrant['participant']['name']:                 
            name = entrant['participant']['name']
        else:
            name = entrant['participant']['username']
        if entrant['participant']['id']:
            entrant_id = entrant['participant']['id']
        else:
            entrant_id = entrant['participant']['group_player_ids']
        D[entrant_id] = name
    return(D)
    

def getTournamentSets(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'/matches.json?api_key='+key+"&state=complete"
    data = requests.get(url, verify='cacert.pem').json()
    nameIDDict = getParticipantIDs(slug,key)
    setTuple = []
    nonDQs = []
    for match in data:
        m = match['match']
        setStringsList = m['scores_csv'].split(',')
        s1T = 0
        s2T = 0
        for matchCount in setStringsList:
            s1,s2 = parse.parse("{:d}-{:d}", matchCount)
            s1T += s1
            s2T += s2
        if s1T == -1 or s2T == -1:
            continue
        else:
            nonDQs.append(match)
            
##        try:
##            s1,s2 = parse.parse("{:d}-{:d}", setCount)
##            if s1 < 0 or s2 < 0:
##                continue
##            else:
##                nonDQs.append(match)
##        except Exception as e:
##            continue
####            print('Invalid Set')
    
    for match in nonDQs:        
        p1ID = match["match"]["winner_id"]
        p2ID = match["match"]["loser_id"]
##        print(p1ID,p2ID)
##        print(sf.normalize_name(nameIDDict[p1ID]), sf.normalize_name(nameIDDict[p2ID]))
        p1 = sf.normalize_name(nameIDDict[p1ID])
        p2 = sf.normalize_name(nameIDDict[p2ID])
        setTuple.append([p1,p2])
    return(setTuple)

def challongeURL(url):
    slug = getTournamentSlug(url)
    key = #CHALLONGE API KEY W.E
    L = getTournamentInfo(slug,key)
    Name = L[0]
    ID = L[1]
    EntrantCount = L[2]
    Date = L[3]
    Data = getTournamentSets(slug,key)
    return({'Name':Name,'ID':ID,'Slug':slug,'Entrants':EntrantCount,'Date':Date,'Data':Data,'Url':url})



'''

Tournament Code

'''

class Tournament:
    def __init__(self, url,**kwargs):
        if url == "Loading":
            self.name = kwargs['Name']
            self.eventID = kwargs['ID']
            self.slug = kwargs['Slug']
            self.entrantcount = kwargs['Entrants']
            self.date = kwargs['Date']
            self.sets = kwargs['Data']
            self.url = kwargs['Url']
            self.raw = kwargs
        elif "challonge.com" in url:
            D = challongeURL(url)
            self.name = D['Name']
            self.eventID = D['ID']
            self.slug = D['Slug']
            self.entrantcount = D['Entrants']
            self.date = D['Date']
            self.sets = D['Data']
            self.url = D['Url']
            self.raw = D    
        else:
            self.slug = get_tournament_slug_from_smashgg_urls(url)
            self.info = get_tournament_info(self.slug)
            self.name = self.info[0]
            self.eventID = self.info[1]
            self.date = self.info[3]
            str_data, self.entrantcount = write_txt_from_smashgg(self.slug)
            self.sets = setTuple(str_data)
            self.url = 'https://smash.gg/tournament/'+self.slug            
            self.raw = {'Name':self.info[0],
                        'ID':self.info[1],
                        'Slug':self.slug,
                        'Entrants':self.entrantcount,
                        'Date':self.info[3],
                        'Data':self.sets,
                        'Url':self.url}
    
    def getEntrantList(self):
        return(entrantList(self.sets))
    def getPlayerLoss(self,player):
        return(playerLoss(player,self.sets))
    def getPlayerWins(self,player):
        return(playerWins(player,self.sets))
    def getTournamentName(self):
        return(self.name)
    def getTournamentEntrantcount(self):
        return(self.entrantcount)
    def getTournamentDate(self):
        return(self.date)
    def getTournamenteventID(self):
        return(self.eventID)
    def getTournamentSlug(self):
        return(self.slug)
    def getSetTuple(self):
        return(self.sets)
    def verifySetData(self):
        if len(self.sets) != 0:
            return(True)


'''

MasterTournament Code Beings

'''



class MasterTournament:
    def __init__(self,tournamentList):
        self.tournamentList = tournamentList

    def addTournament(self, url,**kwargs):
        placer = Tournament(url,**kwargs)
        if placer.verifySetData():
            tournamentSlugs = []
            for tournament in self.tournamentList:
                tournamentSlugs.append(tournament.slug)
            if placer.slug not in tournamentSlugs:
                self.tournamentList.append(placer)
        else:
            print('Empty Tournament, not added')
            return(False)


    def addTournamentFromUrlList(self,urlList):
        for url in urlList:
            self.addTournament(url)

    def tournamentsAdded(self):
        tournamentNames = []
        for tournament in self.tournamentList:
            tournamentNames.append(tournament.getTournamentName())
        return(sorted(tournamentNames))
    
    def deleteTournament(self,tournamentID):
        for tournament in self.tournamentList:
            if tournament.eventID == tournamentID:
                self.tournamentList.remove(tournament)
        return(self.tournamentsAdded())
    
    def getEntrantList(self):
        entrantsRaw = []
        entrantsNormalized = []
        for tournament in self.tournamentList:
            entrantsRaw += tournament.getEntrantList()
        for player in entrantsRaw:
            if player not in entrantsNormalized:
                entrantsNormalized.append(player)
    
        return(sorted(entrantsNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getUniqueEntrantsNumber(self):
        return(len(self.getEntrantList()))

    def getTotalEntrantsNumber(self):
        entrantsRaw = []
        for tournament in self.tournamentList:
            entrantsRaw += tournament.getEntrantList()
        return(len(entrantsRaw))

    def getPlayerTournaments(self,player):
        tournaments = []
        for tournament in self.tournamentList:
            if player in tournament.getEntrantList():
                tournaments.append(tournament.getTournamentName())
        return(sorted(tournaments))

#Player Activity Code
    def getPlayerActivityTournaments(self,player):
        tournaments = []
        for tournament in self.tournamentList:
            if player in tournament.getEntrantList() and tournament.getTournamentEntrantcount() > 49:
                tournaments.append(tournament.getTournamentName())
        return(sorted(tournaments))

    def getActivityTournaments(self):
        tournaments = []
        for tournament in self.tournamentList:
            if tournament.getTournamentEntrantcount() > 49:
                tournaments.append((tournament.getTournamentEntrantcount(),tournament.getTournamentName()))
        return(sorted(tournaments))
        
    def getAllPlayersActivity(self):
        D = {}
        players = []
        activitytournaments = []
        for tournament in self.tournamentList:
            if tournament.getTournamentEntrantcount() > 49:
                for player in tournament.getEntrantList():
                    if player not in D:
                        D[player] = [1,tournament.getTournamentName()]
                    else:
                        D[player][0] += 1
                        D[player][1] += ' '+tournament.getTournamentName()
        return(D)
                
    def getActivePlayers(self):
        D1 = {}
        D2 = self.getAllPlayersActivity()
        for key in D2:
            if D2[key][0] > 3:
                D1[key] = [D2[key][0],D2[key][1]]
        return(D1)
            
                
    def getPlayerWins(self,player):
        winsRaw = [] #List of players Player beat
        winsNormalized = []
        winChecked = []#List of players checked
        for tournament in self.tournamentList:
            winsRaw += tournament.getPlayerWins(player)
        for playerWinAgainst in winsRaw:
            if playerWinAgainst not in winChecked:
                winChecked.append(playerWinAgainst)
                count = winsRaw.count(playerWinAgainst)
                winsNormalized.append(playerWinAgainst + ' x{}'.format(count))
        return(sorted(winsNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getPlayerLoss(self,player):
        lossRaw = []
        lossNormalized = []
        lossChecked = []
        for tournament in self.tournamentList:
            lossRaw += tournament.getPlayerLoss(player)
        for playerLossAgainst in lossRaw:
            if playerLossAgainst not in lossChecked:
                lossChecked.append(playerLossAgainst)
                count = lossRaw.count(playerLossAgainst)
                lossNormalized.append(playerLossAgainst + ' x{}'.format(count))
        return(sorted(lossNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getPlayerWinsLossDict(self,player):
        D = {}
        
        winsRaw = []
        winChecked = []
        lossRaw = []
        lossChecked = []
        for tournament in self.tournamentList:
            winsRaw += tournament.getPlayerWins(player)
            lossRaw += tournament.getPlayerLoss(player)
        for playerWinAgainst in winsRaw:
            if playerWinAgainst not in winChecked:
                winChecked.append(playerWinAgainst)
                count = winsRaw.count(playerWinAgainst)
                if playerWinAgainst not in D:
                    D[playerWinAgainst] = [0,0]
                D[playerWinAgainst][0] += count

        for playerLossAgainst in lossRaw:
            if playerLossAgainst not in lossChecked:
                lossChecked.append(playerLossAgainst)
                count = lossRaw.count(playerLossAgainst)
                if playerLossAgainst not in D:
                    D[playerLossAgainst] = [0,0]
                D[playerLossAgainst][1] += count

        return(D)
        

    def getPlayerTotalSets(self,player):
        count = 0
        D = self.getPlayerWinsLossDict(player)
        for opponent in D:
            W,L = D[opponent]
            count += W
            count += L
        return(count)
     
    def getPlayerWinsLoss(self,player):
        print('Wins:{}\nLosses:{}'.format(self.getPlayerWins(player),self.getPlayerLoss(player)))
      
    def saveToFile(self,filename):
        Final = ''
        L = []
        for tournament in self.tournamentList:
            L.append(tournament.raw)
        file = open(filename,'w',encoding='utf-8')
        for data in L:
            Final += str(data) + '\n'
        file.write(Final)
        file.close()

    def loadFromFile(self,filename,encoding='utf-8'):
        file = open(filename,'r',encoding='utf-8')
        L = file.readlines()
        for tournamentDict in L:
            self.addTournament('Loading',**eval(tournamentDict))
        print("Done")
        return(self.tournamentsAdded())

    def addFromUrlFile(self,filename,encoding='utf-8'):
        file = open(filename,'r',encoding='utf-8')
        
        L = file.readlines()
        for url in L:
            print(url.strip('\n'))
            self.addTournament(url.strip('\n'))
        print('Done')
        return(self.tournamentsAdded())

    def normalizeNamesAgain(self):
        for tournament in self.tournamentList:
            newsetTuple =[]
            for p1,p2 in tournament.sets:
                newsetTuple.append([sf.normalize_name(p1),sf.normalize_name(p2)])
            tournament.setTuple = newsetTuple
            tournament.raw['Data'] = newsetTuple
        self.saveToFile('LoadIn.txt')
        print('Done')

    def saveEntrantsToFile(self,filename):
        entrants = self.getEntrantList()
        final = ""
        for entrant in entrants:
            final += entrant +"\n"
        final = final.strip("\n")
        file = open(filename,"w",encoding='utf-8')
        file.write(final)
        file.close()
        print("Done")
            
    def saveTournamentsToFile(self,filename):
        final = ''
        L = []
        for tournament in self.tournamentList:
            L.append((tournament.date,tournament))
        L.sort(key=lambda tup: tup[0])

        maxName = 0
        maxSlug = 0
        maxUrl = 0
        for date, tournament in L:
            if len(tournament.name) > maxName:
                maxName = len(tournament.name)
            if len(tournament.slug) > maxSlug:
                maxSlug = len(tournament.slug)
            if len(tournament.url) > maxUrl:
                maxUrl = len(tournament.url)
        maxName += 5
        maxSlug += 5
        maxUrl += 5
        fermat = '{:<10}\t{:<15}\t{:<%d}\t{:<10}\t{:<%d}\n' % (maxName, maxUrl)
        title = fermat.format('ID:','Date:','Name:','Entrants:','Url:')
        final += title
        for date, tournament in L:
            final += fermat.format(tournament.eventID,tournament.date,tournament.name,tournament.entrantcount,tournament.url.strip('\n'))
        final = final.strip("\n")
        file = open(filename,"w",encoding="utf-8")
        file.write(final)
        file.close()
        print("Done")


    def clearAll(self):
        self.tournamentList = []

##if '__name__' != '__init__':
##    M = MasterTournament([])
##    M.loadFromFile('LoadIn.txt')
##    M.normalizeNamesAgain()
##    M.saveToFile('LoadIn.txt')

