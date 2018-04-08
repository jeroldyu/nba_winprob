"""
splits_scraper.py
--------------------------------------
This program scrapes home/road splits for each NBA team. All data is scraped from
basketball-reference.com.
"""

## LIBRARIES ##
import csv
import urllib2
from bs4 import BeautifulSoup

## CONSTANTS ##
BASE_URL = 'https://www.basketball-reference.com'
START_YR = 2007
END_YR = 2017
TEAM_ABBR = ['ATL', 'BOS', 'NJN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
			 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOK', 'NYK',
			 'SEA', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

# Contains the rows that will eventually be written into the CSV file.
HOME = []
AWAY = []

## HELPER FUNCTIONS ##
# Calculate features based on given data.
def calc_win_pct(wins, g):
	return round(1. * wins / g, 3)

def calc_fg3_pct(fg3, fg3a):
	return round(1. * fg3 / fg3a, 3)	

def calc_ts_pct(pts, fga, fta):
	return round(1. * pts / (2 * (fga + 0.44 * fta)), 3)	

def calc_efg_pct(fg, fg3, fga):
	return round(1. * (fg + 0.5 * fg3) / fga, 3)	

def calc_tov_pct(tov, fga, fta):
	return round(100. * tov / (fga + 0.44 * fta + tov), 1)

# Make appropriate changes to TEAM_ABBR.
def change_abbr(year):	
	if year == 2008: TEAM_ABBR[TEAM_ABBR.index('NOK')] = 'NOH'
	elif year == 2009: TEAM_ABBR[TEAM_ABBR.index('SEA')] = 'OKC'
	elif year == 2013: TEAM_ABBR[TEAM_ABBR.index('NJN')] = 'BRK'
	elif year == 2014: TEAM_ABBR[TEAM_ABBR.index('NOH')] = 'NOP'
	elif year == 2015: TEAM_ABBR[TEAM_ABBR.index('CHA')] = 'CHO'



"""
Parameters:
* soup: HTML parser for the home/road stats for a team's splits page.
* year: current season being parsed.
* team: current team being parsed.

Function: Extract data from row and return features that will be written into CSV file.
"""
def get_stats(soup, year, team):

	# Team stats
	g = int(soup.select_one('td[data-stat="g"]').get_text())
	wins = int(soup.select_one('td[data-stat="wins"]').get_text())
	fg = float(soup.select_one('td[data-stat="fg"]').get_text()) * g
	fga = float(soup.select_one('td[data-stat="fga"]').get_text()) * g
	fg3 = float(soup.select_one('td[data-stat="fg3"]').get_text()) * g
	fg3a = float(soup.select_one('td[data-stat="fg3a"]').get_text()) * g
	fta = float(soup.select_one('td[data-stat="fta"]').get_text())
	ast = float(soup.select_one('td[data-stat="ast"]').get_text())
	pts = float(soup.select_one('td[data-stat="pts"]').get_text())

	# Stats derived from team stats
	win_pct = calc_win_pct(wins, g)
	fg3_pct = calc_fg3_pct(fg3, fg3a)
	ts_pct = calc_ts_pct(pts * g, fga, fta * g)

	# Opponent stats
	ofg = float(soup.select_one('td[data-stat="opp_fg"]').get_text()) * g
	ofga = float(soup.select_one('td[data-stat="opp_fga"]').get_text()) * g
	ofg3 = float(soup.select_one('td[data-stat="opp_fg3"]').get_text()) * g
	ofta = float(soup.select_one('td[data-stat="opp_fta"]').get_text()) * g
	otov = float(soup.select_one('td[data-stat="opp_tov"]').get_text()) * g
	opts = float(soup.select_one('td[data-stat="opp_pts"]').get_text())

	# Stats derived from opponent stats
	oefg_pct = calc_efg_pct(ofg, ofg3, ofga)
	otov_pct = calc_tov_pct(otov, ofga, ofta)
	
	mov = round(pts - opts, 2)

	return [year, team, win_pct, fg3_pct, ts_pct, fta, ast, oefg_pct, otov_pct, mov]



"""
Parameters:
* url: url that contains team splits for given season.
* year: current season being parsed.
* team: current team being parsed.

Function: Extract home/road splits for team in a given season.
"""
def get_splits(url, year, team):
	
	# Parse page containing team's splits page.
	response = urllib2.urlopen(url)
	response_soup = BeautifulSoup(response, 'html.parser')

	# Find table containing team's home and road splits.
	splits_soup = BeautifulSoup(str(response_soup.select_one('table[id="team_splits"]')), 'html.parser')
	home_soup = BeautifulSoup(str(splits_soup.select('tr')[4]), 'html.parser')
	road_soup = BeautifulSoup(str(splits_soup.select('tr')[5]), 'html.parser')

	# Extract home/road data.
	HOME.append(get_stats(home_soup, year, team))
	print 'Home splits for ' + team + ' successfully extracted.'

	AWAY.append(get_stats(road_soup, year, team))
	print 'Road splits for ' + team + ' successfully extracted.'


"""
Parameters:
* filename: name of CSV file that data will be exported onto.
* stats: either HOME OR AWAY

Function: Export the data in PLAYER_STATS into a CSV file.
"""
def export_stats(filename, stats):
	
	print 'Exporting data to ' + filename + '...'

	file_handle = open(filename, 'w')
	writer = csv.writer(file_handle)
	writer.writerow(['year', 'team', 'win_pct', 'fg3_pct', 'ts_pct', 'fta', 'ast',
					 'oefg_pct', 'otov_pct', 'mov'])
	writer.writerows(stats)

	print 'Success.'	



def main():

	print """
	Running web scraper for single-game win probability model. All data scraped from basketball-reference.com.
	Scraped data starts from the 2006-2007 NBA season, and includes home and road splits for each team.
	"""

	try:
		# Loop through each season
		for year in xrange(START_YR, END_YR + 1):

			print 'LOOPING THROUGH ' + str(year-1) + '-' + str(year) + ' SEASON.'
			change_abbr(year)	# Make changes to abbreviations array if necessary

			# Loop through each team for particular season
			for team in TEAM_ABBR:

				print 'Getting splits for ' + team + '.'
				url = BASE_URL + '/teams/' + team + '/' + str(year) + '/splits/'
				get_splits(url, year, team)

	except Exception as e:
		print 'ERROR You encountered an error. Terminating program and exporting data to csv file.'
		print str(e)

	finally:
		export_stats('home.csv', HOME)
		export_stats('away.csv', AWAY)
		print 'Exiting program.'


if __name__ == '__main__':
	main()
