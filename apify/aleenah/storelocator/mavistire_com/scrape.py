import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
all=[]
def fetch_data():
    # Your scraper here
    page_url=[]
    res=session.get("https://www.mavistire.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find_all('tr', {'style': 'background-color: #f3f3f3'})
    print(len(urls))
    unique=set([])
    for url in urls:
        ua=url.find('a').get('href')

        url="https://www.mavistire.com/locations/"+ua
        print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            data = soup.find('table').find_all('script')[2].text
        except:
            try:
                data = soup.find('table').find('script', {'language': 'javascript'}).text
            except:
                continue #closed
        jsonValue = '{%s}' % (data.partition('{')[2].rpartition('}')[0],)
        #print("["+jsonValue.replace("\'", "\"").replace(':"','":"').replace('",','","').replace('{','{"').replace(',"{',',{').replace(',Lng:','","Lng":"').replace('"Lat:','"Lat":"').replace(',fillcolor','","fillcolor')+"]")


        js_list = json.loads("["+jsonValue.replace("\'", "\"").replace(':"','":"').replace('",','","').replace('{','{"').replace(',"{',',{').replace(',Lng:','","Lng":"').replace('"Lat:','"Lat":"').replace(',fillcolor','","fillcolor')+"]")
        for js in js_list:
            loc=js["Store_Name"]
            id=js["Store"]
            tim=js["Store_Hours"].replace("<br>"," ")
            street=js["Addr"]
            state=js["State"]
            city=js["City_State"].replace(state,"").strip()
            zip=js["Zip"]
            phone=js["Callcenter_Phone"]
            lat=js["Lat"]
            long=js["Lng"]
            if loc+street+id+state+city not in unique:
                unique.add(loc+street+id+state+city)
            else:
                continue
            all.append([
                "https://www.mavistire.com/",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                id,  # store #
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
