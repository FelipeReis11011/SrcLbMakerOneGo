import csv
import requests
import time

def anyRequests(text):
    while True:
        try:
            return requests.get(text).json()["data"]
        except:
            print(text)

def percent(number):
    number = str(number*100)
    if number == 100:
        return "100.00%"
    if number.find(".")==-1:
        number += ".0000"
    if number.find(".")==1:
        number = "0" + number
    if len(number) > 5:
        number = number[:5]
    number += "%"
    return "0" + number

def prettifyTime(tempo):
    minutos=int(tempo/60)
    segundos=tempo-60*minutos
    horas=int(minutos/60)
    minutos=minutos-60*horas
    dias=int(horas/24)
    horas=horas-24*dias
    retorno=""
    if(dias>0):
        retorno+=str(dias)+" day"+("s, " if dias>1 else ", ")
    if(horas>0):
        retorno+=str(horas)+" hour"+("s, " if horas>1 else ", ")
    if(minutos>0):
        retorno+=str(minutos)+" minute"+("s, " if minutos>1 else ", ")
    retorno+=str(segundos)+" seconds"
    return(retorno)

def verify200data(data,runner,stopCondition = None):
    if stopCondition is None:
        stopCondition = []
    for run in data:
        if run in stopCondition:
            return True
        runner['runs'] +=1
        if run['level']:
            runner['runsIL'] +=1
        else:
            runner['runsFG'] +=1
        if run['comment']:
            if len(run['comment']) > runner['biggestComment']:
                runner['biggestComment'] = len(run['comment'])
                runner['bCurl'] = run["weblink"]
            runner['commentSize'] += len(run['comment'])
        runner['sumOfTimes'] += run['times']['primary_t']
        if run['splits']:
            runner['splitsUsed'] += 1
        if run['system']:
            if run['system']['emulated']:
                runner['emulated'] += 1
            if run['system']['platform']:
                runner['platforms'].add(run['system']['platform'])
    return False

API = "https://www.speedrun.com/api/v1/"

print('[')

result = [
] # backup here
names = [runner['name'] for runner in result] #if backup

