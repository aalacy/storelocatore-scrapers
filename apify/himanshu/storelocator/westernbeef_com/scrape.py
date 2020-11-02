import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('westernbeef_com')



session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "http://westernbeef.com/"
    r = session.get("http://westernbeef.com/western-beef---locations.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a", {"class":"nonblock nontext Button rounded-corners transition clearfix grpelem"})
    url = []
    for link in links:
        if base_url+link['href'] in url:
            continue
        url.append(base_url+link['href'])
        page_url = base_url+link['href']
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Address:" in soup1.find_all("div",{"data-muse-type":"txt_frame"})[-1].text:
            data = list(soup1.find_all("div",{"data-muse-type":"txt_frame"})[-1].stripped_strings)
            street_address = data[1]
            city = data[2].split(",")[0]
            state = data[2].split(",")[1].split(" ")[1]
            zipp = data[2].split(",")[1].split(" ")[2]
            phone = data[-1].split(":")[-1].strip()
            hours_of_operation = " ".join(data[3:-2])
        
        elif "Address:" in soup1.find_all("div",{"data-muse-type":"txt_frame"})[0].text:
            data = list(soup1.find_all("div",{"data-muse-type":"txt_frame"})[0].stripped_strings)
            street_address = data[1]
            city = data[2].split(",")[0]
            state = data[2].split(",")[1].split(" ")[1]
            zipp = data[2].split(",")[1].split(" ")[2]
            phone = data[-1].split(":")[-1].strip()
            hours_of_operation = " ".join(data[3:-2])
        else:
            try:
                
                data = soup1.find_all("img",{"class":"grpelem"})[1]['alt']
            except:
                data = soup1.find("img",{"class":"colelem"})['alt']
            if "Telephone" in data:
                phone = data.split("Telephone :")[1].strip()
                hours_of_operation = "Hours:"+" "+data.split("Hours:")[1].split("Contact")[0].strip()
                street_address = " ".join(data.split("Hours:")[0].split(",")[0].split("Address:")[1].split(" ")[:-1]).replace("W.","").replace("Staten","").strip()
                city = data.split("Hours:")[0].split(",")[0].split("Address:")[1].split(" ")[-1].replace("Hempstead","W. Hempstead").replace("Island","Staten Island").strip()
                if len(data.split("Hours:")[0].split(",")[1].split(" ")) ==4:
                    state = data.split("Hours:")[0].split(",")[1].split(" ")[1]
                    zipp = data.split("Hours:")[0].split(",")[1].split(" ")[2]
                else:
                    state = data.split("Hours:")[0].split(",")[1].split(" ")[0]
                    zipp = data.split("Hours:")[0].split(",")[1].split(" ")[1]
            else:
                phone = "<MISSING>"
                hours_of_operation = "Hours:"+" "+data.split("Hours:")[1]
                street_address = " ".join(data.split("Hours:")[0].split(",")[0].split("Address:")[1].split(" ")[:-1])
                city = data.split("Hours:")[0].split(",")[0].split("Address:")[1].split(" ")[-1]
                state = data.split("Hours:")[0].split(",")[1].split(" ")[1]
                zipp = data.split("Hours:")[0].split(",")[1].split(" ")[2]

        store =[]
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        store.append(page_url)
        # logger.info("data====="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


