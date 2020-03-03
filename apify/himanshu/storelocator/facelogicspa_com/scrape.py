import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    r = session.get("http://www.facelogicspa.com/pages/spas")
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find("div",{"class":"pt25 pl25 pr25 pb25"}).find_all("a"):
        if "http" not in link['href']:
            
            page_url = "http://www.facelogicspa.com" + (link['href'])
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = "<MISSING>"
            addr = list(soup1.select(".mt20.mb20")[0].find("p").stripped_strings)
            street_address = " ".join(addr[:-1])
            city = addr[-1].split(",")[0]
            state = addr[-1].split(",")[1].split(" ")[1]
            zipp =  addr[-1].split(",")[1].split(" ")[2]
            phone = soup1.select(".mt20.mb20")[0].find("p").next_sibling.strip().replace("P:",'').replace("-FACE ","").strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = "<MISSING>"
        else:
        
            if "facelogicclovis" in link['href']:
        
                page_url = "http://www.facelogicclovis.com/pages/contact"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "<MISSING>"
                addr = list(soup2.find("div",{"id":"le_54868cf8ef5a3"}).stripped_strings)
                location_name = addr[1]
                street_address = addr[2]
                city = addr[3].split(",")[0]
                state = addr[3].split(",")[1].split(" ")[1]
                zipp =  addr[3].split(",")[1].split(" ")[2]
                phone = addr[4].replace("P:",'').replace("-SKIN ","").strip()
                latitude = soup2.find("div",{"class":"le_plugin_map map-responsive"}).find("iframe")['src'].split("sll=")[1].split(",")[0]
                longitude = soup2.find("div",{"class":"le_plugin_map map-responsive"}).find("iframe")['src'].split("sll=")[1].split(",")[1].split("&")[0]
                hours = "<MISSING>"
            elif "facelogicupland" in link['href']:
                
                page_url = "https://www.facelogicupland.com/about/"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = soup2.find("div",{"class":"entry-content"}).find_all("p")[4].find_all("strong")[0].text
                street_address = soup2.find("div",{"class":"entry-content"}).find_all("p")[4].find_all("strong")[1].text
                addr = soup2.find("div",{"class":"entry-content"}).find_all("p")[4].find_all("strong")[2].text
                city = addr.split(",")[0]
                state = addr.split(",")[1].split(" ")[1]
                zipp = addr.split(",")[1].split(" ")[2]
                phone = soup2.find("div",{"class":"entry-content"}).find_all("p")[5].find("strong").text.strip()
                hours = " ".join(list(soup2.find("div",{"class":"entry-content"}).find_all("p")[6].stripped_strings)[2:])
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "facelogicco" in link['href']:
                
                page_url = "http://www.facelogicbroomfield.com/facelogicco/ContactUs"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(soup2.find_all("div",{"class":"content"})[1].stripped_strings)
                location_name = "<MISSING>"
                street_address = data[-2]
                city = data[-1].split(",")[0]
                state = data[-1].split(",")[1].split(" ")[1]
                zipp = data[-1].split(",")[1].split(" ")[2]
                phone = data[-6]
                hours = " ".join(data[1:15])
                latitude = soup2.find("iframe")['src'].split("!3d")[1].split("!2m")[0]
                longitude = soup2.find("iframe")['src'].split("!3d")[0].split("!2d")[1]
                
            elif "facelogicsc" in link['href']:
                
                page_url = link['href']
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(soup2.find_all("div",{"class":"textwidget"})[-1].stripped_strings)
                location_name = "<MISSING>"
                street_address = data[-2]
                city = data[-1].split(",")[0]
                state = data[-1].split(",")[1].split(" ")[1]
                zipp = data[-1].split(",")[1].split(" ")[2]
                phone = data[0]
                hours = " ".join(list(soup2.find_all("div",{"class":"textwidget"})[-2].find("ul").stripped_strings))
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "facelogickisco" in link['href']:
                
                page_url = link['href']
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(soup2.find_all("div",{"class":"textwidget"})[-3].stripped_strings)
                location_name = "<MISSING>"
                street_address = data[1]
                city = data[2].split(",")[0]
                state = data[2].split(",")[1].split(" ")[1]
                zipp = data[2].split(",")[1].split(" ")[2]
                phone = data[-1]
                hours = " ".join(list(soup2.find_all("div",{"class":"textwidget"})[-1].find("p").stripped_strings))
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "cleveland" in link['href']:
                
                page_url = "https://facelogiccle.com/"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                data = list(soup2.find("span",{"id":"address"}).stripped_strings)
                location_name = data[0]
                street_address = data[1]
                city = data[2].split(",")[0]
                state = data[2].split(",")[1].split(" ")[1]
                zipp = data[2].split(",")[1].split(" ")[2]
                phone = data[-2].replace("P:",'').replace("-SKIN ","").strip()
                hours = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "facelogicbcs" in link['href']:
                
                page_url = link['href']
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "FacelogicBCS"
                data = soup2.find("h3",{"class":"text-align-center"}).text.split("|")
                street_address = data[0].strip()
                city = data[1].split(",")[0].strip()
                state = data[1].split(",")[1].strip()
                zipp = data[-1].strip()
                phone = soup2.find("span",{"class":"site-phone"}).text.strip()
                hours = "<MISSING>"
                latitude = soup2.find(lambda tag: (tag.name == "script") and "mapLat" in tag.text).text.split('"mapLat":')[1].split(",")[0]
                longitude = soup2.find(lambda tag: (tag.name == "script") and "mapLat" in tag.text).text.split('"mapLng":')[1].split(",")[0]
            elif "facelogichighlandpark" in link['href']:
                
                page_url = "https://facelogichighlandpark.com/contact-us"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = soup2.find_all("h4",{'typography':"HeadingDelta"})[1].text
                data = list(soup2.find("p",{'class':'x-el x-el-p c1-23 c1-24 c1-31 c1-4r c1-a c1-33 c1-19 c1-34 c1-9 c1-36 c1-6v c1-96 c1-97 c1-98 x-d-ux x-d-aid x-d-route'}).stripped_strings)
                street_address = data[0].split("\n")[0]
                city = data[0].split("\n")[1].split(",")[0]
                state = data[0].split("\n")[1].split(",")[1].split(" ")[1]
                zipp = data[0].split("\n")[1].split(",")[1].split(" ")[2]
                phone = soup2.find("a",{'class':'x-el x-el-a c1-a c1-20 c1-5i c1-22 c1-23 c1-24 c1-25 c1-26 c1-9 c1-2b c1-2c c1-91 c1-92 x-d-ux x-d-aid'}).text.strip()
                hours = " ".join(list(soup2.find("div",{"class":"x-el x-el-p c1-23 c1-24 c1-31 c1-4r c1-a c1-33 c1-19 c1-o c1-9 c1-9d c1-9e c1-9f c1-9g c1-9h c1-9i c1-9j c1-9k c1-9l c1-9m c1-9n c1-9o c1-9p c1-9q c1-9r c1-9s c1-9t c1-9u c1-9v c1-9w c1-9x c1-9y c1-9z c1-a0 c1-a1 c1-a2 c1-a3 c1-a4 c1-36 c1-6v c1-96 c1-97 c1-98 x-d-ux x-d-route x-d-aid x-d-field-route x-rt"}).stripped_strings))
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            elif "facelogictx" in link['href']:
                
                page_url = "https://www.salonvision.com/facelogictx/AboutUs.aspx"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "<MISSING>"
                street_address = soup2.find("span",{"id":"ctl00_cphBody_A2_lblAddress"}).text.strip()
                city = soup2.find("span",{"id":"ctl00_cphBody_A2_lblCity"}).text.strip()
                state = soup2.find("span",{"id":"ctl00_cphBody_A2_lblState"}).text.strip()
                zipp = soup2.find("span",{"id":"ctl00_cphBody_A2_lblZip"}).text.strip()
                phone = soup2.find("span",{"id":"ctl00_cphBody_A2_lblPhone"}).text.strip()
                hours = " ".join(list(soup2.find("table").stripped_strings)[1:])
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                page_url = "https://facelogicspawaco.com/contact-us/"
                r2 = session.get(page_url)
                soup2 = BeautifulSoup(r2.text, "lxml")
                location_name = "<MISSING>"
                data = list(soup2.find("div",{"class":"et_pb_tab_content"}).stripped_strings)
                street_address = data[0]
                city = data[-1].split(",")[0].strip()
                state = data[-1].split(",")[1].split(" ")[1]
                zipp = data[-1].split(",")[1].split(" ")[2]
                phone = soup2.find_all("div",{"class":"et_pb_tab_content"})[-2].text.replace("Phone Number:","").replace("Email: [email protected]","").strip()
                hours = " ".join(list(soup2.find_all("div",{"class":"et_pb_tab_content"})[-1].stripped_strings)[:-1])
                latitude = soup2.find("iframe")['src'].split("!3d")[1].split("!2m")[0]
                longitude = soup2.find("iframe")['src'].split("!3d")[0].split("!2d")[1]
        
        store = []
        store.append('http://www.facelogicspa.com/')
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(page_url)
        # print(store)
        yield store
        

   


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