mode = "a" if names else "w"
with open("data.csv", mode, newline="") as csvOutput:
    output = csv.writer(csvOutput, delimiter = ";")
    output.writerow(['name','id','wrs','wrsIL',
            'wrsFG','runs','runsIL','runsFG',
            'podiums','games','ILs games','full games',
            'categories','categories ILs','categories Full Game','levels played',
            'Games with at least 1 wr','Games with at least 1 podium',
            'Personal Bests','Obsolete Runs','Second Places','Third Places',
            'Fourth Places','ratio Wrs/pbs','ratio Wrs/runs','Biggest Run Description',
            'Biggest Run Description URL','Run Description Size on Average','Runs Using Splits',
            'Sum Of Runs Times in seconds (Very innacurate)','Sum Of Runs Times Edited',
            'platforms played','Runs Emulated'])
    with open("runners.csv", 'r') as csvRunners:
        file = csv.reader(csvRunners)
        for i in file:
            begin = time.time()
            if i:
                if i[0] in names:
                    continue
                runner = {}
                runner['name'],runner['id'],runner['flag'],runner['banned'] = i
                if runner['banned'] == 'True':
                    runner['name'] = '(Banned User)'
                personalBests = anyRequests(f"{API}users/{runner['id']}/personal-bests")
                runner['personalBests'] = len(personalBests)
                runner['wrs'] = 0
                runner['wrsIL'] = 0
                runner['wrsFG'] = 0
                runner['secondPlaces'] = 0
                runner['thirdPlaces'] = 0
                runner['fourthPlaces'] = 0
                runner['podiums'] = 0
                runner['games'] = set()
                runner['gamesIL'] = set()
                runner['gamesFG'] = set() 
                runner['categories'] = set()
                runner['categoriesIL'] = set()
                runner['categoriesFG'] = set()
                runner['wrsGames'] = set()
                runner['podiumsGames'] = set()
                runner['levels'] = set()
                for run in personalBests:
                    place = run['place']
                    run = run['run']
                    if place == 4 :
                        runner['fourthPlaces'] += 1
                    if place in (1,2,3):
                        runner['podiums'] += 1
                        runner['podiumsGames'].add(run['game'])
                        if place == 2:
                            runner['secondPlaces'] += 1
                        if place == 3:
                            runner['thirdPlaces'] += 1
                        if place == 1:
                            runner['wrs'] += 1
                            if run['level'] is None:
                                runner['wrsFG'] += 1
                            else:
                                runner['wrsIL'] += 1
                            runner['wrsGames'].add(run['game'])
                    runner['games'].add(run['game'])
                    runner['categories'].add(run['game'])
                    if run['level'] is None:
                        runner['gamesFG'].add(run['game'])
                        runner['categoriesFG'].add(run['category'])
                    else: 
                        runner['levels'].add(run['level'])
                        runner['gamesIL'].add(run['game'])
                        runner['categoriesIL'].add(run['category'])
                runner['ratio'] = percent(runner['wrs']/runner['personalBests'])
                runner['runs'] = 0
                runner['runsFG'] = 0
                runner['runsIL'] = 0
                runner['biggestComment'] = 0
                runner['bCurl'] = ""
                runner['commentSize'] = 0
                runner['splitsUsed'] = 0
                runner['sumOfTimes'] = 0
                runner['emulated'] = 0
                runner['platforms'] = set()
                isMoreThan10K = True
                offset = 0
                while offset*200 < 10000:
                    data = anyRequests(f"{API}runs?user={runner['id']}&max=200&offset={offset * 200}&status=verified&orderby=date&direction=asc")
                    offset += 1
                    verify200data(data,runner)
                    if len(data) < 200:
                        isMoreThan10K = False
                        break
                if isMoreThan10K:
                    lastRuns = data.copy()
                    offset = 0
                    while True:
                        data = anyRequests(f"{API}runs?user={runner['id']}&max=200&offset={offset * 200}&status=verified&orderby=date&direction=desc")
                        offset += 1
                        isStop = verify200data(data,runner,lastRuns)
                        if isStop:
                            break
                for cat in ['games','gamesIL','gamesFG','categories',
                            'categoriesIL','categoriesFG','wrsGames',
                            'podiumsGames','levels','platforms']:
                    runner[cat] = len(runner[cat])
                runner['obsoletes'] = runner['runs'] - runner['personalBests']
                info = [runner['name'],
                        runner['id'],
                        runner['wrs'],
                        runner['wrsIL'],
                        runner['wrsFG'],
                        runner['runs'],
                        runner['runsIL'],
                        runner['runsFG'],
                        runner['podiums'],
                        runner['games'],
                        runner['gamesIL'],
                        runner['gamesFG'],
                        runner['categories'],
                        runner['categoriesIL'],
                        runner['categoriesFG'],
                        runner['levels'],
                        runner['wrsGames'],
                        runner['podiumsGames'],
                        percent(runner['wrsGames']/runner['games']).replace(".",","),
                        runner['personalBests'],
                        runner['obsoletes'],
                        runner['secondPlaces'],
                        runner['thirdPlaces'],
                        runner['fourthPlaces'],
                        runner['ratio'],
                        percent(runner['wrs']/runner['runs']).replace(".",","),
                        runner['biggestComment'],
                        runner['bCurl'],
                        str(runner['commentSize']/runner['runs']),
                        runner['splitsUsed'],
                        str(runner['sumOfTimes']),
                        prettifyTime(runner['sumOfTimes']),
                        runner['platforms'],
                        runner['emulated']]
                output.writerow(info)
                result.append(runner)
                print(str(runner) + ',')
            end = time.time()
            print(prettifyTime(end-begin))
print(']')

import datetime
result.sort(
    key=lambda x: x['ratio'], reverse=True
)

print('ratio')

print(datetime.datetime.now().date())

banned = 0
position = 0
lastValue = float('inf')

for n, i in enumerate(result):
    if i['banned'] == 'False':
        print(
            f"{i['flag']}`{i['name']} {' ' * (23-len(i['name']))} {i['ratio']}`"
        )
    else:
        banned += 1
        print(
            f"{i['flag']}`(Banned User)            {i['ratio']}`"
        )
    if n%50 == 49:
        print()

for lbType in ('wrs','wrsFG','wrsIL','runs','games','categories','runsIL','runsFG','podiums','wrsGames'):
    result.sort(
        key=lambda x: x[lbType], reverse=True
    )

    print(lbType)

    print(datetime.datetime.now().date())

    banned = 0
    position = 0
    lastValue = float('inf')
    
    for n, i in enumerate(result):
        if i['banned'] == 'False':
            if i[lbType] != lastValue:
                position = n + 1 - banned
            lastValue = i[lbType]
            print(
                f"`{position}.`{i['flag']}`{i['name']} {' ' * (23-len(str(n+1))-len(i['name']))} {i[lbType]}`"
            )
        else:
            banned += 1
            print(
                f"`{'-' * len(str(position))}.`{i['flag']}`(Banned User) {' ' * (10-len(str(n+1)))} {i[lbType]}`"
            )
