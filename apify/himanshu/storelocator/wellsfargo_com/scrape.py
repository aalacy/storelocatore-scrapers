import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    locator_domain= "https://www.wellsfargo.com/"

    addresses = []
    st_list = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH",'OK',"OR","PA","RI","SC","SD",'TN',"TX","UT","VT","VA","WA","WV","WI","WY"]

    for st in st_list:

        r = session.get("https://www.wellsfargo.com/locator/as/getCities/"+str(st.lower()))
        soup = BeautifulSoup(r.text, "lxml")
        if soup.find("p") == None:
            continue                               
        json_data = json.loads(soup.find("p").text.split("%")[1])

        for ct in json_data['allCities']:

            page_url = "https://www.wellsfargo.com/locator/search/?searchTxt="+str(ct.replace(" ","+"))+"%2C+"+str(st.lower())+"&mlflg=N&sgindex=99&chflg=Y&_bo=on&_wl=on&_os=on&_bdu=on&_adu=on&_ah=on&_sdb=on&_aa=on&_nt=on&_fe=on"        
            r = session.get(page_url)
            soup = BeautifulSoup(r.text, 'lxml')
                        
            for li in soup.find('div',{'id':'resultsSide'}).find_all('li',class_='aResult'):
                
                left_data = li.find('div',class_='vcard')
                adr = left_data.find('address',class_='adr')
                location_type = left_data.find('div',class_='fn heading').text.split('|')[0].strip().replace('+','and').strip()
                location_name = adr.find('div',{'itemprop':'addressLocality'}).text.strip().capitalize()
                street_address = adr.find('div',class_='street-address').text.strip().capitalize()
                city= adr.find('span',class_='locality').text.strip().capitalize()
                state = adr.find('abbr',class_='region').text.strip()
                zipp = adr.find('span',class_='postal-code').text.strip()
                #print(zipp)
                country_code = "US"
                phone_tag = left_data.find('div',class_='tel').text.replace('Phone:','').strip()
                phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                if phone_list != []:
                    phone = phone_list[0].strip()
                else:
                    phone="<MISSING>"
        
                list_hours= list(li.find('div',class_='rightSideData').stripped_strings)
                
                if "Outage Alert" in list_hours:
                    list_hours.remove('Outage Alert')
                if "Unavailable:" in list_hours :
                    list_hours.remove('Unavailable:')
                # if "ATMs" ==  list_hours[2] and len(list_hours) > 1:
                #     list_hours.remove('ATMs')
                    # print(list_hours)
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                if list_hours == []:
                    hours_of_operation = "<MISSING>"
                elif "Features" in list_hours[0]:
                    hours_of_operation = 'ATMs'+' '.join(list_hours).split('ATMs')[1].replace('&','and').strip()
                else:
                    hours_of_operation = " ".join(list_hours).strip().replace('&','and').strip()
                
                
                store = []
                store.append(locator_domain)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hours_of_operation)
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
    
                if store[2] + store[-5] in addresses:
                    continue
                addresses.append(store[2] + store[-5])

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                # return_main_object.append(store)
                yield store
            
        
                
       


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
