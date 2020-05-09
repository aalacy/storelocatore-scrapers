import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgHttpClient
import ssl

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
}

def fetch_data():
    client = SgHttpClient("unitedtkdcenters.com")
    res = client.get("/locations", headers = HEADERS)
    soup= BeautifulSoup(res,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = soup.find_all("a",{"data-ux":"ContentCardButton"})
    name3 = soup.find_all("h4",{"data-ux":"ContentCardHeading"})
    address = soup.find_all("div",{"data-ux":"ContentCardText"})
    url =[]
    for index,i in enumerate(name3):
        if "Hazlet" in  i or "North Bergen" in i or "Union City" in i:
            tem_var =[]
            name5 = (i.text)
            st5 = address[index].text.split(",")[0]
            city = address[index].text.split(",")[1].split("(")[0]
            phone = (address[index].text.split(",")[1].replace(city,""))
            state = "<MISSING>"
            zip1 =  "<MISSING>"
            tem_var.append("https://unitedtkdcenters.com")
            tem_var.append(name5)
            tem_var.append(st5)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zip1)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("https://unitedtkdcenters.com/locations")
            return_main_object.append(tem_var)
    for index,i in enumerate(k):
        if "http:" in i['href'] or  "https:" in i['href'] or "/locations" in i['href']:
            pass
        else:
            tem_var =[]
            r = client.get(i['href'], headers=HEADERS)
            url.append("https://unitedtkdcenters.com"+i['href'])
            soup2= BeautifulSoup(r,"lxml")
            phone =soup2.find("a",{"data-aid":"CONTACT_INFO_PHONE_REND"}).text
            
            full_address =soup2.find("p",{"data-aid":"CONTACT_INFO_ADDRESS_REND"}).text.replace(", United States","").replace(", USA","")
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
            if us_zip_list:
                zipp = us_zip_list[-1]
            st = full_address.replace(zipp,"").split(',')[0]
            city = full_address.replace(zipp,"").split(',')[1]
            state = (full_address.replace(zipp,"").split(',')[-1].replace(" Hackensack","<MISSING>").replace(" South Korea","<MISSING>").replace(" Fairview","<MISSING>"))
            script1 = soup2.find_all("script",{"type":"text/javascript"})
            time =''
            for j in script1:
                if 'var props = {"structuredHours"' in j.text:
                    json1 = json.loads(j.text.split("var props = ")[1].split("var context = ")[0].replace("};","}"))
                    for j in json1['structuredHours']:
                        if "openTime" in j and "closeTime" in j:
                            time = time + ' ' +j['day']+ ' '+j['openTime']+ ' '+j['closeTime']
            name1 = soup2.find("h2",{"data-aid":"CONTACT_SECTION_TITLE_REND","data-ux":"SectionSplitHeading"})
            if name1 != None:
                name = (name1.text)
            else:
                name2 = soup2.find("h1",{"data-aid":"CONTACT_SECTION_TITLE_REND","data-ux":"SectionSplitHeading"})
                name = (name2.text)
            store_name.append(name)
            tem_var.append(st.replace("Goyang-si","Goyang-si, Gyeonggi-do. 10324"))
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipp if zipp else "<MISSING>" )
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)
    for i in range(len(store_name)):
       store = list()
       store.append("https://unitedtkdcenters.com")
       store.append(store_name[i])
       store.extend(store_detail[i])
       store.append("<MISSING>")
       store.append("<MISSING>")
       store.append("<INACCESSIBLE>")
       store.append(url[i])
       if store[2] in address:
            continue
       address.append(store[2])
       if "Ilsan, South Korea" in store:
           pass
       else:
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
