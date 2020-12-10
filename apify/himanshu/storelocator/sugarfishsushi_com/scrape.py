import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sugarfishsushi_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    address = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
    }
    r= session.get('https://sugarfishsushi.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    a= soup.find_all("div",{"class","text-box-inner none"})
    for i in a:
        d = (i.find_all("p"))
        for j in d:
            link = (j.find("a")['href'])
            # logger.info(link)
            r1 = session.get(link,headers = headers)
            soup1 = BeautifulSoup(r1.text,'lxml')
            a1 = soup1.find_all("h1",{"class","none entry-title section-title"})[1]
            location_name = ''
            for h in a1:
                location_name = (h)
            a2 = soup1.find("div",{"class","section-description none section-style-none"})
            zipp = (a2.text.split(" ")[-1].replace("\n",""))
            city = a2.text.split(",")[1].replace("\n","").replace("CA 91604",'Studio City').replace("#150","Los Angeles")
            state = a2.text.split(" ")[-2]
            street_address = a2.text.split(",")[0].replace(" Studio City",'').replace("600 W. 7th St","600 W. 7th St #150")
            hours_of_operation = ''
            if "CA" in state:
                hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[0].text.replace("\n","").replace("Los Angeles","").replace("Sat","Sat ").replace("SUNNoon"," SUN Noon"))
            else:
                hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[-1].text.replace("\n","").replace("New York","").replace("Thu","Thu ").replace("SUNNoon"," SUN Noon").replace("Fri"," Fri").replace("Sat","Sat "))
            phone = soup1.find("h3",{"class","photocard-subtitle none"}).text.replace("\n","").strip().lstrip().rstrip()
            # logger.info(phone)
            #  < class="photocard-subtitle none">
            store = []
            store.append("https://sugarfishsushi.com/")
            store.append(location_name.strip() if location_name else "<MISSING>")
            store.append(street_address.strip() if street_address else "<MISSING>")
            store.append(city.strip().strip() if city else "<MISSING>")
            store.append(state.strip() if state else "<MISSING>")
            store.append(zipp.strip() if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone.strip() if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
            store.append(link.strip() if link else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
    r1 = session.get('https://sugarfishsushi.com/pasadena/',headers = headers)
    soup1 = BeautifulSoup(r1.text,'lxml')
    a1 = soup1.find_all("h1",{"class","none entry-title section-title"})[1]
    location_name = ''
    for h in a1:
        location_name = (h)
    a2 = soup1.find("div",{"class","section-description none section-style-none"})
    zipp = (a2.text.split(" ")[-1].replace("\n",""))
    city = a2.text.split(",")[1].replace("\n","").replace("CA 91604",'Studio City').replace("#150","Los Angeles")
    state = a2.text.split(" ")[-2]
    street_address = a2.text.split(",")[0].replace(" Studio City",'').replace("600 W. 7th St","600 W. 7th St #150")
    hours_of_operation = ''
    if "CA" in state:
        hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[0].text.replace("\n","").replace("Los Angeles","").replace("Sat","Sat ").replace("SUNNoon"," SUN Noon"))
    else:
        hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[-1].text.replace("\n","").replace("New York","").replace("Thu","Thu ").replace("SUNNoon"," SUN Noon").replace("Fri"," Fri").replace("Sat","Sat "))
    phone = soup1.find("h3",{"class","photocard-subtitle none"}).text.replace("\n","").strip().lstrip().rstrip()
    store = []
    store.append("https://sugarfishsushi.com/")
    store.append(location_name.strip() if location_name else "<MISSING>")
    store.append(street_address.strip() if street_address else "<MISSING>")
    store.append(city.strip().strip() if city else "<MISSING>")
    store.append(state.strip() if state else "<MISSING>")
    store.append(zipp.strip() if zipp else "<MISSING>")
    store.append("US")
    store.append("<MISSING>") 
    store.append(phone.strip() if phone else "<MISSING>")
    store.append("SUGAR FISH")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append("https://sugarfishsushi.com/pasadena/")
    yield store 

    r1 = session.get('https://sugarfishsushi.com/locations/midtown-west/',headers = headers)
    soup1 = BeautifulSoup(r1.text,'lxml')
    a1 = soup1.find_all("h1",{"class","none entry-title section-title"})[1]
    location_name = ''
    for h in a1:
        location_name = (h)
    a2 = soup1.find_all("h5",{"class","entry-sub-title none section-sub-title"})[-1]
    zipp = (a2.text.split(" ")[-1].replace("\n",""))
    city = "NEW YORK"
    state = "NY"
    street_address = a2.text.split(",")[0].replace("1740 Broadway","1740 Broadway, #001")
    hours_of_operation = ''
    if "CA" in state:
        hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[0].text.replace("\n","").replace("Los Angeles","").replace("Sat","Sat ").replace("SUNNoon"," SUN Noon"))
    else:
        hours_of_operation = (soup1.find("div",{"class","opening-hours"}).find_all("div",{"class","opening-block"})[-1].text.replace("\n","").replace("New York","").replace("Thu","Thu ").replace("SUNNoon"," SUN Noon").replace("Fri"," Fri").replace("Sat","Sat "))
    phone = soup1.find("h3",{"class","photocard-subtitle none"}).text.replace("\n","").strip().lstrip().rstrip()
    store = []
    store.append("https://sugarfishsushi.com/")
    store.append(location_name.strip() if location_name else "<MISSING>")
    store.append(street_address.strip() if street_address else "<MISSING>")
    store.append(city.strip().strip() if city else "<MISSING>")
    store.append(state.strip() if state else "<MISSING>")
    store.append(zipp.strip() if zipp else "<MISSING>")
    store.append("US")
    store.append("<MISSING>") 
    store.append(phone.strip() if phone else "<MISSING>")
    store.append("SUGAR FISH")
    store.append("<MISSING>")
    store.append("<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append("https://sugarfishsushi.com/locations/midtown-west/")
    yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
