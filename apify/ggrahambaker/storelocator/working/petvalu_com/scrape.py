import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()

    data = {'Host': 'us.petvalu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://us.petvalu.com/store-locator/?location=new%20york,&radius=100',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': '98',
    'Origin': 'https://us.petvalu.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'tk_ai=woo%3ApLgeTii%2Be43iIzeJv3ESzKfM'}


    r = session.post('https://us.petvalu.com/wp-admin/admin-ajax.php', data = data)
    
    print(r.content)






    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
