import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re, json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"
                         ])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
all=[]
def fetch_data(): 
    r=session.get("https://www.sbe.com/hotels/brands/ciel-spa")
    res = r.text.split('<script type="application/ld+json">')[2].split('</script>',1)[0]    
    res = json.loads(res)    
    title = res['name']
    street = res['address']['streetAddress']
    city  = res['address']['addressLocality']
    state = res['address']['addressRegion']
    pcode = res['address']['postalCode']
    phone = res['telephone']
    lat = r.text.split('{"lat":"',1)[1].split('"',1)[0]
    longt = r.text.split('"lng":"',1)[1].split('"',1)[0]
    hours = '<MISSING>'
  
    all.append([
            "https://www.sbe.com/hotels/brands/ciel-spa",
            'https://www.sbe.com/hotels/brands/ciel-spa',
            title,
            street,
            city,
            state,
            pcode,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            longt,  # long
            hours,  # timing
           ])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

