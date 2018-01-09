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
import os.path
import seaborn as sns
import matplotlib.pyplot as plt
from util_functions import *

class Model:
	def __init__(self, item_id, interval, poll_period, model=LinearRegression):
		print_bold("Initializing model for item " + "id=" + str(item_id) + " ~" + id_to_item_name(item_id) + "~" + " over interval " +
			  str(interval) + " with poll period of " + str(poll_period) + " using " + str(model) + " model" + "...")
		self.item_id = item_id
		self.interval = interval
		self.poll_period = poll_period
		self.observation_time_list = []
		self.y_time_list = []
		self.new_y_time_list = []
		self.X, self.y = self.get_training_data()
		self.training_data_to_csv()
		self.X, self.y = self.get_cumul_training_data()
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2)
		model = model()
		model.fit(self.X_train, self.y_train)
		self.model = model
		self.y_pred = self.model.predict(self.X_test)
		print_blue_bold("Finished initialization!")

	def get_mean_abs_error(self):
		mean_absolute_error = metrics.mean_absolute_error(self.y_test, self.y_pred)
		print("mean_absolute_error: " + str(mean_absolute_error))
		return mean_absolute_error

	def get_explained_variance(self):
		explained_variance = metrics.explained_variance_score(self.y_test, self.y_pred)
		print("explained_variance_score: " + str(explained_variance))

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
		print("interval_of_prediction: " + str(self.interval/2))
		self.get_explained_variance()
		self.get_mean_abs_error()

	def get_current_population(self):
		page = urllib.request.urlopen("http://oldschool.runescape.com/")
		soup = BeautifulSoup(page, 'html.parser')
		population_text = soup.find('p', attrs={'class': 'player-count'}).text.strip()
		population_count = int(re.search('(\d+)',population_text).group(1))
		return population_count

	def get_current_selling_price(self, item_id):
		json = get_JSON(item_id)
		if json:
			selling = json['selling']
			print(str(selling) + " retrieved at time: " + str(self.y_time_list[-1]))
			return selling
		return -1

	def get_current_observation(self, item_id):
		json = get_JSON(item_id)
		if json:
			# print(json)
			current_selling_quantity = json['sellingQuantity']
			current_buying_quantity = json['buyingQuantity']
			current_selling_price = json['selling']
			current_buying_price = json['buying']
			current_overall_price = json['overall']
			current_population = self.get_current_population()
			observation_vector = [current_selling_quantity, current_buying_quantity, current_selling_price, current_population]
			print(str(observation_vector) + " retrieved at time: " + str(self.observation_time_list[-1]))
			return observation_vector
		else:
			return -1

	def time_align(self, y):
		print_blue_bold("Aligning y-vector values to correct observation vectors...")
		new_y = []
		for obs_time in self.observation_time_list:
			new_y.append(self.get_best_y(obs_time, y))
		return new_y

	def get_best_y(self, obs_time, y):
		lambda_over_2 = self.interval/2
		for y_time in self.y_time_list:
			expected_y_time = obs_time + lambda_over_2
			closest_y_time_index = index_binary_search(self.y_time_list, expected_y_time, 0, len(self.y_time_list)-1)
			closest_y_time = self.y_time_list[closest_y_time_index] 
			self.new_y_time_list.append(closest_y_time)
			if abs(closest_y_time - expected_y_time)/expected_y_time > 0.2:
				return -1
			return y[closest_y_time_index]

	def make_same_length(self, X, y):
		while len(y) < len(X):
			X.pop()
		while len(X) < len(y):
			y.pop()

	def remove_errors(self, X, y):
		error_count = 0
		print_blue_bold("Removing anomalies...")
		indexes_X = [i for i,x in enumerate(X) if x == -1]
		for i in sorted(indexes_X, reverse=True):
			X.pop(i)
			y.pop(i)
			self.observation_time_list.pop(i)
			self.new_y_time_list.pop(i)
			error_count += 1
		indexes_y = [i for i,x in enumerate(y) if x == -1]
		for j in sorted(indexes_y, reverse=True):
			X.pop(i)
			y.pop(i)
			self.observation_time_list.pop(i)
			self.new_y_time_list.pop(i)
			error_count += 1
		print_green(str(error_count) + " errors removed.")

	def get_training_data(self):
		X = []
		y = []
		t_middle = time.time() + self.interval / 2
		t_end = time.time() + self.interval
		print_blue_bold("Gathering observation vectors...")
		print("[current_selling_quantity, current_buying_quantity, current_selling_price, current_population]")
		while time.time() < t_middle:
			self.observation_time_list.append(time.time())
			X.append(self.get_current_observation(self.item_id))
			time.sleep(self.poll_period)
		print_blue_bold("Gathering target values...")
		print("[selling_price]")
		while len(y) < len(X):
			self.y_time_list.append(time.time())
			y.append(self.get_current_selling_price(self.item_id))
			time.sleep(self.poll_period)
		y = self.time_align(y)
		self.make_same_length(X, y)
		self.remove_errors(X, y)
		return X, y

	def training_data_to_csv(self):
		file_name = str(self.item_id) + "_" + str(self.interval) + "_training_data.csv"
		df = pd.DataFrame(self.X)
		df.columns = ['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population']
		df['price_half_interval'] = self.y
		df.insert(loc=0, column='item_id', value=[self.item_id]*len(self.y))
		df.insert(loc=len(df.columns), column='obs_time', value=self.observation_time_list)
		df.insert(loc=len(df.columns), column='y_time', value=self.new_y_time_list)
		if os.path.exists(file_name):
			temp_df = pd.read_csv(file_name, index_col=0)
			temp_df = temp_df.append(df, ignore_index=True)
			temp_df.to_csv(file_name, index=True)
		else:
			df.to_csv(file_name, index=True)

	def get_cumul_training_data(self):
		file_name = str(self.item_id) + "_" + str(self.interval) + "_training_data.csv"	
		self.dataframe_total = pd.read_csv(file_name)
		dataframe_observations = self.dataframe_total[['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population']]
		all_y_values = self.dataframe_total["price_half_interval"].values
		all_observation_list = dataframe_observations.values
		return all_observation_list, all_y_values

	def show_plots(self):
		plot = sns.pairplot(self.dataframe_total, x_vars=['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population'], y_vars="price_half_interval", size=7, aspect=0.7, kind='reg')
		plt.show()


lin_reg_model = Model(6685, 25, 2)
lin_reg_model.print_attrs()
lin_reg_model.make_prediction([[10000, 6000, 6666, 60000]])
lin_reg_model.show_plots()











