import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

dataframe_total = pd.read_csv('6685_25_training_data.csv')
dataframe_observations = dataframe_total[['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population']]
all_y_values = dataframe_total["price_half_interval"].values
all_observation_list = dataframe_observations.values

plot = sns.pairplot(dataframe_total, x_vars=['current_selling_quantity', 'current_buying_quantity', 'current_selling_price', 'current_population'], y_vars="price_half_interval", size=7, aspect=0.7, kind='reg')
plt.show()