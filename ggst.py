import aiohttp, bs4, typing, json

with open('chars.json', 'r') as f:
    chars = json.load(f)

class MatchupStats(typing.TypedDict):
    character: str
    matches: int
    win_rate: float

class EloStats(typing.TypedDict):
    character: str
    elo: int
    offset: int
    games: int
    position: typing.Optional[int]

class GGSTWebScraper:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    # base function from which most other functions start their data tree
    async def search_player(self, search: str) -> list[bs4.element.Tag]:
        results = []
        async with self.session.get(f'http://ratingupdate.info/?name={search}') as resp:
            t = await resp.text()
            soup = bs4.BeautifulSoup(t, 'html.parser')
            res: list[bs4.element.Tag] = soup.find('div', class_='table-container').find_all('td')
            for e in res:
                if e.find('a'):
                    t = e.find('a')['title']
                    if t == search:
                        results.append(e)
        if results == []:
            raise Exception(f"Player {search} not found. Be sure to type your username correctly, accounting for case and other factors.")
        return results

    # requires search_player
    def search_player_char_link(self, data: list[bs4.element.Tag], char: str) -> str:
        for e in data:
            if e.find('a'):
                try:
                    chars[char.lower()]
                except KeyError:
                    raise Exception("Character not found, ensure you are typing it exactly as it is found on the ratingupdate website.")
                if e.find('a')['href'].endswith(chars[char.lower()]):
                    return e.find('a')['href']
        raise Exception("You have no matches with this character in the database.")

    # requires search_player_char_link
    async def get_player_char_page_data(self, path: str) -> list[bs4.element.Tag]:
        async with self.session.get(f'http://ratingupdate.info{path}') as resp:
            t = await resp.text()
            soup = bs4.BeautifulSoup(t, 'html.parser')
            res: list[bs4.element.Tag] = soup.find('div', class_='table-container').find_all('tr')
            return res

    # requires get_player_char_page_data
    def get_char_matchup_stats(self, data: list[bs4.element.Tag], char: str) -> MatchupStats:
        for e in data:
            if e == data[0]:
                continue
            if e.contents[1].get_text(strip=True) == char.capitalize():
                return {
                    'character': e.contents[1].get_text(strip=True),
                    'matches': int(e.contents[3].get_text(strip=True)),
                    'win_rate': float(e.contents[5].get_text(strip=True)[:-1]) / 100
                }
    
    # requires search_player_char_link
    async def get_elo(self, path: str) -> EloStats:
        async with self.session.get(f'http://ratingupdate.info{path}') as resp:
            t = await resp.text()
            soup = bs4.BeautifulSoup(t, 'html.parser')
            res = soup.find('div', class_='content').find('h2').get_text(strip=True)
            s = " ".join(res.replace('\n', '').replace('#', ' #').split()).split()
            return {
                'character': s[0],
                'elo': int(s[2]),
                'games': int(s[4][1:]),
                'offset': int(s[3][1:]),
                'position': int(s[6][1:]) if len(s) >= 7 else None
            }

    #requires get_player_char_page_data  
    def get_matchup_stats(self, data: list[bs4.element.Tag]) -> list[MatchupStats]:
        stats = []
        for e in data:
            if e == data[0]: continue
            if e.contents[1].get_text(strip=True) == 'Overall': continue
            stats.append(
                {
                    'character': e.contents[1].get_text(strip=True),
                    'matches': int(e.contents[3].get_text(strip=True)),
                    'win_rate': float(e.contents[5].get_text(strip=True)[:-1]) / 100
                }
            )
        return stats