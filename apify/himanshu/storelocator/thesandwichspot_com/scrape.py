import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thesandwichspot_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url","location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url1="https://www.powr.io/plugins/map/wix_view.json?cacheKiller=1565172087400&compId=comp-jcccswek&deviceType=desktop&height=462&instance=yHGw_8WbCn7m6c6pR2XU186ZyTI_PDlSOhco9oNrjxk.eyJpbnN0YW5jZUlkIjoiN2IwNWYwOWYtMjE1NC00YTQxLTlmYmQtODc4Yzg5YTU4MWQ2IiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMTktMDgtMDdUMTA6NDE6NDAuNzQzWiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlwQW5kUG9ydCI6IjEyMy4yMDEuMjI2LjEyOC8zMzQ5NCIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiI1N2Q5YjhmMS1jYmIzLTRmNGMtOWJmZC0zMTI3YTZkMGQ2ZWIiLCJzaXRlT3duZXJJZCI6IjkxOGU5NTAxLTQwMGMtNDcwNS1iM2VlLTc2ZDI5NWYxM2Y2ZiJ9&locale=en&pageId=e97g9&siteRevision=349&viewMode=site&width=733"
    json_data = session.get(base_url1).json()['content']['locations']
     
    data = []
    lat_lng = {}
    for coords in json_data:
        add = coords['address'].replace(", USA","")
        address = add.split(",")
        street = ""
        city = ""
        state = ""
        zipcode = ""
        if len(address) == 3:
            street = address[0]
            city =   address[1]
            state = address[2].split(" ")[1]
            zipcode = address[2].split(" ")[2]
        lat_lng[coords['name'].replace("<p>","").replace("</p>","").replace("65th","65th Street").replace("Gateways Oaks","Gateway Oaks").replace("Elsie Ave","Elsie").replace("Stevens Creek","Steven's Creek")] = {"lat":coords['lat'],"lng":coords['lng'],"street":street,"city":city,"state":state,"zip":zipcode}
    lat_lng['Rocklin'] = {"lat":"<MISSING>","lng":"<MISSING>","street":"<MISSING>", "city":"<MISSING>","zip":"<MISSING>","state":"<MISSING>"}
    r = session.get("https://www.thesandwichspot.com/locations")    
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("div",{"role": "gridcell"})
    for loc in data_list:
        title = loc.find("h4").text
        details = loc.find_all("p",{"class":"font_7"})
        for d in details:
            if "Phone" in d.text:
                phone = d.text.replace("Phone:","")
        phone = phone.replace("COMING SOON","<MISSING>")
        try:
            lat = lat_lng[title]['lat']  
            lng = lat_lng[title]['lng'] 
        except: 
            lat_lng[title]= {"lat":"<MISSING>","lng":"<MISSING>","street":"<MISSING>", "city":"<MISSING>","zip":"<MISSING>","state":"<MISSING>"}
        if (title == "Oyster Point"):
            street = details[0].text.split("\n")[0]    
            city =   details[1].text.split("\n")[1].split(",")[0]
            state = details[1].text.split("\n")[1].split(", ")[1].split(" ")[0]
            zipcode = details[1].text.split("\n")[1].split(", ")[1].split(" ")[1]
            lat = "<MISSING>"
            lng = "<MISSING>"
        elif (title == "Stevenson Ranch" ):
            street = details[0].text.split("\n")[0]    
            city =   details[1].text.split(",")[0]
            state = details[1].text.split(",")[1].split(" ")[1]
            zipcode = details[1].text.split(",")[1].split(" ")[2]
            lat = "<MISSING>"
            lng = "<MISSING>"


        elif (title == "Delta Shore" ):
            street = details[0].text.split("\n")[0]    
            city =   details[1].text.split(",")[0]
            state = details[1].text.split(",")[1].split(" ")[1]
            zipcode = details[1].text.split(",")[1].split(" ")[2]
            lat = "<MISSING>"
            lng = "<MISSING>"


        elif(title == "Reno"):
          
            street = details[0].text.split("\n")[0]    
            print(street)
            city =   details[1].text.split(",")[1]
            state = "NV"
            zipcode = "89511"
            lat = "<MISSING>"
            lng = "<MISSING>"


        elif (lat_lng[title]['street'] == "<MISSING>" or title == "Reno"):
            street = details[0].text.split("\n")[0]    
            print(street)

            city =   details[0].text.split("\n")[1].split(",")[0]
            state = details[0].text.split("\n")[1].split(", ")[1].split(" ")[0]
            zipcode = details[0].text.split("\n")[1].split(", ")[1].split(" ")[1]
            lat = "<MISSING>"
            lng = "<MISSING>"

            
        else: 
            street = lat_lng[title]['street']
            city =   lat_lng[title]['city']
            state = lat_lng[title]['state']
            zipcode = lat_lng[title]['zip']

        data.append(
            [
                "www.thesandwichspot.com",
                "www.thesandwichspot.com/locations",
                title.lstrip(),
                street.lstrip(),
                city.lstrip(),
                state.lstrip(),
                zipcode.lstrip(),
                "US",
                "<MISSING>",
                phone.lstrip(),
                "<MISSING>",
                lat,
                lng,
                "<MISSING>"
            ]
        )   
    return data
def scrape():
    data = fetch_data()
    write_output(data)
scrape()