import time
import csv
import requests
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('murphyusa_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    data=[]
    session = requests.Session()
    count=0
    state_list=['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY', 'LA','ME','MD', 'MA','MI',
                'MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA',
                'WA','WV','WI','WY']
    url = 'http://locator.murphyusa.com/MapServices.asmx/GetLocations'
    headers = {
            'Host': 'locator.murphyusa.com',
            'Connection': 'keep-alive',
            'Content-Length': '32',
            'Origin': 'http://locator.murphyusa.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'http://locator.murphyusa.com/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    for state in state_list:
        api_data = {"stateAbbr": state, "filter": None}
        r = session.post(url, headers=headers, json=api_data, allow_redirects=False)
        if r.status_code == 200:
            json_res = r.json()
            for location in json_res['d']:
                store_num= location['StoreNum']

                street_addr = location['Address']
                lat =location['Lat']
                if lat == "" or lat== " ":
                    lat = '<MISSING>'
                lon = location['Long']
                if lon == "" or lon == " ":
                    lon = '<MISSING>'
                phone = location['Phone']
                if phone == "" or phone == " " or phone == None or phone == 'null':
                    phone = '<MISSING>'
                city = location['City']
                if city == "" or city == " ":
                    city = '<MISSING>'
                state= location['State']
                if state == "" or state == " ":
                    state = '<MISSING>'
                zipcode = location['Zip']
                if zipcode == "" or zipcode == " ":
                    zipcode = '<MISSING>'
                is_express =location['IsExpress']
                if is_express == True:
                    loc_type= 'Murphy Express'
                else:
                    loc_type ='Murphy USA'
                loc_name = loc_type + " " + '#' + str(store_num)
                url2 = "http://locator.murphyusa.com/MapServices.asmx/StoreDetailHtml"
                headers2 = {
                    'Host': 'locator.murphyusa.com',
                    'Connection': 'keep-alive',
                    'Content-Length': '30',
                    'Origin': 'http://locator.murphyusa.com',
                    'X-Requested-With': 'XMLHttpRequest',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Accept': '*/*',
                    'Referer': 'http://locator.murphyusa.com/',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
                api_data = {"storeNum":store_num,"distance":0}
                r2 = session.post(url2, headers=headers2, json=api_data, verify=False)
                if r2.status_code == 200:
                    json_res2 = r2.json()
                    res = json_res2['d']
                    hours_of_op = res.split("</caption>")[1].split('</table>')[0]
                    hours_of_op = re.sub(r'</th><td>|</td><th>|\r\n<tr><th>|</td></tr>|</td></tr>\r\n', " ", hours_of_op)

                data.append([
                     'https://www.murphyusa.com/',
                     'http://locator.murphyusa.com/',
                      loc_name,
                      street_addr,
                      city,
                      state,
                      zipcode,
                      'US',
                      store_num,
                      phone,
                      loc_type,
                      lat,
                      lon,
                      hours_of_op
                    ])
                count=count+1
                logger.info(count)

    time.sleep(3)
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()