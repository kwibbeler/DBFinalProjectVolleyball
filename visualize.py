# create the visualizations and summaries to be used in player and team scouting report

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os

# create a directory within the project to save the plots
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

# create a directory to store the teams scouting report and plots
def create_team_dir(team):
    team_dir = os.path.join(PLOTS_DIR, f"team{team.upper()}")
    os.makedirs(team_dir, exist_ok=True)
    return team_dir

# load the tables from the database into dataframes
def fetch_tables(cursor):
    df_players = pd.read_sql("SELECT * FROM players;", cursor.connection)
    df_team_a = pd.read_sql("SELECT * FROM team_a;", cursor.connection)
    df_team_b = pd.read_sql("SELECT * FROM team_b;", cursor.connection)
    
    return df_players, df_team_a, df_team_b

def player_radial_plot_hit_types(df_players_team, team, team_dir):
    hit_types = ['tip', 'roll_shot', 'free_ball', 'off_speed', 'hit', 'overpass', 'blocked']
    df_team = df_players_team.copy()
    
    N = len(hit_types)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  
    
    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    
    for _, player in df_team.iterrows():
        values = [player[f'pct_{ht}'] if player[f'pct_{ht}'] is not None else 0 for ht in hit_types]
        values += values[:1]
        ax.plot(angles, values, label=f"Player {player['jersey_number']}")
        ax.fill(angles, values, alpha=0.1)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(hit_types)
    ax.set_yticklabels([f"{int(x*100)}%" for x in ax.get_yticks()])
    plt.title(f"Hit Type Percentages - Team {team.upper()}")
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    filename = os.path.join(team_dir, f"player_{player['jersey_number']}_hit_types_team{team.upper()}.png")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"Radar plot saved as {filename}")

def team_radial_plot_hit_types(df_team, team):
    hit_types = ['tip', 'roll_shot', 'free_ball', 'off_speed', 'hit', 'overpass', 'blocked']
    df = df_team.copy()
    
    # team average hit percentage
    team_avg = df[[f'pct_{ht}' for ht in hit_types]].mean().fillna(0).tolist()
    team_avg += team_avg[:1]  
    
    N = len(hit_types)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    
    plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, team_avg, label=f"Team {team.upper()}", color='red')
    ax.fill(angles, team_avg, alpha=0.2, color='red')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(hit_types)
    ax.set_yticklabels([f"{int(x*100)}%" for x in ax.get_yticks()])
    plt.title(f"Team Average Hit Type Percentages - Team {team.upper()}")
    plt.legend()
    
    filename = os.path.join(PLOTS_DIR, f"team_radial_{team.upper()}.png")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"Team radial plot saved as {filename}")

def boxplot_stats(df_players, stat, team):
    df_team = df_players[df_players['team_name'].str.lower() == team.lower()]
    plt.figure(figsize=(8,5))
    sns.boxplot(data=df_team, y=stat)
    plt.title(f"{stat.replace('_',' ').title()} Distribution - Team {team.upper()}")
    plt.ylabel(stat.replace('_',' ').title())
    
    filename = os.path.join(PLOTS_DIR, f"boxplot_{stat}_team_{team.upper()}.png")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"Boxplot saved as {filename}")


def boxplot_team_comparison(df_team_a, df_team_b, stat, team_names):
    # unpack real team names
    team_a_name, team_b_name = team_names

    # assign team column
    df_a = df_team_a.copy()
    df_b = df_team_b.copy()
    df_a['team'] = team_a_name
    df_b['team'] = team_b_name

    # combined dataframe
    df = pd.concat([df_a, df_b], ignore_index=True)

    # make plot
    plt.figure(figsize=(8, 5))
    sns.boxplot(x='team', y=stat, data=df)
    plt.title(f"{stat.replace('_', ' ').title()} Comparison: {team_a_name} vs {team_b_name}")
    plt.ylabel(stat.replace('_', ' ').title())

    # clean filename
    filename = os.path.join(PLOTS_DIR, f"boxplot_{stat}_{team_a_name.lower()}_vs_{team_b_name.lower()}.png")

    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"Team comparison boxplot saved as {filename}")

