import pytz
from tzwhere import tzwhere

def utc_to_local_pytz(utc_dt, timezone):
	"""
	Converts UTC time to local time.
	:param utc_dt: UTC datetime object <datetime>
	:param timezone: timezone in format 'Europe/Paris' <string>
	:return: datetime object in local time <datetime>
	"""
	local_tz = pytz.timezone(timezone)
	local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
	return local_dt

def find_timezone(lat, lon):
	"""
	Search for timezone with geographic coordinates using tzwhere.
	:param lat: latitude <float>
	:param lon: longitude <float>
	:return: timezone in format 'Europe/Paris' <string>
	"""
	tz = tzwhere.tzwhere()
	timezone = tz.tzNameAt(lat, lon)
	if not timezone:
		timezone = tz.tzNameAt(round(lat), round(lon))
	return timezone