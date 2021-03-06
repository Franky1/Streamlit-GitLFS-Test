import numpy as np
import pandas as pd

# DATA_URL = "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv"

# read data from url, takes very long time
# df = pd.read_csv(DATA_URL, low_memory=False)

# read in the data from the previously downloaded csv file
df = pd.read_csv('Motor_Vehicle_Collisions_-_Crashes.csv', low_memory=False)

# remove all unwanted columns
df.drop(columns=['LOCATION'], inplace=True)
df = df.loc[:, ~df.columns.str.startswith('VEHICLE TYPE')]
# probably remove more unwanted columns here?
# df = df.loc[:, ~df.columns.str.startswith('CONTRIBUTING FACTOR')]

# replace lat and long values with 0 values to NaN
df['LATITUDE'].replace(to_replace=0, value=np.nan, inplace=True)
df['LONGITUDE'].replace(to_replace=0, value=np.nan, inplace=True)

# convert timestamps to datetime
df['timestamp'] = pd.to_datetime(df['CRASH DATE'] + ' ' + df['CRASH TIME'], format='%m/%d/%Y %H:%M')

# convert all integer columns to integer
integer_columns = df.columns.str.contains('NUMBER OF')
df.loc[:, integer_columns] = df.loc[:, integer_columns].astype(pd.Int16Dtype())

# convert all datatypes properly
df = df.convert_dtypes()

# sort the dataframe rows by timestamp
df.sort_values(by=['timestamp'], inplace=True, ascending=False)

# reset index to start from 0
df.reset_index(drop=True, inplace=True)

# lowercase of column names
df.columns= df.columns.str.lower()

# replace whitespace with underscores
df.columns = df.columns.str.replace(' ','_')

# set index to collision id column
# df.set_index('collision_id', inplace=True)

# write to feather file, still large
df.reset_index().to_feather('crashes.feather', compression='lz4')
# df.reset_index().to_feather('crashes.feather', compression='zstd')
# write to parquet file
df.to_parquet('crashes.parquet', engine='pyarrow', compression='brotli', index=True)

# write smaller feather file
df.head(100000).reset_index().to_feather('crashes_small.feather', compression='lz4')
