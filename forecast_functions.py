from time_functions import dt_to_string, date_convert_RU
import statistics
import datetime
import urllib.parse
import urllib.request

def forecast_means(data):
	"""
	Calculate mean temperature for full days in forecast.
	Full days are those, that have eight three-hour interval in dictionary (0, 21, 3).

	:param data: dictionary with key=date <datetime.date> and value=temperature <float>.
	:return: dictionary with key=date <datetime.date> and value=temperature <float>.
	"""
	# collect dates
	date_keys = [x.date() for x in list(data)]
	# filter out full days
	days = set([x for x in date_keys if date_keys.count(x) == 8])
	# group temperature by dates from the filtered list
	temps_grouped = map(lambda x: [v for (k, v) in data.items() if x == k.date()], list(sorted(days)))
	# return a dictionary with dates and mean temperature
	return dict([(x, round(statistics.mean(y), 2)) for x, y in zip(list(sorted(days)), list(temps_grouped))])


def last_hour(local_forecast):
	"""
	Check whether next three-hour interval has different date.

	:param local_forecast: dictionary with local times <datetime.date> and temps <float>.
	:return: True if date is different, False otherwise.
	"""
	# check date for current hour
	current_interval_date = list(local_forecast)[0].date()
	# check date of the next interval: + 3 hours
	next_interval_date = (list(local_forecast)[0] + datetime.timedelta(hours=3)).date()
	if next_interval_date != current_interval_date:
		return True
	else:
		return False
	
def calculate_today_last(region, db, local_forecast):
	"""
	Save today mean temperature to database and reset today table.

	:param region: instance of Region class <object>.
	:param db: instance of DatabaseQueries class <object>.
	:param local_forecast: dictionary with local times <datetime.date> and temps <float>.
	:return: mean temperature for today <float>.
	"""
	
	# get all temps from today table
	today_historical_params = {'table': 'today',
						  'conditions': ['region_id'],
						  'condition_data': (region.id,),
						  'filters': ['hour_{}'.format(x) for x in range(0, 24, 3)]}

	# returns a list of tuples
	today_historical = db.select(**today_historical_params)

	if None in today_historical[0]:
		return 0.0

	# calculate mean
	today_avg = round(statistics.mean(today_historical[0]), 2)

	# save to history
	current_date = dt_to_string(list(local_forecast)[0].date(), time=False)
	save_to_history_params = {'table': 'history',
							  'destinations': ['region_id', 'temp', 'date', 'datetime'],
							  'data': (region.id, today_avg, current_date,
									   dt_to_string(datetime.datetime.now()))}
	db.insert(**save_to_history_params)

	# set today table to null
	set_today_to_null_params = {'table': 'today',
								'destinations': ['hour_{}'.format(x) for x in range(0, 24, 3)] + ['datetime'],
								'data': tuple([None] * 9),
								'conditions': ['region_id'],
								'condition_data': (region.id,)}
	db.update(**set_today_to_null_params)

	return today_avg

def calculate_today_intermediate(region, db, local_forecast):
	"""
	Calculate and return intermediate forecast for today.
	Blends historical hour temperature and forecast from API.

	:param region: instance of Region class <object>.
	:param db: instance of DatabaseQueries class <object>.
	:param local_forecast: dictionary with local times <datetime.date> and temps <float>.
	:return: mean temperature for today <float>.
	"""
	
	# get all not null temps from today table
	today_historical_params = {'table': 'today',
						  'conditions': ['region_id'],
						  'condition_data': (region.id,),
						  'filters': ['hour_{}'.format(x) for x in range(0, 24, 3)]}
	# download historical temperature for today (returns a list of tuples)
	today_historical = db.select(**today_historical_params)

	# filter out None values
	today_historical = [temp for temp in today_historical[0] if temp != None]

	# get forecast for the rest of the day
	today_forecast = [v for k, v in local_forecast.items() if k.date() == list(local_forecast)[0].date()]

	# blend these together and count mean
	today_avg = round(statistics.mean(today_historical + today_forecast), 2)

	return today_avg
	

