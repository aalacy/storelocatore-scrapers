import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import datetime
from datetime import datetime
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
    
      
    list_of_urls=[]
    base_url = "https://www.spar.co.uk"
 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    result_coords = []
    r = session.get("https://www.spar.co.uk/sitemap-page",headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for inex,link in enumerate(soup.find_all("a")):
        if "/store-locator/" in link['href']:
            page_url = base_url + link['href']
            # list_of_urls.append(page_url)
            r1= session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            # print("---",len(list_of_urls))
            # data1 = _send_multiple_rq(list_of_urls)
            # for index,q in enumerate(data1):
            # print("----------------qqqqqq",q)
            
            full = list(soup1.find("div",{"class":"store-details__contact"}).stripped_strings)
            if soup1.find("span",{"class":"page__notice-title"}):
                continue
            for index,w in enumerate(full):
                if  "Phone" in w:
                    full= full[index+2:]

            for index,w in enumerate(full):
                if  "Contact us" in w:
                    del full[index]
                    # full= full[index]
                    
            full1 = [re.sub(r"\s+", " ",x).replace('\n', '').replace("\r",'').replace('\t','').strip().lstrip().rstrip() for x in full]
            stopwords=','
            new_words = [word for word in full1 if word not in stopwords]
            stopwords='Address'
            full2 = [word for word in new_words if word not in stopwords]
            city="<MISSING>"
            state = "<MISSNG>"
            try:
                city = addr['address']['addressLocality']
            except:
                city = "<MISSINIG>"
            try:
                state = addr['address']['addressRegion']
            except:
                state = "<MISSNG>"
            if len(full2)==4:
                state = full2[-2]
                city = full2[-2]

                # print(page_url)
                street_address = " ".join(full2[:-2])
                # print(street_address)
                # print("--------------------44444 ",full2)
            elif len(full2)==5:
                # 
                city=full2[-3]
                state=full2[-2]
                street_address = " ".join(full2[:-3])
                # print("--------------------555555 ",full2)
            elif len(full2)==3:
                street_address  = " ".join(full2[:-2])
                city = full2[-2]
                # print(page_url)
                city_state=full2[-2].split(",")
                if len(city_state)==0:
                    city = city_state[0]
                elif len(city_state)==4:
                    city = city_state[2]
                    state = city_state[3]
                else:
                    city = " ".join(city_state).strip()

                # print(full2[-2].split(","))
                # print("--------------------333333333333 ",full2)


            addr = json.loads(soup1.find(lambda tag : (tag.name == "script") and "latitude" in tag.text).text)
            location_name = addr['name']
            street_address = street_address.replace(location_name,'')
            # try:
            #     street_address = addr['address']['streetAddress']
            # except:
            #     street_address = "<MISSING>"
            
            
            try:
                zipp = addr['address']['postalCode']
            except:
                zipp = "<MISSING>"
            try:
                phone = addr['telephone']
            except:
                phone = "<MISSING>"
            location_type = addr['@type']
            time = " ".join(list(soup1.find("table",{"class":"table"}).find("tbody").stripped_strings))
            if "24h" in time:
                hours = time
            elif "CLOSED" in time:
                hours = time
            else:
                # print(time)
                data = re.findall(r'\d{1,3}:\d{1,3}\s+\d{1,3}:\d{1,3}',time)
                # print(data)
                hours = ''
                day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                for hour in range(len(data)):
                    # print(data[hour].split(" ")[-1])
                    start_time = datetime.strptime(data[hour].split(" ")[0],"%H:%M").strftime("%I:%M:%p")
                    end_time = datetime.strptime(data[hour].split(" ")[-1],"%H:%M").strftime("%I:%M:%p")
                    hours+= day[hour] +" "+ str(start_time) +" "+ str(end_time) +" "
                hours = hours
            coord = soup1.find(lambda tag : (tag.name == "script") and "storeLat" in tag.text).text
            latitude = coord.split('storeLat = "')[1].split('";')[0]
            longitude = coord.split('storeLng = "')[1].split('";')[0]
            if latitude == "0":
                latitude = "<MISSING>"
            if longitude == "0":
                longitude = "<MISSING>"
            store_number = coord.split('storeId = ')[1].split(";")[0]
                    
                
            store = []
            result_coords.append((latitude,longitude))
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address.replace("Ettington",'').replace(",",''))
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")   
            store.append("UK")
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data==="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            yield store
            
       

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
