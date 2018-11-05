import csv
import re

import requests
from bs4 import BeautifulSoup

from get_all_players import read_all_players_from_csv
import pandas as pd

BASE_URL = 'https://www.basketball-reference.com'
COLUMNS = ['Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
           '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST',
           'STL', 'BLK', 'TOV', 'PF', 'PTS']
ALL_COLUMNS = ['Player', 'ShortName', 'Height', 'Weight', 'Position', 'BirthPlace', 'SeasonURL'] + COLUMNS


def get_season_href(r):
    children = list(r.children)
    if not children:
        return ''
    else:
        try:
            return list(children[0].children)[0].attrs['href']
        except:
            return ''


def get_attr(s, attr):
    try:
        return s.find(itemprop=attr).get_text()
    except:
        return ''


def read_all_seasons(new_file=False):
    player_data = read_all_players_from_csv('players.csv')
    if new_file:
        with open('seasons.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(ALL_COLUMNS)
        existing_players = set()
    else:
        with open('seasons.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            existing_players = set(row['ShortName'] for row in reader)
    for player_row in player_data:
        print(f'Player {player_row["shortname"]}')
        if player_row['shortname'] in existing_players:
            print('skip')
            continue
        r = requests.get(BASE_URL + player_row['href'])
        season_df = pd.read_html(r.text)[0]
        for c in COLUMNS:
            if c not in season_df.columns:
                season_df[c] = pd.np.nan
        season_df = season_df[COLUMNS]

        season_df['Player'] = player_row['name']
        season_df['ShortName'] = player_row['shortname']

        s = BeautifulSoup(r.text, 'lxml')
        season_df['Position'] = s.findAll(
            text=re.compile('(Guard|Forward|Point Guard|Center|Power Forward|Shooting Guard|Small Forward)')
        )[0].strip().split('\n')[0]
        season_df['Height'] = get_attr(s, 'height')
        season_df['Weight'] = get_attr(s, 'weight')
        try:
            season_df['BirthPlace'] = s.find(itemprop='birthPlace').contents[1].get_text()
        except Exception:
            season_df['BirthPlace'] = pd.np.nan
        season_df['SeasonURL'] = [get_season_href(a) for a in s.select('#per_game > tbody > tr')] + ['']
        season_df = season_df[season_df['G'] > 0]

        with open('seasons.csv', 'a') as csvfile:
            season_df.to_csv(csvfile, columns=ALL_COLUMNS, header=False, index=False)


if __name__ == "__main__":
    read_all_seasons()