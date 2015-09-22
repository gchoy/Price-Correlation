# Price-Correlation


Used Pandas python module to calculate correlation values between income by zipcodes and prices.

Instead of creating a zipcode to latitude and longitud dictionary, modules <a href="https://pypi.python.org/pypi/geocoder">geocoder</a> or <a href="https://github.com/geopy/geopy">geopy</a> could be used, however timed requests should be used in order to avoid server timeout.