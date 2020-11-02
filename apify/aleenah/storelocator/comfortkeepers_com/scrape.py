import csv
from sgrequests import SgRequests
import us

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_state(state):
    url = "https://ckficms-api.herokuapp.com/api/offices?filter%5Binclude%5D%5B%5D=type&filter%5Binclude%5D%5B%5D=communities&filter%5Bwhere%5D%5Band%5D%5B0%5D%5Bst%5D=" + state + "&filter%5Bwhere%5D%5Band%5D%5B1%5D%5Bdisabled%5D=false&filter%5Border%5D=name%20ASC"
    return session.get(url).json()['data']

def fetch_data():
    data=[]
    states = us.states.STATES
    for state in states:
        stores = fetch_state(state.abbr)        
        for store in stores:
            location_type=store['type']
            meta = store['attributes']
            url="https://www.comfortkeepers.com/offices/" +  '-'.join([word for word in state.name.lower().split(' ')]) + '/' + meta['token']

            city = meta["city"]
            st = meta["st"]
            zip_code = meta["zip"]
            street = meta["street"]
            lat = meta["geo"]["lat"]
            lng = meta["geo"]["lng"]
            loc = meta['name']
            phone = meta['phone']
            if "MailDropOnly" in phone:
                phone="<MISSING>"
            hours = '<MISSING>'
            if 'hours' in meta and meta['hours']:
                raw = meta['hours']
                hours = ', '.join([day + ': ' + raw[day] for day in raw])
            store_number = store['id']
            data.append([
                "https://comfortkeepers.com/",
                loc,
                street,
                city,
                st,
                zip_code,
                "US",
                store_number,
                phone,
                location_type.strip(),
                lat,
                lng,
                hours,
                url])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