def search_heating_date(data, threshold=8):
	"""
	Search for heating date. Threshold set to 8°С by default.

	:param data: blended dictionary with dates <datetime.date> and temperatures <float>.
	:return: heating date <datetime.date> if found, None otherwise.
	"""

	# set counter to zero
	counter = 0
	# iterate trough data
	for date, temp in data.items():
		# check for spring
		if spring():
			# check for temperatures greater, than 8 degrees
			if temp > threshold:
				# increment counter if true
				counter += 1
				# return heating supply date if counter is equal to 5
				if counter == 5:
					return date + datetime.timedelta(1)
		# if not spring
		else:
			# check for temperatures less, than 8 degrees
			if temp < threshold:
				# increment counter if true
				counter += 1
				# return heating cut date if counter is equal to 5
				if counter == 5:
					return date + datetime.timedelta(1)
	# return None if heating date not found
	return None

def save_heating_date(db, region):
	"""
	Save heating date to database. Set to NULL if no date found.
	Stop tracking region by setting last_date to 1, if heating date
	reaches current date.

	:param db: instance of DatabaseQueries class <object>.
	:param region: instance of Region class <object>.
	:return: void function.
	"""
	# save heating date to database
	if region.heating_date:
		heating_date_params = {'table': 'regions',
								'destinations': ['heating_date', 'heating_date_RU'],
								'data': (dt_to_string(region.heating_date, time=False),
										 date_convert_RU(region.heating_date)),
								'conditions': ['id'],
								'condition_data': (region.id,)}
		db.update(**heating_date_params)
	# set heating date to null if no date found
	else:
		heating_date_params = {'table': 'regions',
							   'destinations': ['heating_date', 'heating_date_RU'],
							   'data': (None, None),
							   'conditions': ['id'],
							   'condition_data': (region.id,)}
		db.update(**heating_date_params)

	# stop tracking region if heating date is today
	if region.heating_date == datetime.datetime.now().date():
		last_date_params = {'table': 'regions',
							   'destinations': ['last_date'],
							   'data': (1,),
							   'conditions': ['id'],
							   'condition_data': (region.id,)}
		db.update(**last_date_params)


def spring(date=None):
	"""
	Check if current month is spring (march-august).

	:param date: date <datetime.date> or current date by default.
	:return: True if spring, False otherwise.
	"""

	# extract current month if not given
	if not date:
		date = datetime.datetime.now().month

	if date in [3, 4, 5, 6, 7, 8]:
		return True
	else:
		return False

def iterator(regions):
	"""
	Collect misfired regions from file if such exist.

	:param regions: number of regions <list>.
	:return: misfired region ids <list> or all region ids <list>.
	"""
	misfired = []
	# look for misfired regions in file
	with open("misfired.txt", 'r') as file:
		for line in file:
			misfired.append(int(line.strip('\n')))
	# if file is not empty return list of misfired regions as list
	if misfired:
		return misfired
	# return non last date regions
	else:
		return [x for x in range(1, regions + 1)]

def parse_api(baseurl):
	"""
	Parse json by given url. Wait for ten minutes if server
	is not responding. Write error after four attempts.

	:param baseurl: url <string>.
	:return: parsed json object <byte> or False if server is not responding four times.
	"""
	# Make 4 api calls in total
	for call in range(1, 5):
		# Write an error to file if no response after 4 attempts
		if call == 4:
			with open('errors.txt', 'a') as file:
				file.write("Server is not responding after 4 attempts. Time: {}\n".format(
					dt_to_string(datetime.datetime.now())
				))
			return False
		try:
			# download data from api
			result = urllib.request.urlopen(baseurl).read()
			return result
		except urllib.error.URLError:
			# wait 10 minutes if server is not responding and make another call
			print("Seems like server is not responding. Will try again in 10 minutes...")
			time.sleep(660)

def check_last_dates(db):
	"""
	Check regions, that have last_date set to zero.

	:param db: instance of DatabaseQueries class <object>.
	:return: list of region ids with last_date = 0 <list> or None if empty list.
	"""
	last_dates_params = {'table': 'regions',
						  'conditions': [],
						  'condition_data': (),
						  'filters': ['id', 'last_date']}

	last_dates = db.select(**last_dates_params)

	# select zero value last_dates
	zero_last_dates = [x for x in last_dates if x[1] == 0]
	
	# if there are zero last dates return a list of ids with zero last date
	if zero_last_dates:
		return [x[0] for x in zero_last_dates]
	else:
		return None

def reset_last_dates(db):
	"""
	Reset last_dates for all regions.

	:param db: instance of DatabaseQueries class <object>.
	:return: void function.
	"""
	last_date_params = {'table': 'regions',
						'destinations': ['last_date'],
						'data': (0,),
						'conditions': [],
						'condition_data': ()}
	db.update(**last_date_params)