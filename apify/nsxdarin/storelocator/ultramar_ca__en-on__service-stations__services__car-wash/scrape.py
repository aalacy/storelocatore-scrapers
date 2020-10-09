import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    infos = []
    canada = ['43.719,-79.401','45.576,-73.587','51.045,-114.037','45.195,-75.799','53.518,-113.53','43.616,-79.655','49.87,-97.132','49.247,-123.064','43.715,-79.745','43.291,-80.046','46.868,-71.276','49.12,-122.772','45.609,-73.72','44.945,-63.088','42.953,-81.23','43.889,-79.285','43.836,-79.566','45.511,-75.64','52.146,-106.62','45.524,-73.455','43.418,-80.468','49.244,-122.977','42.283,-82.994','50.449,-104.634','49.154,-123.125','43.903,-79.428','43.452,-79.73','43.379,-79.825','46.581,-80.974','45.376,-72.002','43.95,-78.879','48.359,-71.161','46.708,-71.203','44.362,-79.689','49.067,-122.277','49.317,-122.743','46.372,-72.61','43.161,-79.255','43.546,-80.234','43.422,-80.329','43.935,-78.966','49.886,-119.44','44.281,-76.559','43.872,-79.027','49.086,-122.549','48.505,-123.406','45.717,-73.717','43.523,-80.022','47.431,-52.793','48.433,-89.312','43.469,-80.565','49.121,-122.956','42.429,-82.165','52.282,-113.801','53.533,-113.122','43.155,-80.266','45.324,-73.317','46.254,-60.024','49.697,-112.824','43.978,-78.668','43.93,-79.139','49.213,-123.995','50.68,-120.411','43.025,-79.111','49.36,-122.997','48.428,-123.35','45.451,-73.457','45.769,-73.494','44.05,-79.461','49.146,-121.877','49.267,-122.512','44.298,-78.329','44.49,-78.794','45.888,-72.512','45.787,-74.009','53.911,-122.793','46.56,-84.322','46.116,-64.812','42.975,-82.287','57.427,-110.793','49.211,-122.913','45.304,-65.956','43.866,-79.841','45.4,-72.725','53.64,-113.633','42.861,-80.355','50.041,-110.698','55.167,-118.806','51.286,-114.025','43.634,-79.982','49.263,-122.751','45.933,-66.644','45.69,-73.856','45.628,-72.938','43.996,-79.448','49.321,-123.068','42.99,-79.249','46.374,-79.43','44.252,-77.364','45.642,-74.065','46.825,-73.012','45.49,-73.823','49.847,-99.955','48.37,-68.482','45.366,-73.74','45.76,-73.597','45.045,-74.724','46.062,-71.975','44.015,-79.322','42.953,-79.881','44.31,-79.387','45.572,-73.948','44.192,-77.565','49.368,-123.17','48.185,-78.925','48.494,-81.297','45.591,-73.419','43.138,-80.736','45.267,-74.023','50.217,-119.386','42.775,-81.175','49.217,-122.346','45.383,-74.046','43.088,-80.452','42.24,-82.552','44.268,-79.592','46.26,-63.125','53.203,-105.725','48.448,-123.535','44.116,-79.623','46.015,-73.116','44.082,-79.775','53.547,-113.914','50.402,-105.55','49.489,-119.572','49.281,-122.879','49.899,-119.582','49.983,-125.271','46.104,-70.682','48.027,-77.755','45.47,-73.668','43.372,-80.985','45.457,-73.816','44.613,-79.412','48.612,-71.683','42.919,-79.045','42.218,-83.05','53.261,-113.53','45.599,-73.328','48.835,-123.709','45.433,-73.288','43.915,-80.114','50.721,-113.966','42.095,-82.556','45.353,-73.598','43.174,-79.564','45.617,-73.86','45.207,-72.147','45.534,-73.344','47.502,-52.955','45.641,-73.833','49.099,-122.66','51.175,-114.466','49.709,-124.974','46.121,-71.297','50.355,-66.107','46.083,-64.712','60.71,-135.075','43.94,-77.162','45.483,-75.212','53.744,-113.149','45.392,-73.416','44.145,-79.381','43.146,-79.439','42.214,-82.954','47.521,-52.813','45.578,-73.216','45.877,-73.412','42.113,-83.042','45.503,-73.507','44.504,-80.267','42.102,-82.732','49.267,-68.256','47.526,-52.889','44.604,-75.701','44.578,-80.914','45.684,-73.388','45.377,-73.51','42.912,-81.555','45.864,-73.784','44.5,-80.009','46.017,-73.423','42.085,-82.897','45.485,-73.602','45.517,-73.646','56.249,-120.846','45.456,-73.855','49.531,-115.758','49.024,-122.79','45.409,-74.163','51.037,-113.837','45.303,-79.277','48.928,-58.014','46.049,-64.815','53.278,-110.03','62.473,-114.384','49.726,-123.117','47.82,-69.518','43.975,-78.152','45.426,-73.886','45.453,-73.737','46.756,-71.505','43.077,-79.225','53.011,-112.837','45.57,-73.166','49.246,-122.69','42.916,-79.191','45.429,-65.929','48.446,-123.31','45.531,-73.938','50.714,-119.236','49.252,-124.797','48.434,-123.408','47.027,-65.503','43.201,-79.123','45.541,-73.903','53.352,-113.415','43.035,-81.451','53.53,-113.993','45.89,-77.316','43.044,-79.337','45.518,-73.278','45.396,-73.565','44.732,-79.902','48.421,-123.493','48.581,-123.422','44.017,-78.39','50.288,-107.795','47.385,-68.346','46.806,-71.358','44.972,-75.645','51.216,-102.464','47.446,-64.978','45.742,-74.151','45.046,-79.236','44.274,-77.005','42.863,-80.735','49.519,-96.682','45.829,-73.916','49.831,-94.429','54.404,-110.262','46.406,-63.781','52.298,-114.115','48.943,-64.564','45.371,-73.985','50.568,-111.9','45.766,-73.83','46.396,-80.086','52.769,-108.275','48.798,-67.474','48.771,-72.215','48.958,-55.704','46.544,-75.625','49.679,-124.918','51.086,-115.351','45.638,-73.801','45.817,-77.111','46.044,-73.473','51.051,-113.389','44.402,-81.363','55.75,-97.848','45.903,-73.323','45.205,-72.778','50.583,-113.863','46.439,-70.999','49.969,-98.286','42.965,-81.051','45.243,-76.28','49.879,-124.542','43.696,-80.98','45.307,-73.742','52.469,-113.72','46.324,-72.33','45.872,-74.057','48.409,-123.684','50.088,-119.406','45.967,-74.124','44.321,-77.803','45.29,-73.882','45.665,-74.304','48.654,-77.934','45.399,-74.981','43.032,-80.881','52.967,-113.386','42.731,-81.093','49.181,-97.938','44.204,-80.901','49.315,-124.317','44.883,-79.336','45.348,-63.271','54.287,-130.311','55.76,-120.238','45.657,-73.304','47.254,-61.957','47.627,-65.58','50.098,-122.989','44.112,-77.759','53.284,-109.986','48.948,-54.553','48.65,-123.407','45.382,-65.979','54.455,-128.572','49.597,-119.686','45.719,-75.68','49.143,-102.987','43.76,-80.135','44.247,-81.49','46.942,-70.521','48.643,-123.434','59.253,-116.599','46.061,-73.759','52.325,-106.582','48.279,-74.438','44.603,-80.743','49.666,-103.847','44.958,-75.253','45.391,-73.959','52.133,-122.152','46.405,-82.633','45.434,-73.161','45.576,-75.765','45.371,-73.915','50.227,-119.194','45.139,-76.144','43.16,-81.896','49.488,-117.293','48.481,-123.47','44.242,-65.149','50.149,-96.89','45.612,-74.62','48.702,-72.454','45.875,-74.187','46.07,-74.287','47.005,-71.852','49.484,-123.793','54.134,-115.65','43.344,-81.406','48.474,-72.234','45.96,-73.741','47.459,-79.711','53.386,-117.593','52.988,-122.477','53.8,-113.639','46.177,-64.995','44.297,-80.53','46.217,-63.096','46.163,-74.583','52.291,-106.658','45.673,-73.761','45.418,-73.347','44.179,-81.247','45.825,-64.204','45.668,-73.783','52.388,-113.802','46.052,-73.405','46.78,-71.691','45.835,-66.502','51.792,-114.125','43.602,-81.307','45.932,-74.003','45.59,-62.643','45.296,-72.681','44.79,-79.915','49.343,-124.428','45.289,-72.977','43.434,-81.225','45.427,-76.358','44.895,-76.017','45.084,-71.863','43.913,-80.888','49.192,-98.106','44.018,-80.061','48.989,-123.823','44.378,-64.517','51.15,-100.04','49.796,-112.151','45.537,-73.214','44.811,-81.204','53.584,-116.461','47.139,-71.41','49.395,-82.412','47.772,-70.055','45.473,-76.686','49.724,-112.617','46.216,-72.603','47.644,-52.827','54.062,-128.668','44.081,-80.197','53.346,-60.499','45.257,-73.634','49.276,-117.654','51.413,-112.643','48.209,-80.079','45.247,-74.29','47.659,-52.76','45.818,-73.264','45.687,-75.979','51.174,-115.568','52.03,-113.959','46.98,-71.296','43.016,-82.089','45.485,-74.37','49.792,-92.772','63.76,-68.46','48.621,-93.389','49.075,-117.732','46.833,-71.63','44.153,-81.024','45.639,-72.539','43.736,-81.708','46.913,-71.148','43.669,-81.476','50.984,-118.188','48.328,-64.813','49.88,-74.252','42.772,-80.987','45.374,-73.544','49.66,-115.982','42.74,-80.788','47.045,-71.148','48.821,-79.227','43.254,-81.143','53.208,-114.985','52.676,-113.581','52.961,-66.937','46.691,-71.711','45.8,-66.605','46.255,-72.935','47.412,-70.715','50.114,-120.784','43.448,-81.611','45.672,-74.452','45.301,-74.202','44.464,-80.396','45.481,-73.647','45.356,-72.589','45.531,-75.867','48.002,-66.634','56.227,-117.316','44.402,-81.2','49.78,-67.272','45.774,-71.929','45.342,-74.113','45.534,-74.014','46.2,-64.516','55.278,-114.776','46.58,-71.253','52.377,-114.924','48.557,-58.562','53.354,-113.726','46.22,-71.775','43.839,-66.106','49.133,-66.332','45.498,-73.975','45.35,-80.037','43.149,-81.636','45.344,-73.456','46.173,-73.43','48.174,-54.031','46.231,-70.775','48.584,-68.189','45.203,-78.404','45.072,-64.519','52.839,-110.845','47.733,-65.867','49.371,-121.468','48.48,-67.43','46.358,-66.997','46.601,-71.517','49.258,-121.837','45.955,-73.881','44.48,-77.273','46.9,-71.554','47.576,-53.316','46.173,-71.886','52.862,-104.597','52.319,-112.719','49.134,-97.723','44.901,-76.251','48.415,-89.506','45.726,-73.49','45.94,-73.401','45.408,-72.986','52.202,-105.121','45.597,-76.216','45.776,-73.354','53.988,-111.282','48.533,-71.11','46.471,-72.67','42.884,-82.135']
    locs = []
    for item in canada:
        lat = item.split(',')[0]
        lng = item.split(',')[1]
        print(('Pulling Coordinates %s, %s...' % (lat, lng)))
        url = 'https://www.ultramar.ca/en-on/find-services-stations/?latitude=' + lat + '&longitude=' + lng + '&is_ultralave=on'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if 'data-lat="' in line:
                items = line.split('data-title="')
                for item in items:
                    if 'data-lng="' in item:
                        lat = ''
                        lng = ''
                        country = 'CA'
                        website = 'ultramar.ca/en-on/service-stations/services/car-wash'
                        loc = 'https://ultramar.ca' + item.split('data-details_url="')[1].split('"')[0]
                        state = ''
                        phone = ''
                        zc = ''
                        name = ''
                        store = '<MISSING>'
                        typ = 'Car Wash'
                        hours = ''
                        add = ''
                        city = ''
                        r2 = session.get(loc, headers=headers)
                        lines = r2.iter_lines()
                        print(loc)
                        for line2 in lines:
                            line2 = str(line2.decode('utf-8'))
                            if '<h1 class="station__title"' in line2:
                                name = line2.split('<h1 class="station__title"')[1].split('<')[0]
                            if 'var map = initMap(' in line2:
                                lat = line2.split(',')[1].strip()
                                lng = line2.split(',')[2].strip().split(')')[0]
                            if '<span class="station__coordinates-line">' in line2:
                                add = line2.split('<span class="station__coordinates-line">')[1].split('<')[0]
                                g = next(lines)
                                g = str(g.decode('utf-8'))
                                city = g.split('>')[1].split(',')[0]
                                state = g.split(', ')[1].split(' ')[0]
                                zc = g.split(', ')[1].split('<')[0].split(' ',1)[1]
                            if 'station__coordinates-line" href="tel:' in line2:
                                phone = line2.split('station__coordinates-line" href="tel:')[1].split('"')[0]
                            if 'Open 24h' in line2:
                                hours = 'Mon-Sun: 24 Hours'
                            if 'day</span>' in line2:
                                if hours == '':
                                    hours = line2.split('<span>')[1].split('<')[0] + ': '
                                else:
                                    hours = hours + '; ' + line2.split('<span>')[1].split('<')[0]
                                g = next(lines)
                                g = str(g.decode('utf-8'))
                                hours = hours + g.split('<span>')[1].split('<')[0]
                        add = add.replace('>','')
                        info = lat + '|' + lng + '|' + add
                        if info not in infos:
                            infos.append(info)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
