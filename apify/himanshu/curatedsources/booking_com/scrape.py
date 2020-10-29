import csv
from bs4 import BeautifulSoup as bs
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('booking_com')


session = SgRequests()


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
    ca_address = []
    base_url = "https://www.booking.com"

    soup = bs(session.get("https://www.booking.com/country.html").content, "lxml")

    for Accommodation in soup.find("a",text=re.compile("Canada")).parent.parent.parent.find_all("a"):
        try:
            if Accommodation['href'].count("/") == 2:
                continue
            
            # logger.info(":::::::::::::::::::::",Accommodation.text,":::::::::::::::::::::")
            accmd_soup = bs(session.get(base_url + Accommodation['href']).content, "lxml")

            for region_link in accmd_soup.find("h2",text=re.compile("Top Regions in Canada")).parent.findNext("div").find_all("a"):
                # logger.info(re.sub(r'\s+'," ",region_link.text))
                region_soup = bs(session.get(base_url + region_link['href']).content, "lxml")
                
                region_id = region_soup.find("a",{"title":re.compile("All ")})['href'].split("region=")[1].split(";")[0]
                
                offset = 0
                while True:

                    off_url = "https://www.booking.com/searchresults.html?aid=304142&tmpl=searchresults&class_interval=1&dest_id="+str(region_id)+"&dest_type=region&group_adults=2&group_children=0&label_click=undef&nflt=sth%3D74%3B&no_rooms=1&raw_dest_type=region&region="+str(region_id)+"&room1=A%2CA&sb_price_type=total&shw_aparth=1&slp_r_match=0&srpvid=419b265e8f2801c9&ssb=empty&top_ufis=1&rows=25&offset="+str(offset)

                    off_soup = bs(session.get(off_url).content, "lxml")   

                    if off_soup.find("a",{"class":"hotel_name_link url"}) == None or offset == 1025:
                        break
                    
                    for url in off_soup.find_all("a",{"class":"hotel_name_link url"}):
                        
                        if "/us/" in url['href']:
                            continue
                        
                        page_url = base_url + url['href'].strip()
                        soup = bs(session.get(page_url).text,'lxml')
                        data = json.loads(str(soup.find("script",{"type":"application/ld+json"})).split(">")[1].split("<")[0])
                       
                        location_name = data['name']

                        try:
                            street_address = data['address']['addressLocality']
                        except:
                            street_address = "<MISSING>"
                        try:
                            state = data['address']['addressRegion']
                        except:
                            state = "<MISSING>"
                        try:
                            zipp = data['address']['postalCode']
                        except:
                            zipp = "<MISSING>"
                        city = str(soup).split("city_name:")[1].split("',")[0].replace("'",'').strip()
                        try:
                            location_type = data['@type']
                        except:
                            location_type = "<MISSING>"
                        try:
                            lat = data['hasMap'].split("center")[1].split(",")[0].replace("=",'')
                            lng = data['hasMap'].split("center")[1].split(",")[1].split("&")[0].replace("=",'')
                        except:
                            lat = "<MISSING>"
                            lng = "<MISSING>"

                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append(state)
                        store.append(zipp)
                        store.append("CA")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append(location_type)
                        store.append(lat)
                        store.append(lng)
                        store.append("<MISSING>")
                        store.append(page_url)
                        if store[2] in ca_address:
                            continue
                        ca_address.append(store[2])
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        
                        yield store
                        
                    offset += 25
           
        except Exception as e:
            # logger.info(e)
            continue   
    
    addressess=[]
    return_main_object = []
    base_url = "https://www.booking.com/city.html?label=gen173nr-1FCAEoggI46AdIM1gEaKQCiAEBmAExuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKD2ez3BcACAdICJDE1OGMwODM2LWRmMjgtNDdjYS1hNTZhLWQ2ZGU3OGRkZWEzOdgCBeACAQ;sid=987a93e4bbb5e033adbcca4ed721e65f"
    list1=[]
    dummy =[]
    soup1 = bs(session.get(base_url).text,'lxml')
    for i in soup1.find_all("div",{"class":"block_third"}):
        for q in i.find_all("li"):
            main_url="https://www.booking.com"+q.find('a')['href']
            try:
                city_id = bs(session.get(main_url).text,'lxml').text.split("b_dest_id")[1].split("ip_country:")[0].split("'")[1]
            except:
                continue
            pages="https://www.booking.com/searchresults.html?tmpl=searchresults&city="+str(city_id)+"&class_interval=1&dest_id="+str(city_id)+"&dest_type=city&offset="+str(0)
            soup3 = bs(session.get(pages).text,'lxml')
            total_page = (soup3.find_all("li",{"class":"bui-pagination__item sr_pagination_item"})[-1].find("div",{"class":"bui-u-inline"}).text.strip())
            for i in range(0,int(total_page)):
                sub_url="https://www.booking.com/searchresults.html?tmpl=searchresults&city="+str(city_id)+"&dest_id="+str(city_id)+"&dest_type=city&offset="+str(i*25)
                soup4 = bs(session.get(sub_url).text,'lxml')
                # logger.info(sub_url)
                for tag in soup4.find("div",{"class":"hotellist"}).find_all("div",{'class':"sr-hotel__title-wrap"}):
                    if tag.find("a")['href'] in dummy:
                        continue
                    dummy.append(tag.find("a")['href'])
                    soup5 = bs(session.get("https://www.booking.com"+tag.find("a")['href'].strip()).text,'lxml')
                    page_url = "https://www.booking.com"+tag.find("a")['href'].strip()
                    # logger.info(page_url)
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
                        # logger.info("data ===" + str(store))
                        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        yield store
                    except:
                        pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


