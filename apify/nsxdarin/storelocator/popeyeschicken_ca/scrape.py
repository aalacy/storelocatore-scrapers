import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('popeyeschicken_ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    canada = ['43.719,-79.401','45.576,-73.587','51.045,-114.037','45.195,-75.799','53.518,-113.53','43.616,-79.655','49.87,-97.132','49.247,-123.064','43.715,-79.745','43.291,-80.046','46.868,-71.276','49.12,-122.772','45.609,-73.72','44.945,-63.088','42.953,-81.23','43.889,-79.285','43.836,-79.566','45.511,-75.64','52.146,-106.62','45.524,-73.455','43.418,-80.468','49.244,-122.977','42.283,-82.994','50.449,-104.634','49.154,-123.125','43.903,-79.428','43.452,-79.73','43.379,-79.825','46.581,-80.974','45.376,-72.002','43.95,-78.879','48.359,-71.161','46.708,-71.203','44.362,-79.689','49.067,-122.277','49.317,-122.743','46.372,-72.61','43.161,-79.255','43.546,-80.234','43.422,-80.329','43.935,-78.966','49.886,-119.44','44.281,-76.559','43.872,-79.027','49.086,-122.549','48.505,-123.406','45.717,-73.717','43.523,-80.022','47.431,-52.793','48.433,-89.312','43.469,-80.565','49.121,-122.956','42.429,-82.165','52.282,-113.801','53.533,-113.122','43.155,-80.266','45.324,-73.317','46.254,-60.024','49.697,-112.824','43.978,-78.668','43.93,-79.139','49.213,-123.995','50.68,-120.411','43.025,-79.111','49.36,-122.997','48.428,-123.35','45.451,-73.457','45.769,-73.494','44.05,-79.461','49.146,-121.877','49.267,-122.512','44.298,-78.329','44.49,-78.794','45.888,-72.512','45.787,-74.009','53.911,-122.793','46.56,-84.322','46.116,-64.812','42.975,-82.287','57.427,-110.793','49.211,-122.913','45.304,-65.956','43.866,-79.841','45.4,-72.725','53.64,-113.633','42.861,-80.355','50.041,-110.698','55.167,-118.806','51.286,-114.025','43.634,-79.982','49.263,-122.751','45.933,-66.644','45.69,-73.856','45.628,-72.938','43.996,-79.448','49.321,-123.068','42.99,-79.249','46.374,-79.43','44.252,-77.364','45.642,-74.065','46.825,-73.012','45.49,-73.823','49.847,-99.955','48.37,-68.482','45.366,-73.74','45.76,-73.597','45.045,-74.724','46.062,-71.975','44.015,-79.322','42.953,-79.881','44.31,-79.387','45.572,-73.948','44.192,-77.565','49.368,-123.17','48.185,-78.925','48.494,-81.297','45.591,-73.419','43.138,-80.736','45.267,-74.023','50.217,-119.386','42.775,-81.175','49.217,-122.346','45.383,-74.046','43.088,-80.452','42.24,-82.552','44.268,-79.592','46.26,-63.125','53.203,-105.725','48.448,-123.535','44.116,-79.623','46.015,-73.116','44.082,-79.775','53.547,-113.914','50.402,-105.55','49.489,-119.572','49.281,-122.879','49.899,-119.582','49.983,-125.271','46.104,-70.682','48.027,-77.755','45.47,-73.668','43.372,-80.985','45.457,-73.816','44.613,-79.412','48.612,-71.683','42.919,-79.045','42.218,-83.05','53.261,-113.53','45.599,-73.328','48.835,-123.709','45.433,-73.288','43.915,-80.114','50.721,-113.966','42.095,-82.556','45.353,-73.598','43.174,-79.564','45.617,-73.86','45.207,-72.147','45.534,-73.344','47.502,-52.955','45.641,-73.833','49.099,-122.66','51.175,-114.466','49.709,-124.974','46.121,-71.297','50.355,-66.107','46.083,-64.712','60.71,-135.075','43.94,-77.162','45.483,-75.212','53.744,-113.149','45.392,-73.416','44.145,-79.381','43.146,-79.439','42.214,-82.954','47.521,-52.813','45.578,-73.216','45.877,-73.412','42.113,-83.042','45.503,-73.507','44.504,-80.267','42.102,-82.732','49.267,-68.256','47.526,-52.889','44.604,-75.701','44.578,-80.914','45.684,-73.388','45.377,-73.51','42.912,-81.555','45.864,-73.784','44.5,-80.009','46.017,-73.423','42.085,-82.897','45.485,-73.602','45.517,-73.646','56.249,-120.846','45.456,-73.855','49.531,-115.758','49.024,-122.79','45.409,-74.163']
    for item in canada:
        lat = item.split(',')[0]
        lng = item.split(',')[1]
        #logger.info('Pulling Coordinates %s-%s...' % (lat, lng))
        url = 'https://hosted.where2getit.com/popeyes/ajax?&xml_request=<request><appkey>17DA36EB-B7DF-3E53-B01F-391651032194<%2Fappkey><formdata+id%3D"locatorsearch"><dataview>store_default<%2Fdataview><limit>100<%2Flimit><geolocs><geoloc><addressline><%2Faddressline><longitude>' + lng + '<%2Flongitude><latitude>' + lat + '<%2Flatitude><country>CA<%2Fcountry><%2Fgeoloc><%2Fgeolocs><where><operatingstatus><or><eq>Operating<%2Feq><eq>Reopenings<%2Feq><%2For><%2Foperatingstatus><%2Fwhere><searchradius>250<%2Fsearchradius><%2Fformdata><%2Frequest>'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<address1>' in line:
                add = line.split('<address1>')[1].split('<')[0]
            if '<address2>' in line:
                add = add + ' ' + line.split('<address2>')[1].split('<')[0]
                add = add.strip()
                if ' a/k' in add:
                    add = add.split(' a/k')[0]
                if ' a/K' in add:
                    add = add.split(' a/K')[0]
                if ' A/k' in add:
                    add = add.split(' A/k')[0]
                if ' A/K' in add:
                    add = add.split(' A/K')[0]
            if '<city>' in line:
                city = line.split('<city>')[1].split('<')[0]
            if '<country>' in line:
                country = line.split('<country>')[1].split('<')[0]
            if '<latitude>' in line:
                lat = line.split('<latitude>')[1].split('<')[0]
            if '<longitude>' in line:
                lng = line.split('<longitude>')[1].split('<')[0]
            if '<province>' in line:
                state = line.split('<province>')[1].split('<')[0]
            if '<postalcode>' in line:
                zc = line.split('<postalcode>')[1].split('<')[0]
            if '<phone>' in line:
                phone = line.split('<phone>')[1].split('<')[0]
                name = "Popeye's"
                typ = 'Restaurant'
            if '<clientkey>' in line:
                store = line.split('<clientkey>')[1].split('<')[0]
            if '<v_hours_dinein_close_fri>' in line:
                friclose = line.split('<v_hours_dinein_close_fri>')[1].split('<')[0]
            if '<v_hours_dinein_close_thu>' in line:
                thuclose = line.split('<v_hours_dinein_close_thu>')[1].split('<')[0]
            if '<v_hours_dinein_close_wed>' in line:
                wedclose = line.split('<v_hours_dinein_close_wed>')[1].split('<')[0]
            if '<v_hours_dinein_close_tue>' in line:
                tueclose = line.split('<v_hours_dinein_close_tue>')[1].split('<')[0]
            if '<v_hours_dinein_close_mon>' in line:
                monclose = line.split('<v_hours_dinein_close_mon>')[1].split('<')[0]
            if '<v_hours_dinein_close_sat>' in line:
                satclose = line.split('<v_hours_dinein_close_sat>')[1].split('<')[0]
            if '<v_hours_dinein_close_sun>' in line:
                sunclose = line.split('<v_hours_dinein_close_sun>')[1].split('<')[0]
            if '<v_hours_dinein_open_fri>' in line:
                friopen = line.split('<v_hours_dinein_open_fri>')[1].split('<')[0]
            if '<v_hours_dinein_open_thu>' in line:
                thuopen = line.split('<v_hours_dinein_open_thu>')[1].split('<')[0]
            if '<v_hours_dinein_open_wed>' in line:
                wedopen = line.split('<v_hours_dinein_open_wed>')[1].split('<')[0]
            if '<v_hours_dinein_open_tue>' in line:
                tueopen = line.split('<v_hours_dinein_open_tue>')[1].split('<')[0]
            if '<v_hours_dinein_open_mon>' in line:
                monopen = line.split('<v_hours_dinein_open_mon>')[1].split('<')[0]
            if '<v_hours_dinein_open_sat>' in line:
                satopen = line.split('<v_hours_dinein_open_sat>')[1].split('<')[0]
            if '<v_hours_dinein_open_sun>' in line:
                sunopen = line.split('<v_hours_dinein_open_sun>')[1].split('<')[0]
            if '</poi>' in line:
                website = 'popeyeschicken.ca'
                loc = '<MISSING>'
                if monopen != '':
                    hours = 'Mon: ' + monopen + '-' + monclose
                    hours = hours + '; Tue: ' + tueopen + '-' + tueclose
                    hours = hours + '; Wed: ' + wedopen + '-' + wedclose
                    hours = hours + '; Thu: ' + thuopen + '-' + thuclose
                    hours = hours + '; Fri: ' + friopen + '-' + friclose
                    hours = hours + '; Sat: ' + satopen + '-' + satclose
                    hours = hours + '; Sun: ' + sunopen + '-' + sunclose
                else:
                    hours = '<MISSING>'
                if zc == '':
                    zc = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if store not in ids and country == 'CA':
                    ids.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
