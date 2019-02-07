import TournamentClass as TC




Tier1 = ['Mango',
         'Sfat',
         'Westballz',
         'Lucky',
         'S2J',
         'Mike Haze',
         'Hugs',
         'Macd',
         'Santiago',
         'Squid',
         'Army',
         'Fiction',
         'Captain Faceroll']

Tier2 =['Okamibw',
        'Franz',
        'Zeo',
        'Wieners',
        'Mojoe',
        'Smashdaddy',
        'Neeco',
        'Bizzarro Flame',
        'Psychomidget',
        'Koopatroopa895',
        'Eastcoastjeff',
        'Mixx',
        'Jace',
        'Luigikid',
        'Gage',
        'Cdk']

Tier3 = ['Nut',
         'Venelox',
         'Vavez',
         'Megachristmas',
         'Cesar',
         "Lil' Snack",
         'Kl3Shikuh',
         'Dr. Light',
         'Stomach Flu',
         'Tino',
         'Epic Murloc',
         'Peachicedt',
         'Jago',
         'Rymo',
         'Tenshi',
         'Dayge',
         'Vavez',
         'Blue',
         'Nishi',
         'Noire',
         'Shoyo',
         'Oli',]

Tier4 = ['Donb',
         'Maruf',
         'Beasty_Turtle3',
         'Hulka',
         'Motoko',
         'Tuxedo Mask',
         'Kramer',
         'Munch',
         'Tapez',
         'Vivi',
         'Sergio',
         'Null',
         'Grape',
         'Kony',
         'Yams',
         'Daddy',
         'Kanti',
         'Eloy',
         'Dd',
         'Cohenski',
         'Casper',
         'Gooms',
         'Tapez',
         'Destroyah',
         'Venti']

OOR = ['Hungrybox',
       'Leffen',
       'Ryan Ford',
       'Azusa',
       'Cal',
       'Crush',
       'N0Ne',
       'Drephen',
       'Medz',
       'Dansdaman',
       'A Rookie',
       'Captainjaime',
       'Zhu',
       'Nmw',
       'Spark',
       'Tai',
       'Ralph',
       'La Luna',
       'Iceman',
       'Rocky',
       'Eddy Mexico',
       'Kira',
       'Widlar',
       'John Wick',
       'Sk92',
       'Yoshimaster3000',
       'Bladewise',
       'Laudandus',
       'Kalamazhu',
       'Shroomed',
       'Homemadewaffles',
       'Bimbo',
       'Vish',
       'Rudolph',
       'Hyprid',
       'Far!',
       '.Jpg',
       'Darrell',
       'Reno',
       'Zorc']                         



def createTier5(MasterTournament):
    M = MasterTournament
    Tier5 = []
    E = M.getEntrantList()
    print(len(E))
##    E = M.getActivePlayers()
##    for player in E:
##        if player not in Tier1 + Tier2 + Tier3 + Tier4 + OOR:
##            Tier5.append(player)
    for player in E:
        if player not in Tier1 + Tier2 + Tier3 + Tier4 + OOR:
            count = M.getPlayerTotalSets(player)
            if count > 5:
                Tier5.append(player)
##    for i in range(len(Tier5)):
##        print(Tier5[i])
    print(len(Tier5))
    return(Tier5)

    
    



def saveToFile(string,filename):
    file = open(filename,'w',encoding='utf-8')
    file.write(string)
    file.close()
def createRatio(W,L):
    T = W+L
    if T != 0:
        ratio = str(round(W/T,2))
    else:
        ratio = 'n/a'
    return(ratio)

def createTNvsTNSheet(Tier,MasterTournament):
    M = MasterTournament
    final = ""
    title = "Matchups\t"
    for player in Tier:
        title += player+"\t"
    title += 'Total:\tWinRatio:'
    title += "\n"
    final += title

    for i in range(len(Tier)):
        line = ''
        nW = 0
        nL = 0
        player = Tier[i]
        playerWinLossDict = M.getPlayerWinsLossDict(player)
        line += player+"\t"
        for j in range(len(Tier)):
            opponent = Tier[j]
            if i == j:
                line += "X\t"
            else:
                if opponent not in playerWinLossDict:
                    line += "n/a\t"
                else:
                    W,L = playerWinLossDict[opponent]
                    nW += W
                    nL += L
                    line += str(W)+"-"+str(L)+"\t"
        line += str(nW)+"-"+str(nL)+'\t'+createRatio(nW,nL)
        line += "\n"
        final += line
    return(final)
        

def createTNvsTMSheet(TierN,TierM,MasterTournament):
    M = MasterTournament
    final = ""
    title = "Matchups\t"
    for player in TierM:
        title += player+"\t"
    title += 'Total:\tWinRatio:'
    title += "\n"
    final += title

    for player in TierN:
        line = ""
        playerWinLossDict = M.getPlayerWinsLossDict(player)
        line += player+"\t"
        nW = 0
        nL = 0
        for opponent in TierM:
            if opponent not in playerWinLossDict:
                line += "n/a\t"
            else:
                W,L = playerWinLossDict[opponent]
                nW += W
                nL += L
                line += str(W)+"-"+str(L)+"\t"
        line += str(nW)+"-"+str(nL)+'\t'+createRatio(nW,nL)
        line += '\n'
        final += line
    return(final)

def createTNvsT5Sheet(TierN,Tier5,MasterTournament):
    M = MasterTournament
    final = ""
    title = "Matchups\tTotal:\tWinRatio:\n"
    final += title

    for player in TierN:
        line = ""
        playerWinLossDict = M.getPlayerWinsLossDict(player)
        line += player+"\t"
        nW = 0
        nL = 0
        for opponent in Tier5:
            if opponent in playerWinLossDict:
                W,L = playerWinLossDict[opponent]
                nW += W
                nL += L
        line += str(nW)+"-"+str(nL)+'\t'+createRatio(nW,nL)
        line += '\n'
        final += line
    return(final)

def createGiant(MasterTournament):
    M = MasterTournament
    final = ""
    Tier5 = createTier5(M)
    L = [Tier1,Tier2,Tier3,Tier4,Tier5]
    D = {str(Tier1):'Tier1',str(Tier2):'Tier2',str(Tier3):'Tier3',str(Tier4):'Tier4',str(Tier5):'Tier5'}
    for T1 in L[:-1]:
        for T2 in L:
            sheet = ''
            final += D[str(T1)]+'\tvs\t'+D[str(T2)]+'\n' 
            if T1 == T2:
                sheet = createTNvsTNSheet(T1,M)+'\n\n'
            elif T1 != T2  and T2 != Tier5:
                sheet = createTNvsTMSheet(T1,T2,M)+'\n\n'
            else:
                sheet = createTNvsT5Sheet(T1,T2,M)+'\n\n'
            final += sheet
        final += '\n\n'
    return(final)
            
M = TC.MasterTournament([])
M.loadFromFile('LoadIn.txt')
saveToFile(createGiant(M),'Test3.tsv')             
