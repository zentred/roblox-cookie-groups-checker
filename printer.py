import json, traceback, os
from rich import print
os.system('cls')

data = json.load(
    open('log.json')
)

funds = visits = assets = pending = groups_10 = groups_50 = groups_100 = total = groups_500 = 0

for user in data:
    funds += data[user]['totalRobux']
    assets += data[user]['totalAssets']
    visits += data[user]['totalVisits']
    pending += data[user]['totalPending']
    for group in data[user]['groups']:
        members = group['members']
        if members >= 100: groups_100 += 1
        elif members >= 50: groups_50 += 1
        elif members >= 10: groups_10 += 1
        elif members >= 500: groups_500 += 1
        total += 1

print(f'''
    total groups: {total}
        - 10+ members: {groups_10}
        - 50+ members: {groups_50}
        - 100+ members: {groups_100}
        - 500+ members: {groups_500}

    total funds: {funds}
    total pending: {pending}
    total visits: {visits}
    total assets: {assets}
      ''')
