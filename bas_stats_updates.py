import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
import json
import re
from datetime import datetime
import numpy as np
comm = re.compile("<!--|-->")

class Team: #change team player object
    
    def __init__(self, team, year, player=None):
        self.year = year
        self.team = team
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}.html".format(self.team, self.year)).text
        self.soup = BeautifulSoup(re.sub("<!--|-->","",self.team_stat),"html.parser")

    def team_sum(self, four_factor = False):
        summary_container = self.soup.find("table",id="team_misc")
        summary_table = summary_container.find("tbody")
        team_sum_row = summary_table.find_all("tr")
        dict_league_rank = {row['data-stat']:row.get_text() for row in team_sum_row[1]}
        dict_team_sum = {row['data-stat']:row.get_text() for row in team_sum_row[0]}
        del dict_team_sum['player'], dict_league_rank['player']
        df_team = pd.DataFrame(data = [dict_team_sum, dict_league_rank],index = ['TEAM','LEAGUE']).T
        for column in df_team.columns:
            try:
                df_team[column] = pd.to_numeric(df_team[column])
            except:
                pass

        if four_factor:
            off_stats = df_team.loc[['tov_pct',
                                      'pace', 'orb_pct', 'efg_pct', 'ft_rate']]
            off_stats.columns = ['Team','OFF']
            # off_stats['Team'] = off_stats['Team'].apply(lambda x: float(x))
            
            def_stats = df_team.loc[['opp_tov_pct',
                                     'pace', 'drb_pct', 'opp_efg_pct', 'opp_ft_rate']]
            def_stats.columns = ['Team','DEF']
            # def_stats['Team'] = def_stats['Team'].apply(lambda x: float(x))
            return off_stats, def_stats

        return df_team

    def roster(self, player = None):

        roster_containter = self.soup.find("tbody")
        roster_vals = roster_containter.find_all('tr')
        data_list = []
        
        for row in range(len(roster_vals)):
            table_data = roster_vals[row].find_all("td")
            data_list.append({table_data[data_row]['data-stat']
                            :table_data[data_row].get_text() for data_row in range(len(table_data))})
        
        df_roster = pd.DataFrame(data=data_list)

        if player:
            return df_roster[df_roster['player'].str.contains(player)].T
            
        return df_roster


    def injury_report(self,roster_update=False):
        injury_table = self.soup.find("table",id="injury")
        inj_body = injury_table.find("tbody")
        inj_data = inj_body.find_all("tr")
         
        df_injury = pd.DataFrame({

            "player": [inj_data[data].find("th").get_text()
                              for data in range(len(inj_data))],
            "team": [inj_data[data].find_all("td")[0].get_text() for data in range(len(inj_data))],
            "date": [inj_data[data].find_all("td")[1].get_text() for data in range(len(inj_data))],
            "description": [inj_data[data].find_all("td")[2].get_text() for data in range(len(inj_data))]
  
        })

        if roster_update == True:
            updated =  df_injury['description'].apply(lambda x: 0 if 'OUT' in x.upper().split(' ') else 1)
            df_injury.description = updated
            return df_injury

        return df_injury

    def per_game(self,player = None):
        per_game_table = self.soup.find("table", id="per_game")
        table_body = per_game_table.find("tbody")
        table_row = table_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']
                            :table_data[data_row].get_text() for data_row in range(len(table_data))})
        df_per_game = pd.DataFrame(data=data_row)
        for column in df_per_game.columns:
            try:
                df_per_game[column] = pd.to_numeric(df_per_game[column])
            except:
                pass

        if player:
            return df_per_game[df_per_game['player'].str.contains(player)].T
        
        return df_per_game
    
    def totals(self, player = None):
        totals_table = self.soup.find("table", id="totals")
        totals_body = totals_table.find("tbody")
        table_row = totals_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                             for data_row in range(len(table_data))})
        df_totals = pd.DataFrame(data=data_row)
        for column in df_totals.columns:
            try:
                df_totals[column] = pd.to_numeric(df_totals[column])
            except:
                pass

        if player:
            return df_totals[df_totals['player'].str.contains(player)].T

        return df_totals

    def per_minute(self, player = None):
        six_table = self.soup.find("table", id="per_minute")
        six_body = six_table.find("tbody")
        table_row = six_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                             for data_row in range(len(table_data))})
        df_minutes = pd.DataFrame(data=data_row)

        for column in df_minutes.columns:
            try:
                df_minutes[column] = pd.to_numeric(df_minutes[column])
            except:
                pass

        if player:
            return df_minutes[df_minutes['player'].str.contains(player)].T

        return df_minutes
    
    def per_poss(self, player = None):
        poss_table = self.soup.find("table", id="per_poss")
        poss_body = poss_table.find("tbody")
        table_row = poss_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                             for data_row in range(len(table_data))})
        df_poss = pd.DataFrame(data=data_row)
        for column in df_poss.columns:
            try:
                df_poss[column] = pd.to_numeric(df_poss[column])
            except:
                pass

        if player:
            return df_poss[df_poss['player'].str.contains(player)].T

        return df_poss

    def advanced(self, player = None):
        poss_table = self.soup.find("table", id="advanced")
        poss_body = poss_table.find("tbody")
        table_row = poss_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                             for data_row in range(len(table_data))})
        df_poss = pd.DataFrame(data=data_row)
        for column in df_poss.columns:
            try:
                df_poss[column] = pd.to_numeric(df_poss[column])
            except:
                pass

        if player:
            return df_poss[df_poss['player'].str.contains(player)].T

        return df_poss

    def shooting(self, player = None):
        shooting_table = self.soup.find("table", id="shooting")
        shooting_body = shooting_table.find("tbody")
        table_row = shooting_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                            for data_row in range(len(table_data))})
        df_shooting = pd.DataFrame(data=data_row)
        for column in df_shooting.columns:
            try:
                df_shooting[column] = pd.to_numeric(df_shooting[column])
            except:
                pass

        if player:
            return df_shooting[df_shooting['player'].str.contains(player)].T

        return df_shooting

    def pbp(self, player = None):
        pbp_table = self.soup.find("table", id="pbp")
        pbp_body = pbp_table.find("tbody")
        table_row = pbp_body.find_all("tr")
        data_row = []
        for row in range(len(table_row)):
            table_data = table_row[row].find_all("td")
            data_row.append({table_data[data_row]['data-stat']: table_data[data_row].get_text()
                            for data_row in range(len(table_data))})
        df_pbp = pd.DataFrame(data=data_row)
        for column in df_pbp.columns:
            try:
                df_pbp[column] = pd.to_numeric(df_pbp[column])
            except:
                pass

        if player:
            return df_pbp[df_pbp['player'].str.contains(player)].T

        return df_pbp

    def salaries(self, plater = None):
        salaries_table = self.soup.find("table", id="salaries2")
        salaries_body = salaries_table.find_all("tr")
        sal_dict = {salaries_body[row].find("td",class_='left').get_text():salaries_body[row].find("td",class_='right').get_text() 
        for row in range(1,len(salaries_body))}
        df_sal = pd.DataFrame(sal_dict, index=[0]).T
        for column in df_sal.columns:
            try:
                df_sal[column] = pd.to_numeric(df_sal[column])
            except:
                pass

        if player:
            return df_sal[df_sal.index.str.contains(player)].T

        return df_sal

    def leader(self):
        leader_container = self.soup.find("div",id="div_leaderboard")
        leader_table = leader_container.find_all("div")
        data_dict = {leader_table[row].find("caption",class_="poptip").get_text():leader_table[row].find("td",class_="single").get_text() 
                    for row in range(len(leader_table))}
        df_ranks = pd.DataFrame(data_dict,index=[0]).T

        return df_ranks

    def splits(self,type_split=None,split_row = None):
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}/splits".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        splits_table = self.soup.find("table", id="team_splits")
        tr_tags = splits_table.find_all("tr")
        new_dict = []
        for row in range(len(tr_tags)):
            try:
                label = tr_tags[row].find("td",class_='left').get_text()
                data = tr_tags[row].find_all('td',class_='right')
                values = {data[line]['data-stat']:data[line].get_text() for line in range(len(data))}
                new_dict.append({label:values})
            except:
                pass

        df = pd.DataFrame({key:dic[key] for dic in new_dict for key in dic})
        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass
        
        if type_split and split_row:
            return df[type_split].loc[split_row]
        elif type_split:
            return df[type_split]
        else:
            return df

    def schedule(self,date=None,game=None):
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}_games.html".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        results_table = self.soup.find("table",id="games")
        results_body = results_table.find("tbody")
        results_row = results_body.find_all("tr")
        new_dict = []
        for num in range(len(results_row)):
            try:
                td_tags = results_row[num].find_all("td")
                values = {td_tags[data]['data-stat']:td_tags[data].get_text() for data in range(len(td_tags))}
                new_dict.append(values)
            except:
                pass

        df = pd.DataFrame(data=new_dict)
        df['date_game'] = pd.to_datetime(df['date_game'],format='%a, %b %d, %Y')
        df[['opp_pts','pts']] = df[['opp_pts','pts']].apply(pd.to_numeric) 
        df['spread'] = df['pts'] - df['opp_pts']
        df.drop(labels='box_score_text',inplace=True,axis=1)
        df = df[pd.notnull(df['date_game'])]

        if game:
            return df[df['opp_name'].str.contains(game)]
        if date:
            return df[df.date_game==date]
        else:
            return df

    def game_log(self,game=None):
        #https://www.basketball-reference.com/teams/TOR/2020/gamelog/
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}/gamelog".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        game_table = self.soup.find('table',id='tgl_basic')
        table_body = game_table.find('tbody')
        tr_table = table_body.find_all('tr')
        new_dict = []
        try:
            for row in range(len(tr_table)):
                td_tags = tr_table[row].find_all('td')
                values = {td_tags[data]['data-stat']:td_tags[data].get_text() for data in range(len(td_tags))}
                new_dict.append(values)  
        except:
            pass

        df = pd.DataFrame(data=new_dict)
        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass
        df = df[pd.notnull(df['date_game'])]
        df['date_game'] = pd.to_datetime(df['date_game'],format='%Y-%m-%d')
        if game:
            return df[df['opp_id'].str.contains(game)]
        return df
    
    def lineup(self):
        #https://www.basketball-reference.com/teams/TOR/2020/lineups/
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}/lineups".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")

        lineup_table = self.soup.find_all("table")

        table_5man = []
        table_4man = []
        table_2man = []

        for table in lineup_table:
            lineup_body = table.find("tbody")
            tr_lineup = lineup_body.find_all("tr")
            for row in range(len(tr_lineup)):
                td_tags = tr_lineup[row].find_all("td")
                values = {td_tags[data]['data-stat']:td_tags[data].get_text() for data in range(len(td_tags))}
                if table['id'] == 'lineups_5-man_':
                    table_5man.append(values)
                elif table['id'] == 'lineups_3-man_':
                    table_4man.append(values)
                else:
                    table_2man.append(values)

        df_5man = pd.DataFrame(data=table_5man)
        df_4man = pd.DataFrame(data=table_4man)
        df_2man = pd.DataFrame(data=table_2man)
        return df_5man, df_4man, df_2man

    def starting_lineup(self):
        #https://www.basketball-reference.com/teams/TOR/2020_start.html
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}_start.html".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        tables = self.soup.find_all('table')
        table_starting = []
        table_summary = []
    
        for table in tables:
            lineup_body = table.find("tbody")
            tr_lineup = lineup_body.find_all("tr")
            for row in range(len(tr_lineup)):
                td_tags = tr_lineup[row].find_all("td")
                values = {td_tags[data]['data-stat']:td_tags[data].get_text() for data in range(len(td_tags))}
                if table['id'] == 'starting_lineups_po0':
                    table_starting.append(values)
                else:
                    table_summary.append(values)

        df_starting = pd.DataFrame(data=table_starting)
        df_summary = pd.DataFrame(data=table_summary)
        return df_starting, df_summary

    def on_off(self, player = None):
        #https://www.basketball-reference.com/teams/TOR/2020/on-off/
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}/on-off/".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        table_body = self.soup.find("table",id='on_off')
        table_row = table_body.find_all("tr")
        new_dict = []
        for row in range(len(table_row)):
            try:
                th_tags = table_row[row].find('th')
                if th_tags['data-append-csv'] != None:
                    player_id = th_tags['data-append-csv']
                    split_id = table_row[row].find("td",class_='left').get_text() + ' {}'.format(player_id)
                    data = table_row[row].find_all("td",class_='right')
                    values = {data[num]['data-stat']:data[num].get_text() for num in range(len(data))}
                    new_dict.append({split_id:values})
            except: pass
        
        df = pd.DataFrame({key:dic[key] for dic in new_dict for key in dic}).T
        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass
        df.reset_index(inplace=True)
        df.rename(columns = {'index':'onoff'},inplace=True)
        
        if player:
            return df[df['onoff'].str.contains(player[:5])]
        else:
            return df

    def depth_chart(self,depth_level=None):
        #https://www.basketball-reference.com/teams/TOR/2020_depth.html
        self.team_stat = requests.get(
            "https://www.basketball-reference.com/teams/{}/{}_depth.html".format(self.team, self.year)).text
        self.soup = BeautifulSoup(
            re.sub("<!--|-->", "", self.team_stat), "html.parser")
        tables = self.soup.find_all("table")
        new_dict = []
        for table in range(len(tables)):
            caption = tables[table].find("caption").get_text()
            table_row = tables[table].find('td')
            players = {'%s '%caption+player.get_text() for player in table_row.find_all('a')}
            span_tags = [tags.get_text().replace('/',',').split(',') for tags in table_row.find_all('span')]
            player_data ={player:data for player, data in zip(players,span_tags)}
            new_dict.append(player_data)
        
        df = pd.DataFrame({key:dic[key] for dic in new_dict for key in dic}).T
        df.reset_index(inplace=True)
        df.columns = ['player','minutes','pts','reb','ast','ws']
        df['minutes'] = df['minutes'].apply(lambda x: x[:-3])
        df['pts'] = df['pts'].apply(lambda x: x[:-3])
        df['reb'] = df['reb'].apply(lambda x: x[:-3])
        df['ast'] = df['ast'].apply(lambda x: x[:-3])
        df['ws'] = df['ws'].apply(lambda x: x[:-3])
        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass
        
        if depth_level:
            return df[df['player'].str.contains(depth_level)]
        else:
            return df

if __name__ == '__main__':
    team = Team('BOS',2020)
    print(team.depth_chart())

