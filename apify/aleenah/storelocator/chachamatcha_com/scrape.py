import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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

session = SgRequests()

def fetch_data():
    # Your scraper here

    res=session.get("https://chachamatcha.com/pages/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('div', {'class': 'location__item-content'})
    all=[]
    for store in stores:
        l=store.find('h3').text
        if "Stay  Tuned"in l:
            continue
        st=store.find('strong').text
        add=store.find('span').text.replace("  "," ")

        print(add)
        if "," in add:
            add=add.split(",")
            c = add[0]
            add=add[1].strip().split(" ")
            s = add[0]
            z = add[1]
        else:
            sz=add.strip().split(" ")
            print(add)
            print(sz)
            z=sz[-1]
            s=sz[-2]
            c= add.replace(s+" "+z,"").strip()

        tim=store.find('div',{'class':'location__item-details'}).text.replace("Hours","").replace("Menu","").strip().replace("\n"," ")
        all.append([
            "https://chachamatcha.com",
            l,
            st,
            c,
            s,
            z,
            "US",
            "<MISSING>",  # store #
            "<MISSING>",  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim.strip(),  # timing
            "https://chachamatcha.com/pages/locations"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
