import requests
import urllib
import re
import time
import numpy as np
from bs4 import BeautifulSoup
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_JSON(item_id):
	try:
		json = requests.get("https://api.rsbuddy.com/grandExchange?a=guidePrice&i="+str(item_id)).json()
		return json
	except:
		print("Error in JSON request")
		return {}

def get_current_population():
	page = urllib.request.urlopen("http://oldschool.runescape.com/")
	soup = BeautifulSoup(page, 'html.parser')
	population_text = soup.find('p', attrs={'class': 'player-count'}).text.strip()
	population_count = int(re.search('(\d+)',population_text).group(1))
	return population_count

def get_current_selling_price(item_id):
	json = get_JSON(item_id)
	return json['selling']

def training_data_to_csv(item_id, X, y):
	df = pd.DataFrame(X)
	df.columns = ['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population']
	df['price_half_interval'] = y
	df.insert(loc=0, column='item_id', value=[item_id]*len(y))
	df.to_csv("training_data.csv", )

def make_same_length(X, y):
	while len(y) < len(X):
		X.pop()
	while len(X) < len(y):
		y.pop()

def get_training_data(item_id, interval, poll_period):
	X = []
	y = []
	t_middle = time.time() + interval / 2
	t_end = time.time() + interval
	json = get_JSON(item_id)

	current_selling_quantity = json['sellingQuantity']
	current_buying_quantity = json['buyingQuantity']
	current_selling_price = json['selling']
	current_buying_price = json['buying']
	current_overall_price = json['overall']
	current_population = get_current_population()

	while time.time() < t_middle:
		time.sleep(poll_period)
		X.append([current_selling_quantity, current_buying_quantity, 
			      current_selling_price, current_population])

	while time.time() < t_end:
		time.sleep(poll_period)
		y.append(get_current_selling_price(item_id))
	make_same_length(X, y)
	training_data_to_csv(item_id, X, y)
	return X, y

# currently hardcoded to lin_reg, will fix to accomodate all relevant of models

class Model:
	def __init__(self, item_id, interval, poll_period, model=LinearRegression):
		print("Initalizing model for item " + "id=" + str(item_id) + " over interval " +
			  str(interval) + " with poll period of " + str(poll_period) + " using " + str(model) + " model" + "...")
		self.item_id = item_id
		self.interval = interval
		self.poll_period = poll_period
		self.X, self.y = get_training_data(item_id, interval, poll_period)
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.4)
		model = model()
		model.fit(self.X_train, self.y_train)
		self.model = model
		self.y_pred = self.model.predict(self.X_test)
		print("finished initialization!")


	def get_mean_abs_error(self):
		mean_absolute_error = np.sqrt(metrics.mean_squared_error(self.y_test, self.y_pred))
		print("mean_absolute_error is " + str(mean_absolute_error))
		return mean_absolute_error

	def make_prediction(self, observation_vector):
		y_pred = self.model.predict(observation_vector)
		print("y_pred is " + str(y_pred))
		return y_pred

lin_reg_model = Model(6685, 7200, 20)
lin_reg_model.get_mean_abs_error()
lin_reg_model.make_prediction([[10000, 6000, 6666, 60000]])













