import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import csv
import re
import json
import unicodedata
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    address = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Content-Type': 'application/json',
        'Referer': 'https://www.bmwusa.com/?bmw=grp:BMWcom:header:nsc-flyout'
    }
    while zip_code:
        result_coords =[]
        
        addressess = []
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        base_url = "https://www.careeronestop.org/"
        location_url = "https://www.careeronestop.org/Localhelp/AmericanJobCenters/find-american-job-centers.aspx?&location="+str(zip_code)+"&radius=100&pagesize=500"
        r = session.get(location_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        table = soup.find("table",{"class":"cos-table cos-table-mobile"}).find("tbody").find_all("tr")
        for tr in table:
            location_name = tr.find("a",{"class":"notranslate"}).text
            page_url = tr.find("a",{"class":"notranslate"})['href']
            data_link = ("https://www.careeronestop.org/"+page_url)
            r1 = session.get(data_link,headers=headers)
            soup = BeautifulSoup(r1.text,"lxml")
            addr = (soup.find_all("script",{"type":"text/javascript"})[11])
            data_main = (str(addr).split("locinfo = ")[1].split("var mapapi =")[0].replace(";",""))
            json_data = json.loads(data_main)
            street_address1 = json_data['ADDRESS1']
            city = json_data['CITY']
            state = json_data['STATE']
            zipp = json_data['ZIP']
            latitude = json_data['LAT']
            longitude = json_data['LON']
            location_name = soup.find("div",{"id":"detailsheading"}).text
            try:
                phone = soup.find("a",{"class":"notranslate"}).text
            except:
                phone = "mp"
            st_data = soup.find_all("span",{"class":"notranslate"})[2].text.split(",")[0].replace(city,"").replace(street_address1,"")
            street_address = street_address1 +" "+ st_data
            try:
                hs = soup.find("tbody",{"id":"ctl22_tbAJCDetail"}).find_all("tr")[3].text
                if "Hours" in hs: 
                    data_hs = (hs)
                else:
                    hs = soup.find("tbody",{"id":"ctl22_tbAJCDetail"}).find_all("tr")[4].text
                    if "Hours" in hs: 
                        data_hs = hs
                    else:
                        hs = soup.find("tbody",{"id":"ctl22_tbAJCDetail"}).find_all("tr")[2].text
                        if "Hours" in hs: 
                            data_hs = hs
            except:
                data_hs = "mp"   
            store = []
            store.append("https://www.careeronestop.org/")
            store.append(location_name)
            store.append(street_address.replace("      "," ").replace("7161  Gateway Drive","").strip())
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(data_hs.replace("Hours","").replace("     "," ") if data_hs else "<MISSING>" )
            store.append(data_link)
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
        if len(json_data) < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
