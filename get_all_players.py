import csv
import string

import requests
from bs4 import BeautifulSoup

BASE_URL = 'www.basketball-reference.com'


def read_url_as_bs(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def read_all_players():
    all_players_data = []
    for letter in string.ascii_lowercase:
        url = f'http://{BASE_URL}/players/{letter}/'
        player_list_bs = read_url_as_bs(url)
        all_players = player_list_bs.findAll('th', {'data-stat': 'player', 'scope': 'row'})
        for player in all_players:
            shortname = player.attrs['data-append-csv']
            try:
                href = player.contents[0].attrs['href']
                name = str(player.contents[0].contents[0])
            except KeyError:
                href = player.contents[0].contents[0].attrs['href']
                name = str(player.contents[0].contents[0].contents[0])
            all_players_data.append({
                'name': name,
                'shortname': shortname,
                'href': href
            })
    return all_players_data


def save_all_players_to_csv(data, csv_path):
    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name', 'shortname', 'href'])
        writer.writeheader()
        writer.writerows(data)


def read_all_players_from_csv(csv_path):
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def main():
    data = read_all_players()
    save_all_players_to_csv(data, 'players.csv')


if __name__ == "__main__":
    main()
