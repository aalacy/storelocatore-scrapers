import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

sta = {
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}
states_lp = sta.keys()
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "https://sbarro.com"
    for st in states_lp:
        # print(st)
        location_url = "https://sbarro.com/locations/?user_search=" + str(st)
        r = session.get(location_url)
        soup = BeautifulSoup(r.text, "lxml")
        links = soup.find_all("h2",{"class":"location-name"})
        for index,link in enumerate(links):
            coords = soup.find_all("section",{"class":"locations-result"})
            latitude = []
            longitude = []
            for coord in coords:
                latitude.append(coord['data-latitude'])
                longitude.append(coord['data-longitude'])
            page_url = base_url+link.find("a")['href']
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            try:

                try:
                    location_name = soup1.find("h1",{"class":"location-name"}).text.strip()
                except:
                    location_name = soup1.find("h2",{"class":"location-name"}).text.strip()
            except:
                continue
                
            
            # print(location_name)
            street_address = " ".join(soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[:-2]).strip()
            city = soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[-2].strip().capitalize()
            temp_state_zip = soup1.find("p",{"class":"location-address"}).text.replace(",,",',').split(",")[-1].strip().split(" ")
            # print(temp_state_zip)
            if len(temp_state_zip) == 2:
                state = temp_state_zip[0]
                zipp = temp_state_zip[1]
            elif len(temp_state_zip) == 3:
                state = temp_state_zip[0]
                zipp = temp_state_zip[2]
            else:
                state = temp_state_zip[0]
                zipp = "<MISSING>"
            try:
                phone = soup1.find("div",{"class":"location-phone location-cta"}).find("span",{"class":"btn-label"}).text.strip()
            except:
                phone = "<MISSING>"
            try:
                hours_of_operation = " ".join(list(soup1.find("div",{"class":"location-hours"}).stripped_strings))
            except:
                hours_of_operation = "<MISSING>"

            country_code = "US"
            location_type = "Restaurant"
            if latitude[index] =="0" and longitude[index] == "0":
                latitude[index] = "<MISSING>"
                longitude[index] = "<MISSING>"

            if state == st:

                store = []
                store.append(base_url)
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>") 
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude[index])
                store.append(longitude[index])
                store.append(hours_of_operation.replace("Hours of Operation","") if hours_of_operation.replace("Hours of Operation","") else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                        continue
                addresses.append(store[2])
                yield store
                
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
