import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.greenmill.com/"
    r =  session.get("https://www.greenmill.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    links = soup.find("ul",{"class":"sub-menu"}).find_all("a")
    for link in links:
        page_url = link['href']
        r1 = session.get(page_url)
        soup1 = BeautifulSoup(r1.text, "lxml")
        # print(page_url)
        if soup1.find("div",{"itemprop":"name"}):
            location_name = soup1.find("div",{"itemprop":"name"}).text.strip()
        else:
            location_name = "<MISSING>"
        if soup1.find("div",{"itemprop":"streetAddress"}):
            street_address = soup1.find("div",{"itemprop":"streetAddress"}).text.strip()
            city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
            state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
            zipp = soup1.find("span",{"itemprop":"postalCode"}).text.strip()
            phone = soup1.find("span",{"itemprop":"telephone"}).text.strip()
            latitude = soup1.find_all("meta",{"itemprop":"latitude"})[0]['content']
            longitude = soup1.find_all("meta",{"itemprop":"latitude"})[1]['content']
            hours = soup1.find("meta",{"itemprop":"openingHours"})['content'].replace(","," , ")
            # hours = (str(soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[0].text)+" "+\
            # soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[1].text+" "+\
            # soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[2].text+" "+\
            # soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[3].text).strip()
        else:
            addr = list(soup1.find("p",{"style":"font-size: 13px;"}).stripped_strings)
            # print(page_url)
            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].split(" ")[1]
            zipp = addr[1].split(",")[1].split(" ")[2]
            latitude = soup1.find_all("iframe",{"class":"gmapsloc"})[-1]['src'].split("!3d")[1].split("!")[0]
            longitude = soup1.find_all("iframe",{"class":"gmapsloc"})[-1]['src'].split("!2d")[1].split("!")[0]
            # hours = soup1.find("meta",{"itemprop":"openingHours"})['content']
            hours = (soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[1].text)+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[2].text+" "+\
            soup1.find("li",{"class":"g1-column g1-three-fifth g1-valign-top"}).find_all("p")[3].text
            hours = hours.replace("North: Hwy 71 N & 41st Ave NE East: Hwy 12 E & County Rd 9E West: Hwy 12 W & County Rd 5 South: Hwy 71 S & 45th Ave SE Minimum Delivery Order: $10","").replace("Members earn Green Mill Reward points that reward you every time you dine with us. Points can be redeemed for future savings on your favorite dishes at Green Mill. It’s our way of saying thanks! Learn more."," ").replace("North: Stillwater Blvd. South: Bailey Rd. East: Woodbury Dr. West: White Bear Ave. Minimum Delivery Order: $10","").strip()
        location_type = "Restaurant"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone )
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print("data===="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
