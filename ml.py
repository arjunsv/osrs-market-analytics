import requests
import urllib
import re
import time
from bs4 import BeautifulSoup


def get_JSON(itemId):
	json = requests.get("https://api.rsbuddy.com/grandExchange?a=guidePrice&i="+str(itemId)).json()
	return json

def get_current_selling_quantity(item_id):
	return get_JSON(itemId)['sellingQuantity']

def get_current_buying_quantity(item_id):
	return get_JSON(itemId)['buyingQuantity']

def get_current_selling_price(item_id):
	return get_JSON(itemId)['selling']

def get_current_buying_price(item_id):
	return get_JSON(itemId)['buying']

def get_current_overall_price(item_id):
	return get_JSON(itemId)['overall']

def get_current_population():
	page = urllib.request.urlopen("http://oldschool.runescape.com/")
	soup = BeautifulSoup(page, 'html.parser')
	population_text = soup.find('p', attrs={'class': 'player-count'}).text.strip()
	population_count = int(re.search('(\d+)',population_text).group(1))
	return population_count

def get_observation_vector(item_id):
	return [get_current_population(), get_current_selling_quantity(itemId), get_current_selling_price(itemId)]


def get_training_data(item_id, interval, poll_period):
	X = []
	y = []
	
	t_middle = time.time() + 60 * interval / 2
	t_end = time.time() + 60 * interval
	while time.time() < t_middle:
		time.sleep(poll_interval)


	return


