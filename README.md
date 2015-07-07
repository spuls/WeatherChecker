WeatherChecker
=======

Check the accuracy of weather forecasts.

## Forecasts
So far there are 3 forecast suppliers supported:
* Wetter.com
* OpenWeatherMap
* ForecastIO

The forecast is taken for three days with each four forecast times points.

The current weather information is obtained via OpenWeatherMap.

## Dependencies
For each forecast supplier, the API information is needed. This has to be obtained by each developer. It is not provided in this project.

For Wetter.com and OpenWeatherMap the implemented API-access is standalone. For ForecastIO a library has to be installed from ForecastIO (not provided here).