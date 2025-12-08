# CSCI 403 Database Final Project

## Project Description
The goal of this project is to explore and analyze volleyball team and player performance data using SQL and Python. Our objective is to create a comprehensive system that automatically generates **player and team scouting reports**, visualizations, and comparisons that are useful for coaches, analysts, and players. 

This project demonstrates a synthesis of database querying, data cleaning, statistical analysis, and visualization techniques learned in CSCI 403. By combining player-level and team-level data, we can quickly identify trends, strengths, and areas for improvement.

Specifically, the project aims to:

- Summarize **player-level statistics** (total hits, kills, errors, and hitting efficiency)
- Calculate **team-level summaries** (total service aces, errors, and ratios)
- Visualize **hit type distributions** for players and teams using radial plots
- Compare **hitting efficiency** across teams with side-by-side boxplots
- Generate organized **scouting reports** that integrate textual summaries with visualizations

---

## Features

### Player-Level Visuals
- Radial plots showing hit type percentages for each player
- Player statistics including:
  - Total hits
  - Total kills
  - Total hit errors
  - Hitting efficiency

### Team-Level Visuals
- Radial plots showing average hit type percentages for each team
- Service ace/error ratio bar plots
- Side-by-side boxplots comparing hitting efficiency between teams

#### Example Radial Plot
![Team A Hit Type Distribution](plots/teamA/hit_types_teamA.png)  

---

### Scouting Reports
- Summarized player and team statistics
- Team totals and averages
- Hit type percentages for each player and team
- References to generated plots for easy access

#### Sample Team Summary Statistics
- Team Summary Statistics:
- Total Hits: 432
- Total Kills: 210
- Total Hit Errors: 45
- Average Hitting Efficiency: 0.39
- Total Service Aces: 25
- Total Service Errors: 12
- Service Ace/Error Ratio: 2.08

- Hit Type Percentages:
- tip: 0.12
- roll_shot: 0.08
- free_ball: 0.05
- off_speed: 0.07
- hit: 0.52
- overpass: 0.10
- blocked: 0.06

---

## Data Source
The project uses three SQL tables:

1. **players** – player-level statistics such as hits, kills, hit errors, hitting efficiency, and hit type percentages  
2. **team_a** – team-level statistics such as service aces and service errors  
3. **team_b** – team-level statistics such as service aces and service errors  

---

## Setup and Running the Project
1. Clone the repository:
```bash
git clone https://github.com/kwibbeler/DBFinalProjectVolleyball
cd DBFinalProjectVolleyball
```

2. Create Virtual Environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install Dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Database Connection
Modify `main.py` to point to your database connection.

5. Run the script to generate visuals and scouting reports:
```bash
python `main.py`
```

Output:

- Plots saved in plots/ directory
- Scouting reports saved in plots/teamA/ and plots/teamB/

---

## Project Structure

```text
├── main.py                 
├── visualize.py             
├── database_setup.sql      
├── plots/                   
│   ├── teamA/
│   └── teamB/
├── README.md               
└── requirements.txt    
```   

---

## Dependencies

- Python 3.12+
- pandas
- numpy
- matplotlib
- seaborn
- SQL database connection