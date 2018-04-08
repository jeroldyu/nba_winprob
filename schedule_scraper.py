"""
schedule_scraper.py
--------------------------------------
This program extracts game scores from basketball-reference.com.
"""

## LIBRARIES ##
import csv
import urllib2
from bs4 import BeautifulSoup

## CONSTANTS ##
BASE_URL = 'https://www.basketball-reference.com'
START_YR = 2007
END_YR = 2017
TEAMS = {'Atlanta Hawks': 'ATL', 'Boston Celtics': 'BOS', 'New Jersey Nets': 'NJN',
		 'Charlotte Bobcats': 'CHA', 'Chicago Bulls': 'CHI', 'Cleveland Cavaliers': 'CLE',
		 'Dallas Mavericks': 'DAL', 'Denver Nuggets': 'DEN', 'Detroit Pistons': 'DET',
		 'Golden State Warriors': 'GSW', 'Houston Rockets': 'HOU', 'Indiana Pacers': 'IND',
		 'Los Angeles Clippers': 'LAC', 'Los Angeles Lakers': 'LAL', 'Memphis Grizzlies': 'MEM',
		 'Miami Heat': 'MIA', 'Milwaukee Bucks': 'MIL', 'Minnesota Timberwolves': 'MIN',
		 'New Orleans/Oklahoma City Hornets': 'NOK', 'New York Knicks': 'NYK',
		 'Seattle SuperSonics': 'SEA', 'Orlando Magic': 'ORL', 'Philadelphia 76ers': 'PHI',
		 'Phoenix Suns': 'PHO', 'Portland Trail Blazers': 'POR', 'Sacramento Kings': 'SAC',
		 'San Antonio Spurs': 'SAS', 'Toronto Raptors': 'TOR', 'Utah Jazz': 'UTA',
		 'Washington Wizards': 'WAS', 'New Orleans Hornets': 'NOH', 'Oklahoma City Thunder': 'OKC',
		 'Brooklyn Nets': 'BRK', 'New Orleans Pelicans': 'NOP', 'Charlotte Hornets': 'CHO'}
MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']


# Contains the rows that will eventually be written into the CSV file.
GAMES = []


"""
Parameters:
* score: extracted home/away score for a game.

Function: helper function to determine if a score is valid (i.e. the game has been played).
"""
def validate_score(score):
	return int(score) if score != '' else -1

"""
Parameters:
* url: url that contains game scores in a given month.

Function: Extracts game scores for a given month.
"""
def parse_games(url):
	
	# Parse page containing team's splits page.
	response = urllib2.urlopen(url)
	response_soup = BeautifulSoup(response, 'html.parser')	

	# Find table that includes the schedule and all games; loop through games
	schedule_soup = BeautifulSoup(str(response_soup.select_one('table[id="schedule"]')), 'html.parser')
	for row in schedule_soup.select('tbody > tr'):

		row_soup = BeautifulSoup(str(row), 'html.parser')
		if row_soup.select_one('tr[class="thead"]') is not None: break	# Stop when playoffs start
		
		# Extracted desired features.
		day = row_soup.select_one('th').get_text()[5:]
		away = TEAMS[row_soup.select_one('td[data-stat="visitor_team_name"]').get_text()]
		home = TEAMS[row_soup.select_one('td[data-stat="home_team_name"]').get_text()]
		away_score = validate_score(row_soup.select_one('td[data-stat="visitor_pts"]').get_text())
		home_score = validate_score(row_soup.select_one('td[data-stat="home_pts"]').get_text())

		GAMES.append([day, away, home, away_score, home_score])



"""
Function: Export the data in GAMES into a CSV file.
"""
def export_stats():

	filename = 'games.csv'
	
	print 'Exporting data to ' + filename + '...'

	file_handle = open(filename, 'w')
	writer = csv.writer(file_handle)
	writer.writerow(['day', 'away', 'home', 'away_score', 'home_score'])
	writer.writerows(GAMES)

	print 'Success.'



def main():

	print """
	Running web scraper for single-game win probability model. All data scraped from basketball-reference.com.
	Scraped data starts from the 2006-2007 NBA season, and includes final scores from every regular season game.
	"""

	try:
		# Loop through each season
		for year in xrange(START_YR, END_YR + 1):

			# Code to check for lockout year, when season started in December
			months = MONTHS
			if year == 2012: months = MONTHS[2:]

			print 'LOOPING THROUGH ' + str(year-1) + '-' + str(year) + ' SEASON.'

			# Loop through each month of regular season
			for month in months:
				url = BASE_URL + '/leagues/NBA_' + str(year) + '_games-' + month + '.html'
				parse_games(url)	# Extract data
				
				print 'Parsed games in the month of ' + month[0].upper() + month[1:] + ' successfully.'

	except Exception as e:
		print 'ERROR You encountered an error. Terminating program and exporting data to csv file.'
		print str(e)

	finally:
		export_stats()
		print 'Exiting program.'


if __name__ == '__main__':
	main()
