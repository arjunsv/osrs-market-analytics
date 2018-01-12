import sys
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
	def __init__(self, item_id, interval, poll_period, csv_only, model=LinearRegression):
		print("==============================================================================================="*2)
		print_bold("Initializing model for item " + "id=" + str(item_id) + " ~" + id_to_item_name(item_id) + "~" + " over interval " +
			  str(interval) + " (seconds)" + " with poll period of " + str(poll_period) + " (seconds)" " using " + str(model) + " model" + "...")
		print("==============================================================================================="*2)
		self.item_id = item_id
		self.interval = interval
		self.poll_period = poll_period
		self.csv_only = csv_only
		self.observation_time_list = []
		self.y_time_list = []
		self.new_y_time_list = []
		self.anchor_price = self.get_current_selling_price(self.item_id, True)
		if self.anchor_price == -1:
			print_red_bold_nl("Unable to initialize model due to API request failure.")
			sys.exit()
		if not csv_only:
			self.X, self.y = self.get_new_training_data()
			self.training_data_to_csv()
		self.X, self.y = self.get_cumul_training_data()
		self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2)
		model = model()
		model.fit(self.X_train, self.y_train)
		self.model = model
		self.y_pred = self.model.predict(self.X_test)
		print_blue_bold("Finished initialization!")

	def get_new_training_data(self):
		X = []
		y = []
		t_middle = time.time() + self.interval / 2
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
			y.append(self.get_ratio_anchor_val(self.get_current_selling_price(self.item_id, False)))
			time.sleep(self.poll_period)
		y = self.time_align_vectors(y)
		self.make_same_length(X, y)
		self.remove_errors(X, y)
		return X, y

	def get_current_population(self):
		page = urllib.request.urlopen("http://oldschool.runescape.com/")
		soup = BeautifulSoup(page, 'html.parser')
		population_text = soup.find('p', attrs={'class': 'player-count'}).text.strip()
		population_count = int(re.search('(\d+)',population_text).group(1))
		return population_count

	def get_current_selling_price(self, item_id, is_anchor):
		json = get_JSON(item_id)
		if json:
			selling = json['selling']
			if not is_anchor:
				print(str(self.get_ratio_anchor_val(selling)) + " retrieved at time: " + str(self.y_time_list[-1]))
			return selling
		return -1

	def get_current_observation(self, item_id):
		json = get_JSON(item_id)
		if json:
			# print(json)
			current_selling_quantity = json['sellingQuantity']
			current_buying_quantity = json['buyingQuantity']
			current_selling_to_anchor_ratio = self.get_ratio_anchor_val(json['selling'])
			current_buying_price = json['buying']
			current_overall_price = json['overall']
			current_population = self.get_current_population()
			observation_vector = [current_selling_quantity, current_buying_quantity, current_selling_to_anchor_ratio, current_population]
			if not self.csv_only:
				print(str(observation_vector) + " retrieved at time: " + str(self.observation_time_list[-1]))
			return observation_vector
		else:
			return -1

	def time_align_vectors(self, y):
		print_blue_bold("Aligning y-vector values to correct observation vectors...")
		new_y = []
		for obs_time in self.observation_time_list:
			new_y.append(self.get_optimal_y(obs_time, y))
		return new_y

	def get_optimal_y(self, obs_time, y):
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
		print_blue_bold("Removing anomalies...")
		error_count = 0
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
		print(str(error_count) + " errors removed.")

	def get_ratio_anchor_val(self, price):
		return price/self.anchor_price

	def training_data_to_csv(self):
		print_blue_bold("Exporting to csv...")
		file_name = str(self.item_id) + "_" + str(self.interval) + "_training_data.csv"
		df = pd.DataFrame(self.X)
		df.columns = ['current_selling_quantity', 'current_buying_quantity', 'current_selling_to_anchor_ratio', 'current_population']
		df['target_selling_to_anchor_ratio'] = self.y
		df.insert(loc=0, column='item_id', value=[self.item_id]*len(self.y))
		df.insert(loc=len(df.columns), column='anchor_selling_price', value=[self.anchor_price]*len(self.y))
		df.insert(loc=len(df.columns), column='obs_time', value=self.observation_time_list)
		df.insert(loc=len(df.columns), column='target_time', value=self.new_y_time_list)
		if os.path.exists(file_name):
			temp_df = pd.read_csv(file_name, index_col=0)
			temp_df = temp_df.append(df, ignore_index=True)
			temp_df.to_csv(file_name, index=True)
		else:
			df.to_csv(file_name, index=True)

	def get_cumul_training_data(self):
		print_blue_bold("Reading from csv...")
		file_name = str(self.item_id) + "_" + str(self.interval) + "_training_data.csv"	
		self.dataframe_total = pd.read_csv(file_name)
		dataframe_observations = self.dataframe_total[['current_selling_quantity', 'current_buying_quantity', 'current_selling_to_anchor_ratio', 'current_population']]
		all_y_values = self.dataframe_total["target_selling_to_anchor_ratio"].values
		all_observation_list = dataframe_observations.values
		return all_observation_list, all_y_values

	def get_mean_abs_error(self):
		mean_absolute_error = metrics.mean_absolute_error(self.y_test, self.y_pred)
		print("mean_absolute_error: " + str(mean_absolute_error))
		return mean_absolute_error

	def get_explained_variance(self):
		explained_variance = metrics.explained_variance_score(self.y_test, self.y_pred)
		print("explained_variance_score: " + str(explained_variance))

	def make_predictions(self, observation_vectors):
		print_blue_bold("Making predictions...")
		if self.anchor_price == -1:
			print_red_bold_nl("Unable to make valid prediction due to model initialization failure")
		y_pred_ratios_to_anchor = self.model.predict(observation_vectors)
		y_pred_prices = [self.anchor_price * ratio for ratio in y_pred_ratios_to_anchor]
		observation_vector_prices = [self.anchor_price * obs_vec[2] for obs_vec in observation_vectors]
		print("CURRENT SAMPLE SIZE: " + str(len(self.X)))
		for i in range(len(observation_vectors)):
			print_bold("OBSERVATION VECTOR " + str(i))
			print("observation_vector: " + str(observation_vectors[i]))
			print("y_pred_ratio_to_anchor: " + str(y_pred_ratios_to_anchor[i]))
			print("observation_price: " + str(observation_vector_prices[i]))
			print("y_pred_price: ", end="")
			if y_pred_prices[i] > observation_vector_prices[i]:
				print_green_bold(y_pred_prices[i])
				print(" PREDICTED CHANGE OF ", end="")
				print_green_bold("+" + str(100*abs(1 - y_pred_prices[i]/observation_vector_prices[i])) + "%")
				print(" -- APPROX ", end="")
				print_green_bold(y_pred_prices[i] - observation_vector_prices[i])
				print(" GP OVER INTERVAL OF " + str(self.interval/2) + " (seconds)")
			else:
				print_red_bold(y_pred_prices[i])
				print(" PREDICTED CHANGE OF ", end="")
				print_red_bold("-" + str(100*abs(1 - y_pred_prices[i]/observation_vector_prices[i])) + "%")
				print(" -- APPROX ", end="")
				print_red_bold(y_pred_prices[i] - observation_vector_prices[i])
				print(" GP OVER INTERVAL OF " + str(self.interval/2) + " (seconds)")
		return y_pred_ratios_to_anchor

	def predict_current(self):
		print_blue_bold("Predicting on current values...")
		print("CURRENT TIME: " + str(time.time()))
		obs_vector = self.get_current_observation(self.item_id)
		if obs_vector == -1:
			print_red_bold_nl("Unable to predict due to invalid JSON request.")
		else:
			return self.make_predictions([obs_vector])

	def print_attrs(self):
		print("observation_vector_count: " + str(len(self.X)))
		print("target_vector_count: " + str(len(self.y)))
		print("observation_vectors: " + str(self.X))
		print("target_vectors: " + str(self.y))
		print("interval_of_prediction: " + str(self.interval/2))
		self.get_explained_variance()
		self.get_mean_abs_error()

	def show_plots(self):
		plot = sns.pairplot(self.dataframe_total, x_vars=['current_selling_quantity', 'current_buying_quantity', 'current_selling_to_anchor_ratio', 'current_population'], y_vars="target_selling_to_anchor_ratio", size=7, aspect=0.7, kind='reg')
		plt.show()

lin_reg_model = Model(6685, 28800, 300, True)
# lin_reg_model.print_attrs()
lin_reg_model.predict_current()
# lin_reg_model.show_plots()











