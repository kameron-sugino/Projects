#!/usr/bin/env python

import pandas as pd
from numpy import reshape 
import numpy as np
#df = pd.read_csv("C:/Users/Kam/Desktop/Projects/Cost-Splitter/test_data.csv")
#df = pd.read_csv("C:/Users/Kam/Desktop/Projects/Cost-Splitter/test_data_no_dummy.csv")

def cost_splitter(df):
    #split out binary table
    pay_matrix = df.iloc[:, 3:df.shape[1]]
    #calculate number of people who participated in the purchase and then split the total cost
    rowsum = pay_matrix.sum(axis=1)
    cost_per_person = df.iloc[:,2]/rowsum
    pay_matrix_cpp = (pay_matrix.T*cost_per_person).T

    #create index names for later
    ind = list(pay_matrix_cpp.columns)
    ind2 = pd.DataFrame(ind)
    ind3 = ["id"] + ind

    #create melted matrix and sum the "Paid By" values together
    df_new = pd.concat([df.iloc[:,1],pay_matrix_cpp],axis=1)

    #append dummy rows to bottom of the matrix; need to make sure that each person is in the "Paid By" column to ensure a square matrix
    people = pd.DataFrame(list(pay_matrix_cpp.columns))
    empty = pd.DataFrame(np.zeros((len(people),len(people)), dtype=int))
    empty_people = pd.concat([people, empty],axis=1)
    empty_people.columns=df_new.columns
    df_new_dummy = pd.concat((df_new,empty_people))

    #melt the dataframe for groupby
    df_melt = pd.melt(df_new_dummy, 
                      id_vars = ["Paid By"])
    df_melt_groupby = df_melt.groupby(["Paid By","variable"]).sum().reset_index()

    #cast the grouped data into a matrix
    df_cast = df_melt_groupby.pivot(index="Paid By", columns="variable")
    df_cast_t = (df_cast).T

    #convert to array for matrix subtraction
    #the pandas dataframes wouldn't cooperate because the transposition moved the "name" parameter
    #and I wasn't able to fix it
    t1 = df_cast.to_numpy()
    t2 = df_cast_t.to_numpy()

    #subtract the original matrix from the transposed matrix to get back the (amount each person owes - the amount owed)
    matrix_delta = np.subtract(t1,t2)
    #append names to output a "paid by" column in the final output
    matrix_delta_np = np.hstack((ind2,matrix_delta))
    df_delta = pd.DataFrame(matrix_delta_np)
    df_delta_named = df_delta.set_axis(people,axis=0).set_axis(ind3,axis=1)

    #melt the matrix again and remove the rows with a negative or zero value
    df_delta_named_melt = df_delta_named.melt(id_vars="id")
    final_all = df_delta_named_melt.rename(columns={"id":"Geting paid","variable":"Is paying","value":"Amount"})
    final = final_all[(final_all[["Amount"]] > 0).all(axis=1)]
    print(final)
    

#test case
#cost_splitter(df)
