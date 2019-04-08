import sqlite3

class DatabaseQueries:
	"""
	Class of sqlite3 database queries. Initializes with database path.
	"""
	def __init__(self, database):
		self.database = database

	def update(self, table, destinations, data, conditions, condition_data):
		"""
		Update table with given parameters.
		Supports single/multiple column updates with no/single/multiple conditions.

		:param table: database table <string>.
		:param destinations: table columns for update <list>.
		:param data: new data <tuple>.
		:param conditions: table columns for WHERE clause <list>.
		:param condition_data: data to match conditions <tuple>.
		:return: void function.
		"""
		# connect to database
		con = sqlite3.connect(self.database)
		db = con.cursor()

		# write data to database
		if len(conditions) == 0:
			if len(destinations) == 1:
				mytuples = data + condition_data
				db.execute("""UPDATE {} SET {} = ?""".format(
					table, *destinations), mytuples)
			else:
				mytuples = data + condition_data
				db.execute(("UPDATE {} SET {} = ?" + ((", {} = ?") *
						   (len(destinations) - 1))).format(
					table, *destinations), mytuples)

		if len(conditions) == 1:
			if len(destinations) == 1:
				mytuples = data + condition_data
				db.execute("""UPDATE {} SET {} = ? WHERE {} = ?""".format(
					table, *destinations, *conditions), mytuples)
			else:
				mytuples = data + condition_data
				db.execute(("UPDATE {} SET {} = ?" + ((", {} = ?") *
						   (len(destinations) - 1)) + " WHERE {} = ?").format(
					table, *destinations, *conditions), mytuples)

		if len(conditions) > 1:
			if len(destinations) == 1:
				mytuples = data + condition_data
				db.execute(("UPDATE {} SET {} = ? WHERE {} = ?" +
						   (("AND {} = ? ") * (len(conditions) - 1))).format(
					table, *destinations, *conditions), mytuples)
			else:
				mytuples = data + condition_data
				db.execute(("UPDATE {} SET {} = ?" + ((", {} = ?") *
						   (len(destinations) - 1)) + " WHERE {} = ?" +
						   (("AND {} = ? ") * (len(conditions) - 1))).format(
					table, *destinations, *conditions), mytuples)

		con.commit()

		# close connection
		db.close()

	def select(self, table, conditions, condition_data, filters=None):
		"""
		Select data from table with given parameters.
		Supports single/multiple/all(*) selection with no/single/multiple conditions.

		:param table: database table <string>.
		:param conditions: table columns for WHERE clause <list>.
		:param condition_data: data to match conditions <tuple>.
		:param filters: table columns for selection <list>, set to None by default.
		:return: list of tuples of size one <list>, for example [(1, 2, 3)]
		"""
		# connect to database
		con = sqlite3.connect(self.database)
		db = con.cursor()

		if not filters:
			if len(conditions) == 0:
				db.execute("""SELECT * FROM {}""".format(table))
				rows = db.fetchall()
				db.close()
				return rows

			if len(conditions) > 0:
				db.execute(("SELECT * FROM {} WHERE {} = ?" +
							   (("AND {} = ? ") * (len(conditions) - 1))).format(
					table, *conditions), condition_data)
				rows = db.fetchall()
				db.close()
				return rows

		if filters and len(filters) == 1:
			if len(conditions) == 0:
				db.execute("""SELECT {} FROM {}""".format(*filters, table))
				rows = db.fetchall()
				db.close()
				return rows

			if len(conditions) > 0:
				db.execute(("SELECT {} FROM {} WHERE {} = ?" +
							(("AND {} = ? ") * (len(conditions) - 1))).format(
					*filters, table, *conditions), condition_data)
				rows = db.fetchall()
				db.close()
				return rows

		if filters and len(filters) > 1:
			if len(conditions) == 0:
				db.execute(("SELECT {}" + ((", {}") * (len(filters) - 1)) + " FROM {}").format(
					*filters, table))
				rows = db.fetchall()
				db.close()
				return rows

			if len(conditions) == 1:
				print(("SELECT {}" + ((", {}") * (len(filters) - 1)) + " FROM {} WHERE {} = ?").format(
					*filters, table, *conditions))
				db.execute(("SELECT {}" + ((", {}") * (len(filters) - 1)) + " FROM {} WHERE {} = ?").format(
					*filters, table, *conditions), condition_data)
				rows = db.fetchall()
				db.close()
				return rows

			if len(conditions) > 1:
				db.execute(("SELECT {}" + ((", {}") * (len(filters) - 1)) + " FROM {} WHERE {} = ?" +
							(("AND {} = ? ") * (len(conditions) - 1))).format(
					*filters, table, *conditions), condition_data)
				rows = db.fetchall()
				db.close()
				return rows

	def insert(self, table, destinations, data):
		"""
		Insert new data to table with given parameters.

		:param table: database table <string>.
		:param destinations: table columns for update <list>.
		:param data: new data <tuple>.
		:return: void function.
		"""
		# connect to database
		con = sqlite3.connect(self.database)
		db = con.cursor()

		# write data to database
		db.execute("INSERT INTO {}({}) VALUES({})".format(
			table, ", ".join(destinations), ",".join(list("?" * len(data)))), data)
		con.commit()

		# close connection
		db.close()

	def regions(self, table):
		"""
		Download number of regions in table.

		:param table: database table <string>.
		:return: number of regions <int>.
		"""
		con = sqlite3.connect(self.database)
		db = con.cursor()
		db.execute("""SELECT COUNT(*) FROM {}""".format(table))
		length = db.fetchall()
		db.close()
		return length[0][0]
		


