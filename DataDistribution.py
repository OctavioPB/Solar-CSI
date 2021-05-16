# -*- coding: utf-8 -*-
"""
California Solar Initiative: Dataset distribution and Statistics

@author: Octavio Perez Bravo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st

"""

Data loading:
    
    1- The data csv is converted into a dataframe
    2- Only the Total Cost of the project, The incentive amount
    recived and the company name are pulled from the dataset
    3- Empty records are deleted from the dataframe
    4- The information for the most expensive project is queried
    
"""

full_dataset = pd.read_csv('WorkingDataSet.csv')
solar_companies = full_dataset[['Solar Contractor Company Name',
                               'Total Cost', 'Incentive Amount' ]]
solar_companies.rename(columns = {'Solar Contractor Company Name':'Company Name'}, 
                       inplace = True)
solar_companies.dropna(axis = 0, inplace = True)
solar_companies.reset_index(drop = True, inplace = True)
solar_companies['Total Cost'] = pd.to_numeric(solar_companies['Total Cost'])
max_cost = solar_companies['Total Cost'].idxmax()
company_mc = solar_companies.iloc[max_cost]
print(company_mc)

"""

Raw data plotting:
    
    1- boxplot plots are created to observe the raw data distribution
    
"""
plt.subplot(1,2,1)
plt.title('Data boxplot before cleaning')
plt.boxplot(solar_companies['Incentive Amount'])
plt.subplot(1,2,2)
plt.boxplot(solar_companies['Total Cost'])
plt.show()

"""

Outlier detection:
    
    1- Interquartile ranges are calculated
    2- Using the Z scores table the data is filtered to keep only the
    data within one standard deviation.
    
"""

q1 = solar_companies['Incentive Amount'].quantile(0.25)
print(q1)
q3 = solar_companies['Total Cost'].quantile(0.75)
print(q3)

z_scores = st.zscore(solar_companies[['Total Cost', 'Incentive Amount']])
abs_z_scores = np.abs(z_scores)
filtered_entries = (abs_z_scores < 1).all(axis=1)
solar_companies = solar_companies[filtered_entries]

"""

Plotting:
    
    1- New boxplots are created to detect the new data ranges
    2- Histograms are created to visualize the distribution
    
"""

plt.subplot(1,2,1)
plt.title('Data within 1 standard deviation')
plt.boxplot(solar_companies['Incentive Amount'])
plt.subplot(1,2,2)
plt.boxplot(solar_companies['Total Cost'])
plt.show()

plt.hist(solar_companies['Total Cost'], bins=20, color = 'green')
plt.title('Total Cost within 1 standard deviation')
plt.ylabel('Number of records')
plt.xlabel('USD Amount')
plt.show()
plt.hist(solar_companies['Incentive Amount'], bins=20, color = 'blue')
plt.title('Incentive Amount within 1 standard deviation')
plt.ylabel('Number of records')
plt.xlabel('USD Amount')
plt.show()


