import requests, json, time, ctypes, random
from rich import print

class Bot:
    def __init__(self):
        self.cookies = open('cookies.txt').read().splitlines()
        self.group_log = {}

    def ratelimited(self, reason):
        for i in range(60):
            ctypes.windll.kernel32.SetConsoleTitleW(f'Ratelimited for: {reason} - {i+1}/60')
            time.sleep(1)

    def start_process(self):
        for cookie in self.cookies:
            response = requests.get(
                'https://www.roblox.com/my/settings/json',
                cookies = {'.ROBLOSECURITY': cookie}
            )
            if response.status_code == 200:
                userid = response.json()['UserId']
                groups = self.owned_groups(userid)
                if groups != None:
                    print(f'[green]{userid} owns {len(groups)} groups')
                    self.group_log[str(userid)] = {'totalFunds': 0, 'totalVisits': 0, 'totalPending': 0, 'groups': {}}
                    self.check_funds(cookie, groups, userid)
                    with open('log.json', 'w') as file:
                        json.dump(self.group_log, file, indent=4)
                else:
                    print(f'[yellow]{userid} owns no groups')
            else:
                print(f'[red]Invalid cookie: {cookie}')

    def owned_groups(self, userid):
        response = requests.get(
            f'https://groups.roblox.com/v2/users/{userid}/groups/roles'
        )
        if response.status_code == 200:
            return [group for group in response.json()['data'] if group['role']['rank'] == 255]

    def check_funds(self, cookie, groups, userid):
        session = requests.Session()
        session.cookies['.ROBLOSECURITY'] = cookie
        checked_groups = 0

        for group in groups:
            self.group_log[str(userid)]['groups'][str(group["group"]["id"])] = {'name': group["group"]["name"], 'robux': None}
            while 1:
                response = session.get(
                    f'https://economy.roblox.com/v1/groups/{group["group"]["id"]}/currency'
                )
                if response.status_code == 200:
                    checked_groups += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(f'Funds checked: {checked_groups}/{len(groups)}')
                    self.group_log[str(userid)]['groups'][str(group["group"]["id"])]['robux'] = response.json()['robux']
                    self.group_log[str(userid)]['totalFunds'] += response.json()['robux']
                    break
                else:
                    if response.json()['errors'][0]['message'] == 'Too many requests':
                        self.ratelimited('checking funds')
                    else: break
        self.all_revenue(session, groups, userid)
        self.check_games(session, groups, userid)

    def all_revenue(self, session, groups, userid):
        checked_groups = 0
        for group in groups:
            while 1:
                response = session.get(
                    f'https://economy.roblox.com/v1/groups/{group["group"]["id"]}/revenue/summary/day',
                )
                if response.status_code == 200:
                    checked_groups += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(f'Revenue checked: {checked_groups}/{len(groups)}')
                    if any(response.json()[k] not in [False, 0] for k in response.json()):
                        self.group_log[str(userid)]['groups'][str(group["group"]["id"])]['revenue'] = {}
                    for k in response.json():
                        self.group_log[str(userid)]['totalPending'] += response.json()['pendingRobux']
                        if response.json()[k]:
                            self.group_log[str(userid)]['groups'][str(group["group"]["id"])]['revenue'][k] = response.json()[k]
                    break
                else:
                    if response.json()['errors'][0]['message'] == 'Too many requests':
                        self.ratelimited('checking revenue')
                    else: break

    def check_games(self, session, groups, userid):
        checked_groups = 0
        for group in groups:
            while 1:
                response = session.get(
                    f'https://games.roblox.com/v2/groups/{group["group"]["id"]}/games?limit=100&sortOrder=Asc',
                )
                if response.status_code == 200:
                    checked_groups += 1
                    ctypes.windll.kernel32.SetConsoleTitleW(f'Games checked: {checked_groups}/{len(groups)}')
                    if len(response.json()['data']):
                        self.group_log[str(userid)]['groups'][str(group["group"]["id"])]['games'] = {}
                    for game in response.json()['data']:
                        self.group_log[str(userid)]['groups'][str(group["group"]["id"])]['games'][str(game['id'])] = {'name': game['name'], 'visits': game['placeVisits']}
                        self.group_log[str(userid)]['totalVisits'] += game['placeVisits']
                    break
                else:
                    if response.json()['errors'][0]['message'] == 'Too many requests':
                        self.ratelimited('checking games')
                    else: break

b = Bot()
b.start_process()
