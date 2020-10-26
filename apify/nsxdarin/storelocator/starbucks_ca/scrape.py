import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('starbucks_ca')



weekday = datetime.datetime.today().weekday()

canada = ['43.719,-79.401','45.576,-73.587','51.045,-114.037','45.195,-75.799','53.518,-113.53','43.616,-79.655','49.87,-97.132','49.247,-123.064','43.715,-79.745','43.291,-80.046','46.868,-71.276','49.12,-122.772','45.609,-73.72','44.945,-63.088','42.953,-81.23','43.889,-79.285','43.836,-79.566','45.511,-75.64','52.146,-106.62','45.524,-73.455','43.418,-80.468','49.244,-122.977','42.283,-82.994','50.449,-104.634','49.154,-123.125','43.903,-79.428','43.452,-79.73','43.379,-79.825','46.581,-80.974','45.376,-72.002','43.95,-78.879','48.359,-71.161','46.708,-71.203','44.362,-79.689','49.067,-122.277','49.317,-122.743','46.372,-72.61','43.161,-79.255','43.546,-80.234','43.422,-80.329','43.935,-78.966','49.886,-119.44','44.281,-76.559','43.872,-79.027','49.086,-122.549','48.505,-123.406','45.717,-73.717','43.523,-80.022','47.431,-52.793','48.433,-89.312','43.469,-80.565','49.121,-122.956','42.429,-82.165','52.282,-113.801','53.533,-113.122','43.155,-80.266','45.324,-73.317','46.254,-60.024','49.697,-112.824','43.978,-78.668','43.93,-79.139','49.213,-123.995','50.68,-120.411','43.025,-79.111','49.36,-122.997','48.428,-123.35','45.451,-73.457','45.769,-73.494','44.05,-79.461','49.146,-121.877','49.267,-122.512','44.298,-78.329','44.49,-78.794','45.888,-72.512','45.787,-74.009','53.911,-122.793','46.56,-84.322','46.116,-64.812','42.975,-82.287','57.427,-110.793','49.211,-122.913','45.304,-65.956','43.866,-79.841','45.4,-72.725','53.64,-113.633','42.861,-80.355','50.041,-110.698','55.167,-118.806','51.286,-114.025','43.634,-79.982','49.263,-122.751','45.933,-66.644','45.69,-73.856','45.628,-72.938','43.996,-79.448','49.321,-123.068','42.99,-79.249','46.374,-79.43','44.252,-77.364','45.642,-74.065','46.825,-73.012','45.49,-73.823','49.847,-99.955','48.37,-68.482','45.366,-73.74','45.76,-73.597','45.045,-74.724','46.062,-71.975','44.015,-79.322','42.953,-79.881','44.31,-79.387','45.572,-73.948','44.192,-77.565','49.368,-123.17','48.185,-78.925','48.494,-81.297','45.591,-73.419','43.138,-80.736','45.267,-74.023','50.217,-119.386','42.775,-81.175','49.217,-122.346','45.383,-74.046','43.088,-80.452','42.24,-82.552','44.268,-79.592','46.26,-63.125','53.203,-105.725','48.448,-123.535','44.116,-79.623','46.015,-73.116','44.082,-79.775','53.547,-113.914','50.402,-105.55','49.489,-119.572','49.281,-122.879','49.899,-119.582','49.983,-125.271','46.104,-70.682','48.027,-77.755','45.47,-73.668','43.372,-80.985','45.457,-73.816','44.613,-79.412','48.612,-71.683','42.919,-79.045','42.218,-83.05','53.261,-113.53','45.599,-73.328','48.835,-123.709','45.433,-73.288','43.915,-80.114','50.721,-113.966','42.095,-82.556','45.353,-73.598','43.174,-79.564','45.617,-73.86','45.207,-72.147','45.534,-73.344','47.502,-52.955','45.641,-73.833','49.099,-122.66','51.175,-114.466','49.709,-124.974','46.121,-71.297','50.355,-66.107','46.083,-64.712','60.71,-135.075','43.94,-77.162','45.483,-75.212','53.744,-113.149','45.392,-73.416','44.145,-79.381','43.146,-79.439','42.214,-82.954','47.521,-52.813','45.578,-73.216','45.877,-73.412','42.113,-83.042','45.503,-73.507','44.504,-80.267','42.102,-82.732','49.267,-68.256','47.526,-52.889','44.604,-75.701','44.578,-80.914','45.684,-73.388','45.377,-73.51','42.912,-81.555','45.864,-73.784','44.5,-80.009','46.017,-73.423','42.085,-82.897','45.485,-73.602','45.517,-73.646','56.249,-120.846','45.456,-73.855','49.531,-115.758','49.024,-122.79','45.409,-74.163','51.037,-113.837','45.303,-79.277','48.928,-58.014','46.049,-64.815','53.278,-110.03','62.473,-114.384','49.726,-123.117','47.82,-69.518','43.975,-78.152','45.426,-73.886','45.453,-73.737','46.756,-71.505','43.077,-79.225','53.011,-112.837','45.57,-73.166','49.246,-122.69','42.916,-79.191','45.429,-65.929','48.446,-123.31','45.531,-73.938','50.714,-119.236','49.252,-124.797','48.434,-123.408','47.027,-65.503','43.201,-79.123','45.541,-73.903','53.352,-113.415','43.035,-81.451','53.53,-113.993','45.89,-77.316','43.044,-79.337','45.518,-73.278','45.396,-73.565','44.732,-79.902','48.421,-123.493','48.581,-123.422','44.017,-78.39','50.288,-107.795','47.385,-68.346','46.806,-71.358','44.972,-75.645','51.216,-102.464','47.446,-64.978','45.742,-74.151','45.046,-79.236','44.274,-77.005','42.863,-80.735','49.519,-96.682','45.829,-73.916','49.831,-94.429']

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    allcoords = []
    coords = []
    for coord in canada:
        x = coord.split(',')[0]
        y = coord.split(',')[1]
        latround = round(float(x), 2)
        lnground = round(float(y), 2)
        logger.info(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.starbucks.ca/bff/locations?lat=' + str(x) + '&lng=' + str(y)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        num = 0
        for item in array['stores']:
            website = 'starbucks.ca'
            store = item['storeNumber']
            name = item['name']
            phone = item['phoneNumber']
            lat = item['coordinates']['latitude']
            lng = item['coordinates']['longitude']
            add = item['address']['streetAddressLine1']
            try:
                add = add + ' ' + item['address']['streetAddressLine2']
            except:
                pass
            try:
                add = add + ' ' + item['address']['streetAddressLine3']
            except:
                pass
            add = add.strip()
            city = item['address']['city']
            state = item['address']['countrySubdivisionCode']
            country = item['address']['countryCode']
            if country == 'CA':
                num = num + 1
            zc = item['address']['postalCode']
            typ = item['brandName']
            hours = ''
            weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            today = weekdays[weekday]
            tom = weekdays[(weekday + 1) % 7]
            try:
                hours = item['schedule'][0]['dayName'] + ': ' + item['schedule'][0]['hours']
                hours = hours + '; ' + item['schedule'][1]['dayName'] + ': ' + item['schedule'][1]['hours']
                hours = hours + '; ' + item['schedule'][2]['dayName'] + ': ' + item['schedule'][2]['hours']
                hours = hours + '; ' + item['schedule'][3]['dayName'] + ': ' + item['schedule'][3]['hours']
                hours = hours + '; ' + item['schedule'][4]['dayName'] + ': ' + item['schedule'][4]['hours']
                hours = hours + '; ' + item['schedule'][5]['dayName'] + ': ' + item['schedule'][5]['hours']
                hours = hours + '; ' + item['schedule'][6]['dayName'] + ': ' + item['schedule'][6]['hours']
                hours = hours.replace('Today',today).replace('Tomorrow',tom)
            except:
                pass
            if country == 'PR':
                country = 'US'
            if country == 'CA':
                if store not in ids:
                    ids.append(store)
                    if phone is None or phone == '':
                        phone = '<MISSING>'
                    if hours is None or hours == '':
                        hours = '<MISSING>'
                    if zc is None or zc == '':
                        zc = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                else:
                    num = num - 1
        if num >= 1:
            newcoord = str(latround + 0.05) + ',' + str(lnground)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround + 0.05) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround + 0.05) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground + 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
            newcoord = str(latround - 0.05) + ',' + str(lnground - 0.05)
            if newcoord not in coords:
                coords.append(newcoord)
    while len(coords) > 0:
        x = coords[0].split(',')[0]
        y = coords[0].split(',')[1]
        coords.pop(0)
        latround = round(float(x), 2)
        lnground = round(float(y), 2)
        url = 'https://www.starbucks.ca/bff/locations?lat=' + str(x) + '&lng=' + str(y)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        num = 0
        for item in array['stores']:
            website = 'starbucks.ca'
            store = item['storeNumber']
            name = item['name']
            phone = item['phoneNumber']
            lat = item['coordinates']['latitude']
            lng = item['coordinates']['longitude']
            add = item['address']['streetAddressLine1']
            try:
                add = add + ' ' + item['address']['streetAddressLine2']
            except:
                pass
            try:
                add = add + ' ' + item['address']['streetAddressLine3']
            except:
                pass
            add = add.strip()
            city = item['address']['city']
            state = item['address']['countrySubdivisionCode']
            country = item['address']['countryCode']
            if country == 'CA':
                num = num + 1
            zc = item['address']['postalCode']
            typ = item['brandName']
            hours = ''
            weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            today = weekdays[weekday]
            tom = weekdays[(weekday + 1) % 7]
            try:
                hours = item['schedule'][0]['dayName'] + ': ' + item['schedule'][0]['hours']
                hours = hours + '; ' + item['schedule'][1]['dayName'] + ': ' + item['schedule'][1]['hours']
                hours = hours + '; ' + item['schedule'][2]['dayName'] + ': ' + item['schedule'][2]['hours']
                hours = hours + '; ' + item['schedule'][3]['dayName'] + ': ' + item['schedule'][3]['hours']
                hours = hours + '; ' + item['schedule'][4]['dayName'] + ': ' + item['schedule'][4]['hours']
                hours = hours + '; ' + item['schedule'][5]['dayName'] + ': ' + item['schedule'][5]['hours']
                hours = hours + '; ' + item['schedule'][6]['dayName'] + ': ' + item['schedule'][6]['hours']
                hours = hours.replace('Today',today).replace('Tomorrow',tom)
            except:
                pass
            if country == 'PR':
                country = 'US'
            if country == 'CA':
                if store not in ids:
                    ids.append(store)
                    if phone is None or phone == '':
                        phone = '<MISSING>'
                    if hours is None or hours == '':
                        hours = '<MISSING>'
                    if zc is None or zc == '':
                        zc = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                else:
                    num = num - 1
        if num >= 1:
            newcoord = str(latround + 0.03) + ',' + str(lnground)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround + 0.03) + ',' + str(lnground + 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround + 0.03) + ',' + str(lnground - 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground - 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround) + ',' + str(lnground + 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround - 0.03) + ',' + str(lnground)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround - 0.03) + ',' + str(lnground + 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)
            newcoord = str(latround - 0.03) + ',' + str(lnground - 0.03)
            if newcoord not in allcoords:
                coords.append(newcoord)
                allcoords.append(newcoord)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
