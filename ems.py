# -*- coding: utf-8 -*-
"""ems

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QF-F0zFBC37xGbHwil9XArKutu_GZMIe
"""


import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import random
from scipy.optimize import linprog


# Load the dataset
df = pd.read_csv("/content/sample_data/ems.csv")  # Ensure this file is uploaded alongside your app in GitHub


# 1. Perform K-Means Clustering
def perform_clustering(df):
    area_demand = df.groupby("Area")[[f"Appointments_{year}" for year in range(2020, 2025)]].sum()
    area_demand["Total_Appointments"] = area_demand.sum(axis=1)

    kmeans = KMeans(n_clusters=3, random_state=42)
    area_demand["Cluster"] = kmeans.fit_predict(area_demand[["Total_Appointments"]])

    return area_demand


# 2. Visualize Clustering Results
def plot_clustering_results(area_demand):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=area_demand, x=area_demand.index, y="Total_Appointments", hue="Cluster", palette="viridis")
    plt.title("High-Demand Areas Clustering")
    plt.xlabel("Area")
    plt.ylabel("Total Appointments")
    plt.legend(title="Cluster")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)


# 3. Shortest Path Finder
def find_shortest_path():
    G = nx.Graph()
    locations = list(df["Area"].unique())
    edges = [(locations[i], locations[(i + 1) % len(locations)], random.randint(2, 15)) for i in range(len(locations))]
    G.add_weighted_edges_from(edges)

    start_location = st.selectbox("Select Start Location", locations)
    destination_location = st.selectbox("Select Destination Location", locations)

    if st.button("Find Shortest Path"):
        if start_location != destination_location:
            shortest_path = nx.shortest_path(G, source=start_location, target=destination_location, weight="weight")
            path_length = nx.shortest_path_length(G, source=start_location, target=destination_location, weight="weight")
            st.write(f"Shortest path: {shortest_path} with length {path_length}")
        else:
            st.error("Start and destination locations cannot be the same.")


# 4. Predict Ambulance Demand
def predict_ambulance_demand(df):
    X = df[["Appointments_2020", "Appointments_2021", "Appointments_2022", "Appointments_2023"]]
    y = df["Appointments_2024"]

    model = LinearRegression()
    model.fit(X, y)

    future_demand = model.predict(X)
    df["Predicted_2024_Demand"] = future_demand

    st.write("### Predicted Ambulance Demand for 2024")
    st.write(df[["Area", "Predicted_2024_Demand"]])


# 5. Resource Allocation
def resource_allocation(df):
    area_demand = df.groupby("Area")["Appointments_2024"].sum()
    n_areas = len(area_demand)
    c = -area_demand.values
    A_eq = [[1] * n_areas]
    b_eq = [100]
    x_bounds = [(0, area_demand[area]) for area in area_demand.index]

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=x_bounds, method="highs")

    if result.success:
        st.write("### Optimal Resource Allocation")
        allocation = {area: result.x[i] for i, area in enumerate(area_demand.index)}
        st.write(allocation)
    else:
        st.error("Optimization failed. Please check the inputs.")


# 6. Perform EDA
def perform_eda(df):
    st.write("### Exploratory Data Analysis")
    st.write("#### Basic Statistics")
    st.write(df.describe())

    yearly_totals = df[[f"Appointments_{year}" for year in range(2020, 2025)]].sum()
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=yearly_totals, marker="o")
    plt.title("Total Appointments by Year")
    plt.xlabel("Year")
    plt.ylabel("Total Appointments")
    plt.grid()
    st.pyplot(plt)


# 7. Streamlit Interface
def main():
    st.title("EMS: Emergency Medical Services")
    st.write("### EMS Dataset", df.head())
    clustered_data = perform_clustering(df)
    plot_clustering_results(clustered_data)
    predict_ambulance_demand(df)
    resource_allocation(df)
    perform_eda(df)
    find_shortest_path()


if __name__ == "__main__":
    main()
