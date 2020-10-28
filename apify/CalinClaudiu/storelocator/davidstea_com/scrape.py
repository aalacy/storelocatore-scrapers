import csv
from sgrequests import SgRequests


session = SgRequests()

url = "https://locations.davidstea.com/"

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

headers = {
    'Accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'connection': 'keep-alive',    
    'host': 'gannett-production.apigee.net',
    'if-none-match': 'W/"33e4d-iUv1vrDwV5hfR7msiVMpAASjfoc',
    'origin': 'https://locations.davidstea.com',
    'referer': 'https://locations.davidstea.com/',
    'sec-fetch-dest': '',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'x-api-key': 'iOr0sBW7MGBg8BDTPjmBOYdCthN3PdaJ',
}


api = "https://gannett-production.apigee.net/store-locator-next/59c135c35208bb9433f2a14c/locations-details?locale=en_US&ids=5964f48ab56cb43b122836e3%2C5964f48bb56cb43b122836e8%2C5964f48c556f1db66d5e4955%2C5964f48c556f1db66d5e4958%2C5964f48cbe238c222887c2fa%2C5964f48d556f1db66d5e495e%2C5964f48eaa6136e275e2bbc1%2C5964f48f7421c7d0380a5f35%2C5964f491b56cb43b122836f1%2C5964f498ddcee5847773ab40%2C5964f499be238c222887c31e%2C5964f49b556f1db66d5e497c%2C5964f49baa6136e275e2bbd9%2C5964f49d556f1db66d5e4988%2C5964f49ebe238c222887c339%2C5964f4a05601994a68057121%2C5964f4a17421c7d0380a5f5f%2C5964f4a4556f1db66d5e49a3%2C5d25039bb39a29ff0e582606&clientId=592ec5733a5792e54eba13e1&cname=locations.davidstea.com"

write = []

r1 = session.get(api, headers = headers).json()
for a in r1['features']: #type,features
    if a['properties']['isPermanentlyClosed'] is False:
        #print(a['properties']['hoursOfOperation'])
        lat = a['geometry']['coordinates'][0]
        lon = a['geometry']['coordinates'][1]
        #idk if this is correct
        name = a['properties']['name']
        addr = a['properties']['addressLine1']+" "+a['properties']['addressLine2']
        city = a['properties']['city']
        state = a['properties']['province']
        zipi = a['properties']['postalCode']
        country = a['properties']['country']
        phone = a['properties']['phoneNumber']
        storeid = a['properties']['branch']
        hours = a['properties']['hoursOfOperation']
        #i guess hours may have coming soon.
        #because of
        #"COMING_SOON":"{{ FEATURE.HOURS.COMING_SOON | i18n }}"}
        #but I have no clue where I can find it
        ltype = a['properties']['categories']
        pageur = url+a['properties']['slug']

        #["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
        #"store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        loc = []
        loc.append(url)
        loc.append(name)
        loc.append(addr)
        loc.append(city)
        loc.append(state)
        loc.append(zipi)
        loc.append(country)
        loc.append(storeid)
        loc.append(phone)
        loc.append(ltype)
        loc.append(lat)
        loc.append(lon)
        loc.append(hours)
        loc.append(pageur)
        loc = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in loc]
        write.append(loc)
        #print(loc)  
write_output(write)

