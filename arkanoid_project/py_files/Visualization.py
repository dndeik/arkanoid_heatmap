import argparse
from influxdb import InfluxDBClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#Game window stats
width = 1200
height = 800

"""Instantiate a connection to the InfluxDB."""

dbname = 'coordinates'
dbuser = 'telegraf'
dbuser_password = 'telegraf'
query = 'select * from coord;'

# client = InfluxDBClient(host, port, user, password, dbname)
client = InfluxDBClient(host='127.0.0.1', port=8086, database=dbname)

print("Switch user: " + dbuser)
client.switch_user(dbuser, dbuser_password)

print("Querying data: " + query)
result = client.query(query)

print("Result: {0}".format(result))

print("Next dataframe")
df = pd.DataFrame(client.query(query).get_points())
print(df.head())

#PADDLE VISUALISATION

grouped = df.groupby(['obj','x_coord','y_coord'])

series = grouped.time.nunique()
# print("Series")
# print(series.head())

xy_frame = series.loc['paddle',:,:].reset_index().pivot(index='y_coord', columns='x_coord', values='time')
# print(xy_frame.iloc[:10,:9])

xy_frame.fillna(0, inplace=True)

xy_frame = xy_frame.reindex(range(0,height,10), axis=0, fill_value=0)
xy_frame = xy_frame.reindex(range(0,width,10), axis=1, fill_value=0).astype(int)

# print("Next print")
# print(xy_frame.loc[770, 770:])

#EXPANDING REGION

quantity_paddle = {}
for x in range(height-30, height, 10):
    for y in range(0, width, 10):
        if xy_frame.loc[x,y] != 0:
            quantity_paddle[(x, y)] = int(xy_frame.loc[x, y])
            xy_frame.at[x, y] = 0

for key in quantity_paddle:
    for new_x in range(key[1] - 160, key[1] + 170, 10):
        xy_frame.at[key[0], new_x] = xy_frame.loc[key[0], new_x] + quantity_paddle.get(key[0], key[1])
        xy_frame.at[key[0]-10, new_x] = xy_frame.loc[key[0], new_x]

sns.heatmap(xy_frame)
plt.show()

#BALL VISUALISATION

grouped = df.groupby(['obj','x_coord','y_coord'])

series = grouped.time.nunique()
# print("Series")
# print(series.head())

xy_frame = series.loc['ball',:,:].reset_index().pivot(index='y_coord', columns='x_coord', values='time')
# print(xy_frame.iloc[:10,:9])

xy_frame.fillna(0, inplace=True)

xy_frame = xy_frame.reindex(range(0,height,10), axis=0, fill_value=0)
xy_frame = xy_frame.reindex(range(0,width,10), axis=1, fill_value=0).astype(int)

# print("Next print")
# print(xy_frame.loc[770, 770:])

#EXPANDING REGION

quantity_paddle = {}
# for x in range(0, height, 10):
#     for y in range(0, width, 10):
#         if xy_frame.loc[x,y] != 0:
#             quantity_paddle[(x, y)] = int(xy_frame.loc[x, y])
#             xy_frame.at[x, y] = 0
#
# for key in quantity_paddle:
#     for new_x in range(key[1] - 160, key[1] + 170, 10):
#         xy_frame.at[key[0], new_x] = xy_frame.loc[key[0], new_x] + quantity_paddle.get(key[0], key[1])
#         xy_frame.at[key[0]-10, new_x] = xy_frame.loc[key[0], new_x]

sns.heatmap(xy_frame)
plt.show()