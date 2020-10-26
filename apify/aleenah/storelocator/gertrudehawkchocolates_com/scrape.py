import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
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

    res=session.get("https://gertrudehawkchocolates.com/find_a_store")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores=re.findall(r'"items":(.*}])',str(soup))[0].split('{"id"')
    print(len(stores))
    del stores[0]

    for store in stores:
        id,loc,country,city,zip,street,lat,long =re.findall(':"(.*)","name":"(.*)","country":"(.*)","city":"(.*)","zip":"(.*)","address":"(.*)","status":".*","lat":"(.*)","lng":"(.*)","photo"',store)[0]
        state=re.findall(r'State: (.*) <br>',store)[0]
        phone=re.findall(r'"phone":"(.*)","email',store)[0].split(' ')[0]
        #print(phone)
        timi=re.findall(r'"schedule_string":"(.*)","rating"',store)[0].replace('\\','')
        if len(zip)==4:
            zip="0"+zip

        timi=json.loads(timi)
        tim=""
        for day in timi:
            tim += day.upper()+": "+timi[day]['from']['hours']+":"+timi[day]['from']['minutes']+" - "+timi[day]['to']['hours']+":"+timi[day]['to']['minutes']+" "
        all.append([
            "https://gertrudehawkchocolates.com",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            id,  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            "https://gertrudehawkchocolates.com/find_a_store"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()