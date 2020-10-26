import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline ="") as output_file:
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

    base_url = "https://www.iceland.co.uk/store-finder"
    addresses = []
    r1 = session.get(base_url)
    soup = BeautifulSoup(r1.text,"lxml")
    state = soup.find_all("ul",{"class":"region-stores"})
    for data in state:
        for href in data.find_all("a"):
            r2 = session.get(href['href'])
            page_url = href['href']
            store_number= page_url.split('StoreID=')[1].split('&StoreName')[0]
            # print(page_url)
            soup1 = BeautifulSoup(r2.text,"lxml")
            try:
                streetAddress1  = soup1.find("div",{"class":"address1"}).text.strip()
            except:
                streetAddress1 =''
            try:
                streetAddress2  = soup1.find("div",{"class":"address2"}).text.strip()
            except:
                streetAddress2 =''
            try:
                name = soup1.find("h3",{"class":"store-details-bar-header"}).text.strip()
            except:
                name = "<MISSING>"
            city = re.sub(r'\s+'," ",(soup1.find("div",{"class":"city"}).text))
            if city == " ":
                city = soup1.find("div",{"class":"address2"}).text.strip()
            else:
                city = city
            try:   
                zip1 = soup1.find("div",{"class":"StateZip"}).text
            except:
                zip1 = "<MISSING>"
            try:
                phone = soup1.find("div",{"class":"phone"}).text
            except:
                phone = "<MISSING>"
            try:
                hours =  " ".join(list(soup1.find("store-hours").stripped_strings))
            except:
                hours = "<MISSING>"
            stripts = soup1.find_all("script",{"type":"application/ld+json"})
            for stript in stripts:
                if "latitude" in  stript.text:
                    jdata= json.loads(stript.text)
                    latitude = jdata['geo']['latitude']
                    longitude =jdata['geo']['longitude']
            streetAddress = streetAddress1+' '+streetAddress2
            tem_var =[]
            tem_var.append("https://www.iceland.co.uk")
            tem_var.append(name.strip() if name else "<MISSING>")
            tem_var.append(streetAddress if streetAddress else "<MISSING>")
            tem_var.append(city.strip() if city.strip()  else "<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(zip1.strip() if zip1 else "<MISSING>")
            tem_var.append("UK")
            tem_var.append(store_number)
            tem_var.append(phone.strip() if name else "<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append(hours)
            tem_var.append(page_url)
            # print(tem_var)
            yield tem_var

    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


