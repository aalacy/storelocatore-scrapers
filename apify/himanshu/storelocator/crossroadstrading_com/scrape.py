import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    base_url = "https://crossroadstrading.com/location/"
    for i in range(1,9):
        r = session.get("https://crossroadstrading.com/location/page/"+str(i),headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        return_main_object  = []
        links = []
        title = soup.find_all("h2",{"class":"entry-title-archive"})
        tag_lat = soup.find_all(lambda tag: (tag.name == "script" or tag.name == "h2") and "new google.maps.LatLng" in tag.text.strip())
        for index1,i in enumerate(soup.find_all("div",{"class": "row vc_row-fluid store-contact"})):
            full = list(i.stripped_strings)[2:5]
           
            if full[-1]=="Phone Number":
                del full[-1]
            if full[-1]=="phone":
                del full[-1]
            if len(full)==1:
                street_address  = " ".join(full).replace(". ",',').split(",")[0]
                city = " ".join(full).replace(". ",',').split(",")[1]
                state = " ".join(full).replace(". ",',').split(",")[-1].strip().split( )[0]
                zipp = " ".join(full).replace(". ",',').split(",")[-1].strip().split( )[1]
            else:
                street_address =full[0]
                state = full[-1].replace("Culver City 90066",'Culver City, 90066').split(",")[-1].strip().split( )[0].replace("90066","<MISSING>")
                zipp = full[-1].replace("Culver City 90066",'Culver City, 90066').split(",")[-1].strip().split( )[-1]
                city = full[-1].replace("Culver City 90066",'Culver City, 90066').split(",")[0]
            name = title[index1].text.strip()
            hours_of_operation=''
      

            latitude = str(tag_lat[index1]).split("new google.maps.LatLng(")[1].split(");")[0].split(",")[0]
            longitude = str(tag_lat[index1]).split("new google.maps.LatLng(")[1].split(");")[0].split(",")[1]
            full = list(i.stripped_strings)
            # phone = list(i.stripped_strings)[6].replace(" ",'').replace(".",' ')
            hours_of_operation = " ".join(list(i.stripped_strings)[10:])


            try:
                page_url = title[index1].find("a")['href']
                r1 = session.get(page_url,headers=headers)
                soup1 = BeautifulSoup(r1.text,"lxml")
                try:
                    hours_of_operation =" ".join(list(soup1.find("ul",{"class":"store-hours"}).stripped_strings))
                except :
                    hours_of_operation = hours_of_operation

            except:
                page_url="<MISSING>"

            phone =''
            data = list(i.stripped_strings)
            for index,i in enumerate(data):
                if data[index]=="Phone Number":
                    phone = data[index+1].replace(" ",'').replace(".",' ')

            store = []
            store.append("https://crossroadstrading.com")
            store.append(name)
            store_number = "<MISSING>"
            store.append(street_address.replace('Westpark Plaza, ','') if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append( "US")
            store.append(store_number if store_number else"<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("----------------------",store)
            yield store
     


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
