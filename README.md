# Price-Correlation


As a way of learning Pandas, I wrote a python script that uses Pandas' functions to calculate the correlation between income  and consumer goods prices for each of San Diego County Zipcodes.

To do this I used IRS income data, and created a zipcode to latitude and longitude dictionary using propietary data that linked prices to zipcodes.
This dictionary was used to avoid working with timed requests to services provided through python modules <a href="https://pypi.python.org/pypi/geocoder">geocoder</a> or <a href="https://github.com/geopy/geopy">geopy</a>. Which would have slowed down the script considerably.  

 