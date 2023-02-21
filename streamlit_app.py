import glob
import os

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Motor Vehicle Collisions in NYC", page_icon='🚓',
                    layout='centered', initial_sidebar_state='collapsed')


@st.cache_resource
def get_local_feather_files():
    list_of_files = glob.glob('*.feather')
    files_with_size = [(file_path, os.stat(file_path).st_size) for file_path in list_of_files]
    df = pd.DataFrame(files_with_size)
    df.columns = ['File Name', 'File Size in KBytes']
    df['File Size in KBytes'] = (df['File Size in KBytes'] / 1024).astype(int)
    return df


@st.cache_resource
def load_data():
    data = pd.read_feather('crashes.feather')
    data.drop(columns=['index'], inplace=True)
    # drop rows with no lat/long values:
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    # drop rows outside bounding box of NYC:
    data = data[(data['latitude'] > 40.0) & (data['latitude'] < 42.0) &
                (data['longitude'] > -76.0) & (data['longitude'] < -70.0)]
    return data


@st.cache_data(show_spinner=False)
def query_data_by_persons_injured(injured_people):
    return data.query(f'number_of_persons_injured >= {injured_people}')[["latitude", "longitude"]].dropna(how="any")


@st.cache_data(show_spinner=False)
def get_query_persons_string(selection: str):
    return f'number_of_{selection.lower().split()[0]}_{selection.lower().split()[1]}'


@st.cache_data(show_spinner=False)
def filter_data_by_type_of_people(type_of_people, amount=8):
    return data[(data[type_of_people] > 0)][['on_street_name', 'off_street_name', type_of_people]].sort_values(
        by=[type_of_people], ascending=False).dropna(thresh=2).fillna('')[:amount]


@st.cache_resource
def get_all_contributing_factors():
    contrib_cols = [col for col in data.columns if col.startswith('contributing_factor')]
    contrib_sum = data[contrib_cols].apply(pd.Series.value_counts).fillna(0).sum(axis=1).sort_values(ascending=False).astype(int).to_frame()
    contrib_sum.index.rename('Contributing Factors', inplace=True)
    contrib_sum.columns = ['Frequency of mention']
    return contrib_sum


st.title("Motor Vehicle Collisions in NYC")
st.markdown("This application is a Streamlit Demo App to test Git-LFS on Streamlit Cloud.")

st.subheader("All local feather files found")
st.table(get_local_feather_files())

with st.spinner("Loading data..."):
    data = load_data()

st.subheader("Where are the most people injured in NYC")
max_injured_people = int(data['number_of_persons_injured'].max())
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, max_injured_people)
data_by_persons_injured = query_data_by_persons_injured(injured_people)
st.map(data=data_by_persons_injured)

st.subheader("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people injured or killed',
            ['Persons Injured', 'Persons Killed', 'Pedestrians Injured', 'Pedestrians Killed',
            'Cyclist Injured', 'Cyclist Killed', 'Motorist Injured', 'Motorist Killed',])

st.table(filter_data_by_type_of_people(get_query_persons_string(select)))

st.subheader("Contributing Factors for accidents")
st.table(get_all_contributing_factors())

st.subheader("Show Raw Data")
if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data.head(100).fillna(''))  # limit to first 100 rows
