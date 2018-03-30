from flask import Flask
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
import pandas as pd
from scipy.spatial.distance import cosine

app = Flask(__name__)
 
@app.route("/")
def hello():

  
# --- Read Data --- #
  data = pd.read_csv('remodifieddata.csv')
  #print(data.shape)

# --- Start Item Based Recommendations --- #
# Drop any column named "user"
  data_germany = data.drop('user', 1)
#print(data_germany.head())

# Create a placeholder dataframe listing item vs. item
  data_ibs = pd.DataFrame(data=data_germany,index=data_germany.columns, columns=data_germany.columns)
#print(data_ibs.head)

# Lets fill in those empty spaces with cosine similarities
# Loop through the columns
  for i in range(0, len(data_ibs.columns)):
    # Loop through the columns for each column
     for j in range(0, len(data_ibs.columns)):
        # Fill in placeholder with cosine similarities
         data_ibs.ix[i, j] = 1 - cosine(data_germany.ix[:, i], data_germany.ix[:, j])

# Create a placeholder items for closes neighbours to an item
  data_neighbours = pd.DataFrame(index=data_ibs.columns, columns=[range(1, 11)])
  #print(data_neighbours.shape)
  #print(data_ibs.shape)

# Loop through our similarity dataframe and fill in neighbouring item names
  for i in range(0, len(data_ibs.columns)):
    data_neighbours.ix[i,:10] = data_ibs.ix[0:, i].sort_values(ascending=False)[:1].index

  #print("Looped through similarity dataframe")
# --- End Item Based Recommendations --- #

# --- Start User Based Recommendations --- #

# Helper function to get similarity scores
  def getScore(history, similarities):
     return sum(history * similarities) / sum(similarities)


# Create a place holder matrix for similarities, and fill in the user name column
  data_sims = pd.DataFrame(data=data_neighbours,index=data.index, columns=data.columns)
  data_sims.ix[:, :1] = data.ix[:, :1]

  #print("Placeholder matrix for similarities")

# Loop through all rows, skip the user column, and fill with similarity scores
  for i in range(0, len(data_sims.index)):
    for j in range(1, len(data_sims.columns)):
        #print("Inside for")
        user = data_sims.index[i]
        product = data_sims.columns[j]

        if data.ix[i][j] == 1:
            data_sims.ix[i][j] = 0
        else:
            product_top_names = data_neighbours.ix[product][1:10]
            product_top_sims = data_ibs.ix[product].sort_values(ascending=False)[1:10]
            user_purchases = data_germany.ix[user, product_top_names]

            data_sims.ix[i][j] = getScore(user_purchases, product_top_sims)

# Get the top songs
  data_recommend = pd.DataFrame(data=data_sims,index=data_sims.index, columns=['user', '1', '2', '3', '4', '5', '6'])
  data_recommend.ix[0:, 0] = data_sims.ix[:, 0]
  #print(data_recommend.head())

# Instead of top song scores, we want to see names
  for i in range(0, len(data_sims.index)):
     data_recommend.ix[i, 1:] = data_sims.ix[i, :].sort_values(ascending=False).ix[1:7, ].index.transpose()

  #print("Almost there")
# Print a sample
  return (data_recommend.ix[:10, :4].to_json())
 
if __name__ == "__main__":
    app.run()