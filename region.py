import sqlite3
from time_functions import to_datetime

class Region:
	def __init__(self, database, region_id):
		self.database = database
		self.id = region_id
		self.woeid, self.timezone, self.last_date = self._query_basic()
		self.historical = self._query_historical()
		self.current_temp = None
		self.current_hour = None
		self.today_forecast = None
		self.forecast = None
		self.heating_date = None

	def _query_basic(self):
		con = sqlite3.connect(self.database)
		db = con.cursor()
		mytuples = (self.id,)
		db.execute("""SELECT woeid, timezone, last_date FROM regions WHERE id = ?""", mytuples)
		data = db.fetchall()
		db.close()
		return data[0][0], int(data[0][1].strip("UTC+")), data[0][2]

	def _query_historical(self):
		# connect to database
		con = sqlite3.connect(self.database)
		db = con.cursor()
		mytuples = (self.id,)
		db.execute("""SELECT * FROM (SELECT date, temp FROM history WHERE 
		region_id = ? ORDER BY id DESC LIMIT 5) ORDER BY date ASC""", mytuples)
		data = db.fetchall()
		db.close()
		return {to_datetime(k, time=False):v for k,v in dict(data).items()}
