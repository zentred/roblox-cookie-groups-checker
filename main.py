import requests, json, time, ctypes, random
from threading import Thread
from rich import print

class Bot:
    def __init__(self):
        self.cookies = open('cookies.txt').read().splitlines()
        self.data = {}

    def check_cookies(self):
        with requests.Session() as session:
            for cookie in self.cookies:
                session.cookies['.ROBLOSECURITY'] = cookie
                response = session.get(
                    'https://www.roblox.com/my/settings/json'
                )

                if response.status_code == 200:
                    userid = str(response.json()['UserId'])
                    self.data[userid] = {'totalRobux': 0, 'totalPending': 0, 'totalAssets': 0, 'totalVisits': 0, 'totalMembers': 0, 'groups': {}}
                    groups = self.owned_groups(userid)

                    checked = 0
                    for group in groups:
                        groupid = str(group["group"]["id"])
                        self.data[userid]['groups'][groupid] = {'robux': 0, 'assets': 0, 'visits': 0, 'members': group['group']['memberCount'], 'name': group["group"]["name"], 'games': {}}
                        self.check_robux(userid, groupid, session)
                        self.check_revenue(userid, groupid, session)
                        self.check_games(userid, groupid, session)
                        self.check_assets(userid, groupid, session)
                        checked += 1
                        ctypes.windll.kernel32.SetConsoleTitleW(f'{checked}/{len(groups)}')

                    with open('log.json', 'w') as file:
                        json.dump(self.data, file, indent=4)

    def owned_groups(self, userid):
        return [
            group
            for group in requests.get(
                f'https://groups.roblox.com/v2/users/{userid}/groups/roles'
            ).json()['data']
            if group['role']['rank'] == 255
        ]
    
    def check_robux(self, userid, groupid, session):
        while 1:
            response = session.get(
                f'https://economy.roblox.com/v1/groups/{groupid}/currency'
            )
            if response.status_code == 200:
                self.data[userid]['groups'][groupid]['robux'] = response.json()['robux']
                self.data[userid]['totalRobux'] += response.json()['robux']
                break
            else:
                if response.json()['errors'][0]['message'] == 'Too many requests':
                    time.sleep(5)
                else:
                    break

    def check_revenue(self, userid, groupid, session):
        while 1:
            response = session.get(
                f'https://economy.roblox.com/v1/groups/{groupid}/revenue/summary/day',
            )
            if response.status_code == 200:
                if any(response.json()[k] not in [False, 0] for k in response.json()):
                    self.data[userid]['groups'][groupid]['revenue'] = {}
                for k in response.json():
                    if k == 'pendingRobux':
                        self.data[userid]['totalPending'] += response.json()['pendingRobux']
                    if response.json()[k]:
                        self.data[userid]['groups'][groupid]['revenue'][k] = response.json()[k]
                break
            else:
                if response.json()['errors'][0]['message'] == 'Too many requests':
                    time.sleep(5)
                else:
                    break

    def check_games(self, userid, groupid, session):
        while 1:
            response = session.get(
                f'https://games.roblox.com/v2/groups/{groupid}/games?limit=100&sortOrder=Asc&accessFilter=Public',
            )
            if response.status_code == 200:
                if len(response.json()['data']):
                    self.data[userid]['groups'][groupid]['games'] = {}
                for game in response.json()['data']:
                    self.data[userid]['groups'][groupid]['games'][str(game['id'])] = {'name': game['name'], 'visits': game['placeVisits']}
                    self.data[userid]['groups'][groupid]['visits'] += game['placeVisits']
                    self.data[userid]['totalVisits'] += game['placeVisits']
                break
            else:
                if response.json()['errors'][0]['message'] == 'Too many requests':
                    time.sleep(5)
                else:
                    break

    def check_assets(self, userid, groupid, session):
        cursor, assets = '', []
        while cursor != None:
            response = session.get(
                f'https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId={groupid}&creatorType=Group&cursor={cursor}&limit=100&sortOrder=Desc'
            )
            if response.status_code == 200:
                for asset in response.json()['data']:
                    if asset['itemType'] == 'Asset':
                        assets.append(asset['id'])
                cursor = response.json()['nextPageCursor']
            else: break
        self.data[userid]['groups'][groupid]['assets'] += len(assets)
        self.data[userid]['totalAssets'] += len(assets)

b = Bot()
b.check_cookies()
