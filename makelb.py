import csv
import requests

API = "https://www.speedrun.com/api/v1/"

print('[')

result = [] # backup here
names = [runner['name'] for runner in result] #if backup

with open("runners.csv", 'r') as csvfile:
    file = csv.reader(csvfile)

    for i in file:
        if i:
            runner = {}
            runner['name'],runner['id'],runner['flag'],runner['banned'] = i
            if runner['banned'] == 'True':
                runner['name'] = '(Banned User)'
            if runner['name'] not in names:
                while True:
                    try:
                        personalBests = requests.get(f"{API}users/{runner['id']}/personal-bests").json()["data"]
                        firstPlaces = [run for run in personalBests if run['place'] == 1]
                        runner['wrs'] = len(firstPlaces)
                        runner['wrsIL'] = len([run for run in firstPlaces if run['run']['level']])
                        runner['wrsFG'] = runner['wrs'] - runner['wrsIL']
                        runner['podiums'] = len([run for run in personalBests if run['place'] in (1,2,3)])
                        runner['games'] = len(set([run["run"]["game"] for run in personalBests]))
                        runner['categories'] = len(set([run["run"]["category"] for run in personalBests]))
                        runner['wrsGames'] = len(set([run['run']["game"] for run in firstPlaces]))
                        print(runner['wrsGames'])
                        offset = 0
                        total = totalFG = totalIL = 0
                        while True:
                            data = requests.get(
                                f"{API}runs?user={runner['id']}&max=200&offset={offset * 200}&status=verified&orderby=date"
                            ).json()
                            offset += 1
                            for run in data['data']:
                                total +=1
                                if run['level']:
                                    totalIL +=1
                                else:
                                    totalFG +=1
                            if data["pagination"]["size"] < 200:
                                break
                        runner['runs'] = total
                        runner['runsIL'] = totalIL
                        runner['runsFG'] = totalFG
                        break
                    except:
                        print(runner['id'])
                result.append(runner)
            print(str(runner) + ',')

print(']')

import datetime

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
                f"`-.`{i['flag']}`{i['name']} {' ' * (23-len(str(n+1))-len(i['name']))} {i[lbType]}`"
            )