def service_ratio_plot(df_team, team, team_dir):
    total_aces = df_team['total_service_aces'].sum()
    total_errors = df_team['total_service_errors'].sum()
    ratio = total_aces / total_errors if total_errors > 0 else 0

    plt.figure(figsize=(6,5))
    sns.barplot(x=[f"Team {team.upper()}"], y=[ratio], color='skyblue')
    plt.ylabel("Service Ace/Error Ratio")
    plt.title(f"Service Ace/Error Ratio - Team {team.upper()}")

    filename = os.path.join(team_dir, f"service_ratio_team_{team.upper()}.png")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print(f"Service ratio plot saved as {filename}")


def create_scouting_report(df_players, team, team_dir):
    df_team = df_players[df_players['team_name'].str.lower() == team.lower()]
    
    report_filename = os.path.join(team_dir, f"scouting_report_team_{team.upper()}.txt")
    with open(report_filename, "w") as f:
        f.write(f"Scouting Report - Team {team.upper()}\n")
        f.write("="*50 + "\n\n")
        f.write(f"Number of players: {len(df_team)}\n\n")
        
        for _, player in df_team.iterrows():
            f.write(f"Player {player['jersey_number']}:\n")
            f.write(f"  Total Hits: {player.get('total_hits', 0)}\n")
            f.write(f"  Total Kills: {player.get('total_kills', 0)}\n")
            f.write(f"  Total Hit Errors: {player.get('total_hit_errors', 0)}\n")
            f.write(f"  Hitting Efficiency: {player.get('hitting_efficiency', 0):.2f}\n")
            f.write(f"  Total Service Aces: {player.get('total_service_aces', 0)}\n")
            f.write(f"  Total Service Errors: {player.get('total_service_errors', 0)}\n")
            f.write(f"  Service Ace/Error Ratio: {player.get('service_ace_ratio', 0):.2f}\n")
            f.write("  Hit Type Percentages:\n")
            hit_types = ['tip', 'roll_shot', 'free_ball', 'off_speed', 'hit', 'overpass', 'blocked']
            for ht in hit_types:
                pct = player.get(f'pct_{ht}', 0)
                f.write(f"    {ht}: {pct:.2f}\n")
            f.write("\n")
        
        f.write("Plots included:\n")
        f.write(f"  Radar plot: radar_team_{team.upper()}.png\n")
        f.write(f"  Service ratio: service_ratio_team_{team.upper()}.png\n")
    
    print(f"Scouting report saved as {report_filename}")

def generate_visuals_and_scouting_report(df_players, team_tables):
    
    for team, df_team in team_tables.items():
        print(f"Generating visuals and report for Team {team.upper()}...")
        
        # extract players for current team
        df_players_team = df_players[df_players['team_name'].str.lower() == team.lower()]
        
        team_dir = create_team_dir(team)
        # player hit type radial plot
        player_radial_plot_hit_types(df_players_team, team, team_dir)
        
        # service ace/error ratio plot
        service_ratio_plot(df_team, team, team_dir)
        
        # team hit type radial plot
        team_radial_plot_hit_types(df_team, team)
        
        # boxplots for player stats
        for stat in ['hitting_efficiency', 'total_kills', 'total_hits']:
            boxplot_stats(df_players_team, stat, team)
        
        # create scouting report
        create_scouting_report(df_players_team, team, team_dir)
        
        print(f"Completed visuals and report for Team {team.upper()}\n")
    
    # create comparison boxplots if have stats for more than one team
    if len(team_tables) >= 2:
        stats_to_compare = ['hitting_efficiency', 'total_kills', 'total_hits']
        team_names = list(team_tables.keys())
        
        for stat in stats_to_compare:
            dfs = [df_players[df_players['team_name'].str.lower() == t] for t in team_names]
            boxplot_team_comparison(*dfs, stat, team_names)
    
    print("All visuals and scouting reports generated!")

