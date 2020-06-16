import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    base_url = "https://www.mbusa.com"

    
    
    json_data = session.get("https://nafta-service.mbusa.com/api/dlrsrv/v1/us/search?lat=30.677791&lng=-99.576815&start=0&count=1000&filter=mbdealer").json()['results']
    # loc_type = {"mbdealer":"Dealership","all":"All Locations","amg":"AMG Performance Center","amgelite":"AMG Performance Center Elite","collisioncenter":"Collision Center + Drop-off Locations","elitecollisioncenter":"Elite Collision Center (Aluminum Welding)","prmrexp":"Express Service by MB","service":"Service and Parts","maybach":"Maybach Dealership","zevst":"Zero Emission Vehicle State","sales":"Sales"}
    for data in json_data:
        location_name = data['name']
        street_address = (data['address'][0]['line1']+ str(data['address'][0]['line2'])).strip()
        city = data['address'][0]['city']
        state = data['address'][0]['state']
        zipp = data['address'][0]['zip']
        country_code = data['address'][0]['country']
        store_number = data['id']
        phone = "<INACCESSIBLE>"
        lat = data['address'][0]['location']['lat']
        lng = data['address'][0]['location']['lng']
        location_type = data['type']
        if data['url']:
            page_url = data['url']
        else:
            page_url = "http://www.mbofcovington.com/"
        
        if page_url == "http://www.southorlando.mercedesdealer.com":
            hours = " ".join(list(bs(session.get("https://www.mercedesbenzsouthorlando.com/contact.htm").text,"lxml").find("div",{"class":"hours-default ddc-content ddc-box-1"}).stripped_strings))
        else:
            soup = bs(session.get(page_url).text, "lxml")
            if soup.find("table",{"id":re.compile("_Sales")}):
            
                hours = " ".join(list(soup.find("table",{"id":re.compile("_Sales")}).find("tbody").stripped_strings))
            elif soup.find("div",{"class":re.compile("module-container js-module mod-department-hours mod-department-hours-theme2 mod-department-hours-theme2")}):
            
                if soup.find("div",{"class":re.compile("module-container js-module mod-department-hours mod-department-hours-theme2 mod-department-hours-theme2")}).find("a",{"class":"js-popover"}):
                
                    hr = soup.find("div",{"class":re.compile("module-container js-module mod-department-hours mod-department-hours-theme2 mod-department-hours-theme2")}).find("a",{"class":"js-popover"})['data-content']
                    hours = " ".join(list(bs(hr, "lxml").find("table").stripped_strings))
                elif soup.find("a",{"class":"header-contact__link header-contact__hours-link header-contact__hours-link_showed js-popover js-hours"}):
                    hours = " ".join(list(bs(soup.find("a",{"class":"header-contact__link header-contact__hours-link header-contact__hours-link_showed js-popover js-hours"})['data-content'], "lxml").find("table").find("tbody").stripped_strings))
                else:
                    hours = "<MISSING>"
            elif soup.find("li",{"class":"footer-address blue-color"}):
                
                soup = bs(session.get(soup.find("li",{"class":"footer-address blue-color"}).find("a")['href']).text, "lxml")

                if soup.find("div",{"class":"hours-box"}):
                    
                    hours = " ".join(list(soup.find("div",{"class":"hours-box"}).stripped_strings))
                elif soup.find("dl",{"class":"hours-box"}):
                    
                    hours = " ".join(list(soup.find("dl",{"class":"hours-box"}).stripped_strings))
                else:
                    
                    hours = "<MISSING>"


            else:
                soup = bs(session.get(page_url.replace(".com/",".com")+"/contact-us/").text, "lxml")

                if soup.find("span",{"class":"hours-sales"}):
                    hours = " ".join(list(soup.find("span",{"class":"hours-sales"}).stripped_strings))
                elif soup.find("div",{"class":"page-hours sales-hours"}):
                    hours = " ".join(list(soup.find_all("div",{"class":"page-hours sales-hours"})[-1].stripped_strings))
                else:
                    if session.get(session.get(page_url).url+"navigation-fragments/dealership-info.htm?referrer=%2F").status_code == 200:
                        soup = bs(session.get(session.get(page_url).url+"navigation-fragments/dealership-info.htm?referrer=%2F").text,"lxml")
                        try:
                            hours = " ".join(list(soup.find("ul",{"class":"ddc-list-1 dictionary-list ddc-hours ddc-list-items list-unstyled"}).stripped_strings))
                        except:
                            hours = " ".join(list(soup.find("ul",{"class":"ddc-list-1 dictionary-list ddc-hours consolidated ddc-list-items list-unstyled"}).stripped_strings))
                    else:
                        hours = "<MISSING>"
        
    
    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address.replace('None',''))
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print(store)
        yield store
       
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
