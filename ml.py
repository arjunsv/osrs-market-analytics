import warnings
import requests
import urllib
import re
import time
import numpy as np
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from item_dict import * 
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

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
	if json:
		return json['selling']
	return -1

def get_current_observation(item_id):
	json = get_JSON(item_id)
	if json:
		# print(json)
		current_selling_quantity = json['sellingQuantity']
		current_buying_quantity = json['buyingQuantity']
		current_selling_price = json['selling']
		current_buying_price = json['buying']
		current_overall_price = json['overall']
		current_population = get_current_population()
		observation_vector = [current_selling_quantity, current_buying_quantity, current_selling_price, current_population]
		print(observation_vector)
		return observation_vector
	else:
		return -1

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

def remove_errors(X, y):
	indexes_X = [i for i,x in enumerate(X) if x == -1]
	for i in sorted(indexes_X, reverse=True):
		X.pop(i)
		y.pop(i)
	indexes_y = [i for i,x in enumerate(y) if x == -1]
	for j in sorted(indexes_y, reverse=True):
		X.pop(i)
		y.pop(i)

def test_remove_errors():
	X = [[1,2,3], -1, [4,5,2], -1, -1, [22,4,5]]
	y = [23, 45, -1, 666, 2254, -1]
	remove_errors(X, y)
	return X, y

def id_to_item_name(item_id):
	return id_name_dict[item_id]

def get_training_data(item_id, interval, poll_period):
	X = []
	y = []
	t_middle = time.time() + interval / 2
	t_end = time.time() + interval
	while time.time() < t_middle:
		time.sleep(poll_period)
		X.append(get_current_observation(item_id))
	while time.time() < t_end:
		time.sleep(poll_period)
		y.append(get_current_selling_price(item_id))
	make_same_length(X, y)
	remove_errors(X, y)
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
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2)
		model = model()
		model.fit(self.X_train, self.y_train)
		self.model = model
		self.y_pred = self.model.predict(self.X_test)
		print("finished initialization!")

	def get_mean_abs_error(self):
		mean_absolute_error = np.sqrt(metrics.mean_squared_error(self.y_test, self.y_pred))
		print("mean_absolute_error: " + str(mean_absolute_error))
		return mean_absolute_error

	def make_prediction(self, observation_vector):
		print("prediction_vector: " + str(observation_vector))
		y_pred = self.model.predict(observation_vector)
		print("y_pred: " + str(y_pred))
		return y_pred

	def print_attrs(self):
		print("observation_vector_count: " + str(len(self.X)))
		print("target_vector_count: " + str(len(self.y)))
		print("observation_vectors: " + str(self.X))
		print("target_vectors: " + str(self.y))

lin_reg_model = Model(6685, 7200, 15)
lin_reg_model.get_mean_abs_error()
lin_reg_model.print_attrs()
lin_reg_model.make_prediction([[10000, 6000, 6666, 60000]])













