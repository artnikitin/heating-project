# Weather monitoring service

Weather analysis and central heating supply/cut date forecasting for CIS cities (Russia, Ukraine, Belarus, Kazakhstan). Hosted on [heatingproject.org](https://heatingproject.org).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Be sure to install Python 3.6. For other modules and libraries run:

```
$ pip install -r requirements.txt
```

### Installing

Download the repository manually or run:

```
$ git clone https://github.com/artnikitin/weather-monitoring-service.git
$ cd weather-monitoring-service
$ export FLASK_APP=application.py
$ export API_KEY_OW={enter OpenWeatherMap token here}
$ flask run
```

## Usage

Select a city from the table and get heating date forecast on the next page. A 10-day weather window is displayed in a Plotly graph. FAQ section answers frequently asked questions about central heating in CIS countries.

![Alt text](https://media.giphy.com/media/dBmWDCljNyLb9Xzxcc/giphy.gif)

### API

Weather data is downloaded with [OpenWeatherMap](https://openweathermap.org). Be sure to get a token from this service to use application. Set as environment variable.

To make calculations for heating date run:

```
$ python3 forecast.py
```

It gathers historical weather data, forecast for current day and four-day forecast, blends it and searches for condition matching. For CIS cities the condition is such, that mean temperature (day + night) must remain above or below 8°С for five days in a row. New data is available every three hours (UTC).

```
>>> blended_data = [historical weather] +/ 
[today forecast] +/ 
[4-day forecast]
```
Current temperature for different time intervals is saved to database. In total there are eight 3-hour intervals in range '00-21'. Forecast for today can be calculated by blending temperature at previous (saved) intervals with intraday forecast.

```
>>> today forecast = [saved intervals] +/
[forecast intervals]
```
**forecast.py** is intended to run in background on a server every 3-hours. See bash files, that handle this work:
```
$ ./forecast.sh
```
After running **forecast.py** this bash file runs another one called **misfired.sh**, that checks if there are regions for which API didn't give a response (they are written to **misfired.txt** file) and reruns **forecast.py** after 10 minutes for only those misfired regions. You can run it separately:
```
$ ./misfired.sh
```
A cron on a Linux machine for this job will look like this:
```
5 2-23/3 * * * /path/to/forecast.sh
```
### Database queries
This project uses sqlite3 with helper functions for easier database access. See **DatabaseQueries** class in **database_queries.py** for more information.
Basic usage example for selection:
```
sql_params = {'table': 'table_name',
              'conditions': ['WHERE_columns'],
              'condition_data': (WHERE_data,),
              'filters': ['selection_columns']}
              
rows = db.select(**sql_params)
```
### Dynamic Plotly graph generation
Graphs are created dynamically with javascript only, no need to install any external libraries in Python (although don't forget to include the javascript source for Plotly in the header). Just pass x and y axis values with Jinja. Here is the full script as in **region.html** file:
```

<div id="myDiv"><!-- Plotly chart --></div>

<!-- Script for plotly graph -->
<script>
var trace1 = {
  type: 'scatter',
  x: {{ x | safe }},
  y: {{ y | safe }},
  marker: {
      color: '#C8A2C8',
      line: {
          width: 1.5
      }
  }
};

var data = [ trace1 ];

var layout = {
  title: {
    {% if 'Влад' in region_title %}
    text: 'Погода во {{ region_title }}',
    {% else %}
    text: 'Погода в {{ region_title }}',
    {% endif %}
    font: {
      family: 'Roboto, sans-serif',
      size: 20,
    },
  },

  yaxis: {
    title: {
      text: 'температура (°С)',
      font: {
        family: 'Roboto, sans-serif',
        size: 15,
        color: '#7f7f7f'
      }
    }
  }
};

Plotly.newPlot(
'myDiv', data, layout, {responsive: true});
</script>
```
### Internal API for mobile app
A mobile app gets access to website heating date calculations through a GET request:
```
yourdomain.com/urlforjsonqueries?region='Kiev'

```
Returns data in JSON format as follows:
```
[{"heating_date":"2019-04-13",
"heating_date_RU":"13 \u0430\u043f\u0440\u0435\u043b\u044f",
"last_date":0,
"latin":"Kiev",
"name":"\u041a\u0438\u0435\u0432",
"name_RU":"\u041a\u0438\u0435\u0432\u0435"}]
```
See **application.py** for details.

## Built With

* Python 3.6
* Flask
* SQLite3

## Authors

* **Artem Nikitin** - [artnikitin](https://github.com/artnikitin)

## License

This project is licensed under the MIT License - see the [LICENSE.md](/LICENSE.md) file for details
