mess = 'Москва, 19.00'

city, hour = mess.split(sep=', ')
hour = hour.split(sep='.')[0]
print(type(city), type(hour))
