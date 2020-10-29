import csv
import requests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lifechurch_tv')



def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url"
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    data = []
    # Message: unexpected alert open: {Alert text : Cannot contact reCAPTCHA. Check your connection and try again.}
    # driver = SgSelenium().chrome()

    location_url = "https://www.life.church/locations/?utm_source=life.church&utm_medium=website&utm_content=Header-Locations&utm_campaign=Life.Church"
    r1 = requests.get(location_url)
    soup = BeautifulSoup(r1.text,"html.parser")
    
    for div in soup.find("section",{"id":"map"}).find_all("div",{"class":"location-state"}):
        for d in div.find_all("a",{"class":"campus-link"}):
            page_url = "https://www.life.church"+d['href']
            # logger.info("vivek~~~~~~~~~~~~~~~~ ",)
            if "/contact" in d['href']:
                continue
            r1 = requests.get("https://www.life.church"+ d['href'])
            soup1= BeautifulSoup(r1.text,"lxml")
            if "/coloradosprings" in d['href']:
                location_name ="Tony Doland"
                full = list(soup1.find("div",{'class':"columns small-12 large-5 large-push-1"}).stripped_strings)
                # logger.info(full)
                city  = full[3].split(",")[0]
                state = full[3].split(",")[1].strip().split( )[0]
                zipp  = full[3].split(",")[1].strip().split( )[1]
                phone_numbers="719-662-2421"
                street_address = list(soup1.find("div",{'class':"columns small-12 large-5 large-push-1"}).stripped_strings)[2]
                latitude = soup1.find("meta",{"property":"place:location:latitude"})['content']
                longitude = soup1.find("meta",{"property":"place:location:longitude"})['content']
                hours = "<MISSING>"
                store=[]
                store.append("https://www.life.church/")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone_numbers)
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # logger.info("----------------------",store)
                yield store
                # logger.info(list(soup1.find("div",{'class':"columns small-12 large-5 large-push-1"}).stripped_strings)[1])
            else: 
                # logger.info(soup1)
                store=[]           
                location_name = soup1.find("span",{"class":"campus-name"}).text.strip()
                full = list(soup1.find("a",{"class":"campus-address"}).stripped_strings)
                if full[0]=="Meets at South Valley Middle School" or full[0]=="Meets at Millard West High School" or full[0]=='Meets at Legacy High School!':
                    del full[0]
                street_address  = full[0]
                # logger.info(list(soup1.find("a",{"class":"campus-address"}).stripped_strings))
                city  = full[1].split(",")[0]
                state = full[1].split(",")[1].strip().split( )[0]
                zipp  = full[1].split(",")[1].strip().split( )[1]
                latitude = soup1.find("a",{"class":"campus-address"})['href'].split("//")[-1].split(",")[0]
                longitude = soup1.find("a",{"class":"campus-address"})['href'].split("//")[-1].split(",")[1]
                phone = soup1.find("a",{"href":re.compile("tel")}).text.strip()
                try:
                    hours = (" ".join(list(soup1.find("div",{"class":"campus-service-times small-12 small-centered medium-6 large-12 columns"}).find("table").stripped_strings)))
                except:
                    hours = "<MISSING>"
                store.append("https://www.life.church/")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append(page_url)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # logger.info("----------------------",store)
                yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


