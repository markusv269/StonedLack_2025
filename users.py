import sqlite3
import pandas as pd
import pyarrow

conn = sqlite3.connect('slr_users.sqlite')
users_df = pd.read_sql('SELECT * FROM users', con=conn)

print(users_df.head(5))

users_df.to_parquet('users.parquet', engine='pyarrow')