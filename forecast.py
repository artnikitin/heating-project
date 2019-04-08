import json
import datetime
import time
import os
from database_queries import DatabaseQueries
from region import Region
from time_functions import to_datetime, dt_to_string
import forecast_functions as ff

db = DatabaseQueries("weather.db")

# set season start dates
spring_season_start_date = '01-04'
fall_season_start_date = '01-09'
date_today = datetime.datetime.now().strftime("%d-%m")

# check whether it's start of the season
if date_today == spring_season_start_date or date_today == fall_season_start_date:
	# if true reset all last dates to zero
	ff.reset_last_dates(db)

# count regions
REGIONS = db.regions('regions')
API_KEY = os.environ.get("API_KEY_OW")

def main():
	# set API call counter to zero
	api_call_counter = 0

	# set a list for misfired regions
	misfired = []

	# iterator is set to REGIONS or misfired regions
	# if such exist
	for i in ff.iterator(REGIONS):
		# populate a Region class instance
		region = Region('weather.db', i)

		# collect API key and form a request
		baseurl = "http://api.openweathermap.org/data/2.5/forecast?id={}&units=metric&APPID={}".format(
			region.woeid, API_KEY)

		# check for api calls: restriction 60 calls/minute for free plan
		if api_call_counter == 59:
			# DEBUG
			print('Sleeping for 70 seconds...\n')
			# pause for one minute
			time.sleep(70)
			# reset counter
			api_call_counter = 0

		# download data
		result = ff.parse_api(baseurl)

		# exit script if server is not responding for 45 minutes
		if not result:
			break

		# increment api call counter
		api_call_counter += 1

		# read json
		data = json.loads(result)

		# in case of 404 error or empty data, consider region as misfired
		if not data or data['cod'] == '404':
			misfired.append(i)
			# DEBUG
			print('{} misfired\n'.format(i))
			continue

		# write 429 and 401 errors to errors.txt file
		if data['cod'] == '429' or data['cod'] == '401':
			with open('errors.txt', 'a') as file:
				file.write('Region {}, error code {}: message {} time {}\n'.format(
					i, data['cod'], data['message'],
					dt_to_string(datetime.datetime.now())))
			break

		# proceed if no api errors
		if data['cod'] == '200':

			# collect current temperature
			region.current_temp = data['list'][0]['main']['temp']

			# collect current hour
			region.current_hour = to_datetime(data['list'][0]['dt_txt']).hour

			# save current temp to today
			current_hour_params = {'table': 'today',
						  'destinations': ['hour_' + str(region.current_hour), 'datetime'],
						  'data': (region.current_temp, dt_to_string(datetime.datetime.now())),
						  'conditions': ['region_id'],
						  'condition_data': (region.id,)}

			db.update(**current_hour_params)

			# aggregate forecast
			utc_forecast = {x['dt_txt']: x['main']['temp'] for x in data['list']}
			# convert forecast to local time
			local_forecast = {to_datetime(key) + datetime.timedelta(hours=region.timezone):
								  value for key, value in utc_forecast.items()}

			# calculate average weather for today
			if ff.last_hour(local_forecast):
				region.today_forecast = {list(local_forecast)[0].date():
											 ff.calculate_today_last(region, db, local_forecast)}

			if not ff.last_hour(local_forecast):
				region.today_forecast = {list(local_forecast)[0].date():
											 ff.calculate_today_intermediate(region, db, local_forecast)}

			# calculate forecast
			region.forecast = ff.forecast_means(local_forecast)

			# blend weather data
			blended_data = {**region.historical, **region.today_forecast, **region.forecast}

			# save blended weather data for graphing
			destinations = ['temp_{}'.format(x) for x in range(1, 11)] +\
						   ['date_{}'.format(x) for x in range(1, 11)] +\
						   ['datetime']
			print(destinations)

			data = tuple([x for x in list(blended_data.values())]) +\
				   tuple([dt_to_string(x, time=False) for x in list(blended_data)]) +\
				   (dt_to_string(datetime.datetime.now()),)

			print(data)

			graph_params = {'table': 'graph',
						   'destinations': destinations,
						   'data': data,
						   'conditions': ['region_id'],
						   'condition_data': (region.id,)}

			db.update(**graph_params)

			# calculate heating date only if last_date is not set to 1
			if region.last_date == 0:

				# search for heating date
				region.heating_date = ff.search_heating_date(blended_data)

				# save heating date to database if exists
				ff.save_heating_date(db, region)

			# DEBUG
			print('region {} completed successfully\n'.format(i))

	# write misfired regions to file
	with open('misfired.txt', 'w') as file:
		if len(misfired) == 0:
			file.write('')
		else:
			for misfired_region in misfired:
				file.write(str(misfired_region) + '\n')
		
			
if __name__ == "__main__":
	main()