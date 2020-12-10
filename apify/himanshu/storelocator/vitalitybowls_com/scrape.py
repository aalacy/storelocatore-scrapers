import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('vitalitybowls_com')
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://vitalitybowls.com"
    r = session.get("https://vitalitybowls.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_links = []
    for states in soup.find_all("div",{"class":'et_pb_text_inner'}):
        for link in states.find_all("a"):
            loc_name = link.text
            if "Coming Soon" in loc_name:
                continue
            page_url = (link["href"])
            page_url = link["href"]
            if link["href"] in location_links:
                continue
            location_links.append(link["href"])
            location_request = session.get(link["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            name = location_soup.find("h2",{"class":"et_pb_slide_title"}).text
            address = list(location_soup.find("div",{"class":'et_pb_column et_pb_column_1_4 et_pb_column_inner et_pb_column_inner_0'}).find("div",{"class":"et_pb_text_inner"}).stripped_strings)
            adr = " ".join(address).replace("Newark CA 94560","Newark, CA 94560").split("\n")
            if "(Nyberg Rivers Shopping Center – Exit 289. NE Corner of Nyberg St. and Martinazzi Ave.)" in adr :
                del adr[-1]
            if len(adr)==3:
                city = adr[-1].split(",")[0]
                state = adr[-1].split(",")[1].split( )[0]
                zipp = adr[-1].split(",")[1].split( )[1]
                pars = adr[:-1]
                adr = map(lambda s: s.strip(), pars )
                new = map(lambda s: s.strip(), pars )
                newadd = map(lambda s: s.strip(), pars )
                nadr =  " ".join(adr)
                adrs =''
                for sep in  nadr:
                    if sep.isdigit() == True:
                        adrs = " ".join(new).split(sep)
                        break
                names = adrs[0]
                street_address = " ".join(newadd).replace(names,"")
            elif len(adr)==1:
                news = " ".join(adr).replace("STORE INFO ",'')
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(news))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(news))
                state_list = re.findall(r' ([A-Z]{2}) ', str(news))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                if state_list:
                    state = state_list[-1]
                city = link["href"].split("ns/")[-1].replace("/",'').replace("-",' ')
                street_address = news.replace(state,'').replace(zipp,'').lower().replace(" san jose,",'').replace("colorado  springs,  8092 1 phone: 719-639-7150",'').replace("orlando,",'').replace("ocoee,",'').replace(" peachtree city,",'').replace("omaha,",'').replace("las vegas,",'').replace("frisco,",'').replace("mckinney,",'').replace("irving,",'').replace("san marcos,",'').replace(",",'').replace(city,'').replace("colorado  springs  8092 1 phone: 719-639-7150",'')
                city = city.replace("san jose cherry ave",'san jose').replace("las vegas blue diamond",'las vegas').replace("san jose brokaw",'san jose').replace("san marcos acai bow",'san marcos')
            else:
                city = adr[-1].replace("Pleasant Hill CA 94523",'Pleasant Hill, CA 94523').split(",")[0]
                state = adr[-1].replace("Pleasant Hill CA 94523",'Pleasant Hill, CA 94523').split(",")[1].strip().split( )[0]
                zipp = adr[-1].replace("Pleasant Hill CA 94523",'Pleasant Hill, CA 94523').split(",")[1].strip().split( )[1]
                adr = list(map(lambda s: s.strip(), adr[:-1] ))
                street_address = " ".join(adr).replace("STORE INFO ",'').strip()
            try:
                hours = " ".join(list(location_soup.find("h2",text="HOURS").parent.stripped_strings)).replace("HOURS",'').strip()
            except:
                hours = " ".join(list(location_soup.find("h2",text="Hours").parent.stripped_strings)).replace("Hours",'').strip()
            phone_details = list(location_soup.find_all("div",{"class":'et_pb_text_inner'})[3].stripped_strings)
            geo_location = location_soup.find("iframe")["data-src"]
            if "coming soon" in " ".join(phone_details).lower():
                continue
            phone = ""
            phone_details = [x.lower() for x in phone_details]
            for k in range(len(phone_details)):
                if "tel:" in phone_details[k]:
                    phone = phone_details[k].split("tel:")[1].replace("email:","")
                    if phone == "":
                        phone = phone_details[k+1]
            if phone == "":
                for k in range(len(phone_details)):
                    if "phone:" in phone_details[k]:
                        if k == len(phone_details) - 1 or "email" in phone_details[k+1]:
                            phone = phone_details[k].split("phone:")[1].replace("\xa0"," ")
                        else:
                            phone = phone_details[k+1].replace("email:","")
                            if phone == "":
                                phone = phone_details[k].split("phone:")[1]
            if "phone" in street_address:
                street_address = "13492 Bass Pro Dr., Suite 120"
                zipp = "80921"
                phone = "719-639-7150"

            if "Trail" in street_address:
                street_address = "8226 Tamiami Trail"   
            if "3569 28th st.  the shops at centerpointe mall grand rapids michigan" in street_address:
                street_address = "3569 28th St. SE"
                zipp = "49512"
                state = "Michigan"
                city = "Grand Rapids"
            store=[]
            store.append("https://vitalitybowls.com")
            store.append(loc_name)
            store.append(street_address.replace("8226Tamiami Trail",'8226 Tamiami Trail').replace("westridge square shopping center ",'').replace("city creek center space #",'').replace("persimmon place ",'') if street_address else "<MISSING>")
            store.append(city.replace("frisco eldorado","frisco").replace("omaha legacy","omaha").replace("orlando ocoee","orlando").replace("orlando dr phillips","orlando") if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            if "!3d" in geo_location and "!2d" in geo_location:
                store.append(geo_location.split("!3d")[1].split("!")[0])
                store.append(geo_location.split("!2d")[1].split("!")[0])
            else:
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
            store.append(hours.replace("Re-opening April 28th!",'').replace("\n","").replace("\r","").replace("\t","") if hours.strip() else "<MISSING>")
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            # if str(store[2]+store[-1]) in addressess:
            #     continue
            # addressess.append(str(store[2]+store[-1]))
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
