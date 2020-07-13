import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import requests



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess=[]
    return_main_object = []
    base_url = "https://www.booking.com/city.html?label=gen173nr-1FCAEoggI46AdIM1gEaKQCiAEBmAExuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKD2ez3BcACAdICJDE1OGMwODM2LWRmMjgtNDdjYS1hNTZhLWQ2ZGU3OGRkZWEzOdgCBeACAQ;sid=987a93e4bbb5e033adbcca4ed721e65f"
    list1=[]
    dummy =[]
    soup1 = bs(requests.get(base_url).text,'lxml')
    for i in soup1.find_all("div",{"class":"block_third"}):
        for q in i.find_all("li"):
            main_url="https://www.booking.com"+q.find('a')['href']
            try:
                city_id = bs(requests.get(main_url).text,'lxml').text.split("b_dest_id")[1].split("ip_country:")[0].split("'")[1]
            except:
                continue
            pages="https://www.booking.com/searchresults.html?tmpl=searchresults&city="+str(city_id)+"&class_interval=1&dest_id="+str(city_id)+"&dest_type=city&offset="+str(0)
            soup3 = bs(requests.get(pages).text,'lxml')
            total_page = (soup3.find_all("li",{"class":"bui-pagination__item sr_pagination_item"})[-1].find("div",{"class":"bui-u-inline"}).text.strip())
            for i in range(0,int(total_page)):
                sub_url="https://www.booking.com/searchresults.html?tmpl=searchresults&city="+str(city_id)+"&dest_id="+str(city_id)+"&dest_type=city&offset="+str(i*25)
                soup4 = bs(requests.get(sub_url).text,'lxml')
                # print(sub_url)
                for tag in soup4.find("div",{"class":"hotellist"}).find_all("div",{'class':"sr-hotel__title-wrap"}):
                    if tag.find("a")['href'] in dummy:
                        continue
                    dummy.append(tag.find("a")['href'])
                    soup5 = bs(requests.get("https://www.booking.com"+tag.find("a")['href'].strip()).text,'lxml')
                    page_url = "https://www.booking.com"+tag.find("a")['href'].strip()
                    #print(page_url)
                    zipps=''
                    street_address=''
                    states=''
                    location_type=''
                    try:
                        json_data = json.loads(soup5.find("script",{"type":"application/ld+json"}).text)
                        name=json_data['name']
                        city = str(soup5).split("city_name:")[1].split("',")[0].replace("'",'').strip()
                        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str( json_data['address']['streetAddress']))
                        zipp=''
                        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(json_data['address']['postalCode']))
                        if ca_zip_list:
                            zipp = ca_zip_list[-1]
                        us_zip_list1 = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(json_data['address']['postalCode']))
                        if us_zip_list1:
                            zipp = us_zip_list1[-1]
                        state_list = re.findall(r' ([A-Z]{2})', str(json_data['address']['streetAddress']))
                        if us_zip_list:
                            zipps = us_zip_list[-1]
                        if state_list:
                            states = state_list[-1]
                        street_address = json_data['address']['addressLocality'].replace("United States of America","").replace("US","").replace("USA","").replace(zipps,'').replace(city,'').replace(states,'').replace(","," ")
                        state = json_data['address']['addressRegion']
                        # zipp = " ".join(json_data['address']['postalCode'].split()[1:])
                        location_type = json_data['@type']
                        city = str(soup5).split("city_name:")[1].split("',")[0].replace("'",'').strip()
                        lat = json_data['hasMap'].split("center")[1].split(",")[0].replace("=",'')
                        lng = json_data['hasMap'].split("center")[1].split(",")[1].split("&")[0].replace("=",'')
                        phone="<MISSING>"
                        store = []
                        store.append("https://www.booking.com/")
                        store.append(name.encode('ascii', 'ignore').decode('ascii').strip())
                        store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip() if street_address else "<MISSING>")
                        store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
                        store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
                        store.append(zipp if zipp else "<MISSING>")
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone if phone else "<MISSING>")
                        store.append(location_type if location_type else "<MISSING>")
                        store.append(lat.strip() if lat.strip() else "<MISSING>" )
                        store.append(lng.strip() if lng.strip() else "<MISSING>")
                        store.append( "<MISSING>")
                        store.append(page_url)
                        if str(store[1]+store[2]+store[4]) in addressess:
                            continue
                        addressess.append(str(store[1]+store[2]+store[4]))
                        # store = [x.replace("–", "-") if type(x) ==
                        #          str else x for x in store]
                        store = [x.encode('ascii', 'ignore').decode(
                            'ascii').strip() if type(x) == str else x for x in store]
                        # print("data ===" + str(store))
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        yield store
                    except:
                        pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


