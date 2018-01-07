OSRS Market Analytics and Price Prediction
===================

A tool for visualizing real time prices and quantities of tradeable items in the game Old School Runescape. In this popular online video game, there is a central exchange for items that players use to trade eachother. This active and dynamic data set is an interesting analog for real life markets and prices. 


I plan to use machine learning and other data interpretations in order to predict price increases and drops.


Real Time Data Visualization
-------------

### Video Demo
[![Alt text](https://img.youtube.com/vi/z_3nSR7vbIo/0.jpg)](https://www.youtube.com/watch?v=z_3nSR7vbIo&feature=youtu.be)

This page allows users to select any item in OSRS and add it to the page. The charts on the page will display the current population of OSRS, the quantity traded of the selected items, and the prices of the selected items.

- The CanvasJS graphs will automatically resize axes to accomadate the largest price or quantity of an item loaded into the charts.

- Toggling the labels of the items above the graph will hide the data stream of that particular item and rescale the graph.


Machine Learning and Statistical Analysis to Predict Price Increases/Decreases
-------------

## Train and Predict Diagram

The goal of this part of the project is to use scikit-learn to predict a target value from a set of real time parameters for a specific item based on the predicted price increase in some user-defined time interval.

![alt text](https://i.imgur.com/MKz7XpI.png)

## Training Data Collection

This diagram demonstrates the process of gathering training data and create the observation matrix X, and the corresponding output vector y. λ is a user-defined interval passed in as a parameter when creating the Model object which specifies the duration of training data collection. The diagram below portrays and describes how λ distinguishes how target values are associated with parameter values.

![alt text](https://i.imgur.com/N0jtXiT.png)

*Based on this method of gathering training data, the resulting model is created based on a predicted price that would occurs λ/2 seconds after an observation was taken.*
