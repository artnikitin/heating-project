import datetime

def to_datetime(string, date=True, time=True):
	"""
	Convert datetime object to string.
	Strip date or time using optional parameters.
	:param string: timestamp <string>
	:param date: set to False to strip date.
	:param time: set to False to strip time.
	:return: datetime object <datetime>
	"""
	if date and not time:
		return datetime.datetime.strptime(string, '%Y-%m-%d')
	elif time and not date:
		return datetime.datetime.strptime(string, '%H:%M:%S')
	else:
		return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

def dt_to_string(dt, date=True, time=True):
	"""
	Convert string timestamp to datetime object.
	Strip date or time using optional parameters.
	:param dt: datetime object <datetime>
	:param date: set to False to strip date.
	:param time: set to False to strip time.
	:return: timestamp <string>
	"""
	if date and not time:
		return dt.strftime('%Y-%m-%d')
	elif time and not date:
		return dt.strftime('%H:%M:%S')
	else:
		return dt.strftime('%Y-%m-%d %H:%M:%S')
	
def date_convert_RU(date, short=False):
	"""
	Convert date object to string in Russian with month name:
	'2018-01-06' -> '1 июня'.

	:param date: date object <datetime.date>
	:param short: set to True to get abbreviated month name, use for graph labels.
	:return: date <string>
	"""
	months_ru = ['января', 'февраля', 'марта',
				 'апреля', 'мая', 'юня', 'июля',
				 'августа', 'сентября', 'октября',
				 'ноября', 'декабря']

	months_ru_short = ['янв', 'фев', 'мар',
				 'апр', 'мая', 'июн', 'июл',
				 'авг', 'сент', 'окт',
				 'нояб', 'дек']

	if short:
		for index, month in enumerate(months_ru_short, 1):
			if index == date.month:
				return "{} {}".format(date.day, month)
	else:
		for index, month in enumerate(months_ru, 1):
			if index == date.month:
				return "{} {}".format(date.day, month)
