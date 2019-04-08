from flask import Flask, jsonify, request, render_template
from forecast_functions import spring
from time_functions import to_datetime, date_convert_RU

from database_queries import DatabaseQueries

db = DatabaseQueries('weather.db')

app = Flask(__name__)

@app.route("/")
def index():
	"""
	Renders index.html with list of all regions for table.

	:return: sorted region names (list of tuples) <list>, page title <string>.
	"""
	region_names_params = {'table': 'regions',
							   'conditions': [],
							   'condition_data': (),
							   'filters': ['name', 'country']}

	# returns a list of tuples
	region_names = db.select(**region_names_params)
	# page title
	title = "Прогноз включения отопления"

	return render_template("index.html", regions=sorted(region_names), title=title)

@app.route("/region")
def region():
	"""
	Renders region.html, page for chosen region.

	:return: sorted region names (list of tuples) <list>, page title <string>,
	heating date <string>, title for graph <string>, x and y coordinate data for graph.
	"""
	region_names_params = {'table': 'regions',
						   'conditions': [],
						   'condition_data': (),
						   'filters': ['name', 'country']}

	# returns a list of tuples
	region_names = db.select(**region_names_params)

	# parse region name via GET request
	region = request.args.get("region")

	# download heating date
	heating_date_params = {'table': 'regions',
						   'conditions': ['name'],
						   'condition_data': (region,),
						   'filters': ['heating_date_RU', 'name_RU', 'id']}

	# returns a list of tuples
	heating_data = db.select(**heating_date_params)

	# set message for heating date
	heating_message = None

	heating_date = heating_data[0][0]
	heating_region = heating_data[0][1]
	region_id = heating_data[0][2]

	# russian language sensitive cases for season and no heating date
	if not heating_date and spring():
		if 'Влад' in heating_region:
			heating_message = "Отопление во {} в ближайшее время не отключат.*".format(heating_region)
		else:
			heating_message = "Отопление в {} в ближайшее время не отключат.*".format(heating_region)
	if not heating_date and not spring():
		if 'Влад' in heating_region:
			heating_message = "Отопление во {} в ближайшее время не включат.*".format(heating_region)
		else:
			heating_message = "Отопление в {} в ближайшее время не включат.*".format(heating_region)

	# russian language sensitive cases for season and heating date
	if heating_date and spring():
		if 'Влад' in heating_region:
			heating_message = "Отопление во {} отключат {}.*".format(heating_region, heating_date)
		else:
			heating_message = "Отопление в {} отключат {}.*".format(heating_region, heating_date)
	if heating_date and not spring():
		if 'Влад' in heating_region:
			heating_message = "Отопление во {} включат {}.*".format(heating_region, heating_date)
		else:
			heating_message = "Отопление в {} включат {}.*".format(heating_region, heating_date)

	# page title
	if 'Влад' in heating_region:
		title = "Отопление во {}".format(heating_region)
	else:
		title = "Отопление в {}".format(heating_region)

	# download graphing data
	graph_params = {'table': 'graph',
						   'conditions': ['region_id'],
						   'condition_data': (region_id,),
						   'filters': ['temp_{}'.format(x) for x in range(1, 11)] +
									  ['date_{}'.format(x) for x in range(1, 11)]
					}

	# returns a list of tuples
	graph_data = db.select(**graph_params)

	x = [date_convert_RU(to_datetime(x, time=False), short=True) for x in list(graph_data[0])[10:]]
	y = list(graph_data[0])[:10]
	
	return render_template("region.html", regions=sorted(region_names), title=title,
						   heating_date=heating_message, region_title=heating_region, x=x, y=y)

@app.route("/jsonforapp")
def json():
	"""
	Internal API for mobile app. Output region data in JSON for given region via
	GET request. If no region specified, return data for all regions.
	Example: /jsonforapp?region=Moscow.

	:return: JSON object with region data.
	"""
	# choose json data to show
	filters = ['name', 'name_RU', 'latin', 'heating_date',
			   'heating_date_RU', 'last_date']

	if request.args.get("region"):
		region = request.args.get("region")

		# download region data
		region_data_params = {'table': 'regions',
							   'conditions': ['latin'],
							   'condition_data': (region,),
							   'filters': filters}

		# returns a list of tuples
		region_data = db.select(**region_data_params)
	else:
		# download data for json for all regions
		region_data_params = {'table': 'regions',
					   'conditions': [],
					   'condition_data': (),
					   'filters': filters}

		# returns a list of tuples
		region_data = db.select(**region_data_params)

	json_for_app = [dict([(x, y) for x, y in zip(filters, item)]) for item in region_data]

	return jsonify(json_for_app)


if __name__ == "__main__":
	app.run()
