OSRS Market Analytics and Price Prediction
======

A tool for visualizing real time prices and quantities of tradeable items in the game Old School Runescape. In this popular online video game, there is a central exchange for items that players use to trade eachother. This p This active and dynamic data set is an interesting analog for real life markets and prices. 


# Video Demo (Part I and II)
[![Alt text](http://i3.ytimg.com/vi/M8LtCLca1m8/maxresdefault.jpg)](https://www.youtube.com/watch?v=M8LtCLca1m8)

# I. Real Time Data Visualization

This part of the project allows users to select any item in OSRS and add it to the page. The charts on the page will display the current population of OSRS, the quantity traded of the selected items, and the prices of the selected items.

- The CanvasJS graphs will automatically resize axes to accomadate the largest price or quantity of an item loaded into the charts.

- Toggling the labels of the items above the graph will hide the data stream of that particular item and rescale the graph.


# II. Machine Learning and Statistical Analysis to Predict Price Increases/Decreases

The goal of this part of the project is to use scikit-learn to predict a target value from a set of real time parameters for a specific item based on the predicted price increase in some user-defined time interval.

![alt text](https://i.imgur.com/MKz7XpI.png)

## Training Data Collection

This diagram demonstrates the process of gathering training data and create the observation matrix **X**, and the corresponding output vector **y**. **λ** is a user-defined interval passed in as a parameter when creating the Model object which specifies the duration of training data collection. The diagram below portrays and describes how λ distinguishes how target values are associated with parameter values.

![alt text](https://i.imgur.com/N0jtXiT.png)

*Based on this method of gathering training data, the resulting model is created based on a predicted price that would occurs **λ/2** seconds after an observation was taken.*

Data Sanitization
------

![alt text](https://i.imgur.com/4PT05c6.png)

The diagram above demonstrates the process of aligning the values in output vectors to an observation vector based on the difference between the expected time of observation time + λ/2. observation_time_list represents a mapping between each vector in the observation_vector matrix X and a the time which it was collected at. The target_time_list represents the times that each y value in the target_vector was gathered. For each timestamp, stored as seconds elapsed since January 1st, 1970, 12:00 AM, the target alignment functions perform a binary search to find the appropriate timestamp. These functions utilize the fact that target_time_list is already sorted for an efficient **ϴ(NlogN)** runtime. Upon finding the correct timestamp for a given x_vector, a new target_vector_list y is generated based on the index of that timestamp in order to generate a list which aligns the proper y value to the associated observation vector based on the correct within a specified margin of error. 

![alt text](https://i.imgur.com/PfoFKUt.png)

In the case that there is not a timestamp which is within the acceptable error to the timestamp of the observation vector, a -1 is returned to signify that that vector should be thrown out of the training data. Other errors such as JSON request fails also return -1 to invalidate an observation vector or a target value. This image demonstrates how the entire row, observation vector and associated target value (after "Target Alignment") is removed from the dataset. 
