import pandas as pd


def height_to_cm(h):
    ft, inch = h.split('-')
    inch = int(inch) + int(ft) * 12
    return round(inch * 2.54, 1)


def remove_lb(w):
    return int(w.replace('lb', ''))


def get_position_matrix(position):
    positions = [0, 0, 0, 0, 0]
    if 'Point Guard' in position:
        positions[0] = 1
    if 'Shooting Guard' in position:
        positions[1] = 1
    if 'Small Forward' in position:
        positions[2] = 1
    if 'Power Forward' in position:
        positions[3] = 1
    if 'Center' in position:
        positions[4] = 1
    if 'Guard' in position and 'Point Guard' not in position and 'Shooting Guard' not in position:
        positions[0] = 1
        positions[1] = 1
    if 'Forward' in position and 'Power Forward' not in position and 'Small Forward' not in position:
        positions[2] = 1
        positions[3] = 1
    return positions


def get_score(row):
    """
    Field Goals Made (FGM)         1.5​
    Field Goals Attempted (FGA) ​   -0.5​
    Free Throws Made (FTM)​         1​
    Free Throws Attempted (FTA)​    -0.75​
    Three Pointers Made (3PM)​      1​
    Three Pointers Attempted (3PA)​ -0.25​
    Offensive Rebounds (OREB)​      0.5​
    Rebounds (REB)​                 1​
    Assists (AST)​                  2​
    Steals (STL)​                   2.5​
    Blocks (BLK)​                   2.5​
    Turnovers (TO)​                 -1.75​
    Points (PTS)​                   1​


    """
    return row['FG'] * 1.5 + row['FGA'] * (-0.5) + row['FT'] + row['FTA'] * (-0.75) + row['3P'] + \
        row['3PA'] * (-0.25) + row['ORB'] * 0.5 + row['TRB'] + row['AST'] * 2 + row['STL'] * 2.5 + \
        row['BLK'] * 2.5 + row['TOV'] * (-1.75) + row['PTS']


def get_clear_seasons_data(seasons_csv='seasons.csv', with_labels=False):
    df = pd.read_csv(seasons_csv)
    df.drop(df[df.duplicated(['ShortName', 'Season'], keep='first')].index, inplace=True)
    df.drop(df[df.Lg == 'ABA'].index, inplace=True)
    df.drop(df[df.Lg == 'BAA'].index, inplace=True)
    df.drop(df[df.Lg == 'TOT'].index, inplace=True)
    df.drop(df[df.Season == 'Career'].index, inplace=True)

    # replace position with numeric values

    position_matrix = []
    for i, season_row in df.iterrows():
        position_matrix.append(get_position_matrix(season_row['Position']))
    position_matrix = pd.np.array(position_matrix)
    for i, position in enumerate(['PG', 'SG', 'SF', 'PF', 'C']):
        df['plays_' + position] = position_matrix[:, i]

    # calculate season average score

    df['Score'] = df.apply(get_score, axis=1)

    # replace season string with numeric value
    min_season = int(df['Season'].min().split('-')[0])

    def get_season(row):
        return int(row['Season'].split('-')[0]) - min_season

    df['Season_Numeric'] = df.apply(get_season, axis=1)

    # find next season score - the target column
    df.sort_values(['ShortName', 'Season_Numeric'], inplace=True)
    g = df.groupby(['ShortName'])
    next_season_score = list()
    for i, gr in g:
        next_season_score += list(gr['Score'].shift(-1))
    df['Next_Season_Score'] = next_season_score
    df.dropna(subset=['Next_Season_Score'], inplace=True)

    # drop unnecessary columns
    df.drop(columns=['BirthPlace', 'Season', 'Position', 'SeasonURL', 'Lg'], inplace=True)
    if not with_labels:
        df.drop(columns=['Player'], inplace=True)
    # drop players before 3P use
    df.dropna(subset=['3P', '3PA'], inplace=True)
    # drop players without info for Games Started
    df.dropna(subset=['GS'], inplace=True)
    # drop players with no height-weight info
    df.dropna(subset=['Height', 'Weight'], inplace=True)
    df['Height'] = df['Height'].map(height_to_cm)
    df['Weight'] = df['Weight'].map(remove_lb)
    df.fillna(0, inplace=True)
    df.reset_index(inplace=True)
    df.drop(['index'], axis=1, inplace=True)
    return df


def get_clear_final_data(seasons_csv='seasons.csv', with_labels=False):
    df = get_clear_seasons_data(seasons_csv, with_labels=with_labels)
    df.drop(columns=['ShortName', 'Pos', 'Tm', 'Score'], inplace=True)
    return df


def get_train_test_datasets(df):
    max_season = df['Season_Numeric'].max()
    df_train = df[df['Season_Numeric'] != max_season]
    df_test = df[df['Season_Numeric'] == max_season]
    X_train = df_train.drop(columns=['Next_Season_Score'])
    y_train = df_train['Next_Season_Score']
    X_test = df_test.drop(columns=['Next_Season_Score'])
    y_test = df_test['Next_Season_Score']
    return X_train, X_test, y_train, y_test
