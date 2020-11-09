import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://tsk.com/locations/"
    return_main_object = []
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,'html5lib')
    main = soup.find_all('script')[15].text.split("var locations = ")[1].split("for (var i=0; i < locations.length; i++)")[0].replace('twitter.com\/TSMMAFeaster"}]];','twitter.com\/TSMMAFeaster"}]]')
    list_1 = []
    data_json = json.loads(main)
    for i in data_json:
        for j in i:
            list_1.append(j)
    try:
        i = 4
        while True:
            # r = session.get("https://tsk.com/locations/"+list_1[i]['url'],headers=headers)
            # soup = BeautifulSoup(r.text, "html5lib")
            # data = soup.find("div",{"class":"qigLe4VzIR2OBRVx0QbLM dS6uS5vUPuwi9woFSKW5A _1gETrmJP4-nKwWKbJliZCW _1TdCsy72ploof1Rx0WfhEv foajPYZEN0yB_-OGHR4Ol merce-column"}).text
            # print(data)
            store=[]
            store.append("https://tsk.com/")
            store.append(list_1[i]['name'] if list_1[i]['name'] else "<MISSING>")
            store.append(list_1[i]['street'] if list_1[i]['street'] else "<MISSING>")
            store.append(list_1[i]['city'] if list_1[i]['city'] else "<MISSING>")
            store.append(list_1[i]['state'] if list_1[i]['state'] else "<MISSING>")
            store.append(list_1[i]['zip5'] if list_1[i]['zip5'] else "<MISSING>")
            store.append("US")
            store.append(list_1[i]['crmSchoolId'])
            store.append(list_1[i]['phone'] if list_1[i]['phone'] else "<MISSING>")
            store.append("tsk")
            store.append(list_1[i]['lat'] if list_1[i]['lat'] else "<MISSING>")
            store.append(list_1[i]['lon'] if list_1[i]['lon'] else "<MISSING>")
            store.append("<INACCESSIBLE>")
            # inaccessible
            store.append("https://tsk.com/locations"+list_1[i]['url'])
            yield store
            i = i + 5
    except:
        pass
def scrape():
    data = fetch_data()
    write_output(data)
scrape()