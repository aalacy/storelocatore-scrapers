import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "http://whywaitintheer.com/"     
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("ul",{"id":"nav"}).find_all("li")[1].find("ul").find_all("a"):
        state_link = link['href']
        state_r = session.get(state_link)
        state_soup = BeautifulSoup(state_r.text, "lxml")
        for url in state_soup.find_all("a",{"class":"class_blue"}):
            page_url = url['href']
            # print(page_url)
            location_r = session.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")
            location_name = location_soup.find("div",{"id":"subpagecontent"}).find("h1").text
            # http://www.whywaitintheer.com/walkinmedicalcenter.php
          
            state = link.text.replace("Maryland","MD").replace("Delaware","DE")
            try:
                # print(location_soup.find("option")['value'])
                addr = location_soup.find("option")['value'].split(",")
                if (len(addr)) == 2:
                    street_address = addr[0]
                    info = re.sub(r'\s+'," ",addr[-1].replace(state,"").strip())
                    if len(info.split(" ")) == 2:
                        city = info.split(" ")[0]
                        zipp = info.split(" ")[1]
                    else:
                        city = "<MISSING>"
                        zipp = info.strip()
                    
                elif len(addr) == 3:
                    
                    street_address = addr[0]
                    city = addr[1].replace("Delaware","").strip()
                    zipp = addr[-1].replace(state,"").strip()
                else:
                    street_address = " ".join(addr[0].split(" ")[:-1]).replace(state,"").strip()
                    zipp = addr[0].split(" ")[-1]
                if "Forest Hill" in street_address:
                    city = " ".join(addr[0].split()[-2:])
                    street_address = " ".join(addr[0].split()[:-2])
                
            except:
                continue
            # print("final---",street_address)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            # print(page_url)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            contact = list(location_soup.find("div",{"id":"directions"}).stripped_strings)
            if "var end" in contact[0]:
                del contact[0]
            if "Phone and Hours" in contact[0]:
                del contact[0]
            phone = contact[0].replace("Phone:","").strip()
            del contact[0]
            if "Patient Care Service Center" in contact[0]:
                del contact[0]
            if "Fax:" in contact[0]:
                del contact[0]
            if "Billing:" in contact[0]:
                del contact[0]
            if "Reserve" in contact[2]:
                del contact[2:]
            if "Reserve" in contact[1]:
                del contact[1:]
            hours_of_operation = " ".join(contact).replace("7 days a week Reserve your Time Next Available Walk-in is at: Reserve my spot","").replace("Hours:","").strip()
    
            store = []
            if location_name.strip().encode('ascii', 'ignore').decode('ascii').strip():
                location_name = location_name.strip().encode('ascii', 'ignore').decode('ascii').strip()
            else:
                location_name = "<MISSING>"
            

            
            store.append(base_url)
            store.append(location_name)
            store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(zipp if zipp else "<MISSING>")   
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("Express Care")
            store.append("<MISSING>" )
            store.append("<MISSING>" )
            store.append(hours_of_operation.strip())
            store.append(page_url)
            # print("data==="+str(store[-2]))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

            yield store
        

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
