import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]

    res= session.get("https://www.sunriseseniorliving.com/communities.aspx?zip=10001&radius=10000&cat=csb")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('a', {'class': 'btn-primary--small-reverse'})
    stores+= soup.find_all('a', {'data-track-event': 'US Community Results Page Quebec Community Page Button'})
    print(len(stores))

    for store in stores:
        url="https://www.sunriseseniorliving.com"+store.get('href')

        if url=="https://www.sunriseseniorliving.com/care-services/home-care.aspx":
            continue
        elif url =="https://www.sunriseseniorliving.com/communities/sunrise-of-beaconsfield.aspx":
            url="https://www.sunrisequebec.ca/english/our-quebec-communities/beaconsfield/overview.aspx"
        elif url =="https://www.sunriseseniorliving.com/communities/sunrise-of-dollard-des-ormeaux.aspx":
            url = "https://www.sunrisequebec.ca/english/our-quebec-communities/dollard-des-ormeaux/overview.aspx"
        elif url =="https://www.sunriseseniorliving.com/communities/sunrise-of-fontainebleau.aspx":
            url="https://www.sunrisequebec.ca/english/our-quebec-communities/fontainebleau/overview.aspx"
        res = session.get(url)
        print(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            jso = soup.find('script', {'type': 'application/ld+json'}).text
            jso = json.loads(jso)

            addr = jso["address"]
            city = addr["addressLocality"]
            state = addr["addressRegion"]
            zip = addr["postalCode"].strip()
            street = addr["streetAddress"]
            lat = jso["geo"]["latitude"]
            long = jso["geo"]["longitude"]
            loc = jso["name"]
            phone = jso['telephone']
            tim = jso['openingHoursSpecification']
            tim = tim['dayOfWeek'][0] + " - " + tim['dayOfWeek'][-1] + ": " + tim['opens'] + " - " + tim['closes']

        except:
            try:
                addr = soup.find('div', {'class': 'footer__content footer__content--address'}).text.strip().split(",")
                sz= addr[-1].strip().split(" ")
                del addr[-1]
                state = sz[0]
                del sz[0]
                zip=" ".join(sz)
                city = addr[-1]
                del addr[-1]
                street=" ".join(addr).strip()
                phone=soup.find('a', {'class': 'footer__content--phone'}).text.strip()
                tim="<MISSING>"
                coord=soup.find('a', {'id': 'footer_0_hypAddress'}).get('href')
                lat,long= re.findall(r'!3d(-?[\d\.]+)!4d(-?[\d\.]+)',coord)[0]
                loc=soup.find('title').text
            except:
                street=soup.find('span', {'itemprop': 'streetAddress'}).text.replace(",",'').strip()
                city=soup.find('span', {'itemprop': 'addressLocality'}).text.replace(",",'').strip()
                state=soup.find('span', {'itemprop': 'addressRegion'}).text.replace(",",'').strip()
                zip=soup.find('span', {'itemprop': 'postalCode'}).text.replace(",",'').strip()
                lat=soup.find('meta', {'itemprop': 'latitude'}).get('content')
                long=soup.find('meta', {'itemprop': 'longitude'}).get('content')
                phone=soup.find('span', {'itemprop': 'telephone'}).text.replace(",",'').strip()
                loc=soup.find('span', {'itemprop': 'name'}).text
                tim="<MISSING>"
        if len(phone) <5:
            phone=soup.find('div', {'class': 'inquiry-phone'}).find('strong').text

        print(tim)
        if len(zip)== 5:
            country="US"
        else:
            country="CA"
        all.append([
            "https://www.sunriseseniorliving.com",
            loc.strip(),
            street,
            city,
            state,
            zip,
            country,
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
