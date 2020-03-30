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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://www.honeygrow.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    loc= soup.find_all("div",{"class":"activelocation"})
    for i in loc:
        tem_var=[]
        r = session.get("https://www.honeygrow.com"+i.a['href'])
        soup1= BeautifulSoup(r.text,"lxml")
        # print("===============",i.text)
        info = list(soup1.find("div",{"class":"info"}).stripped_strings)
        
        if len(info[1].split(','))==3:
            # print("===============",i.text)
            name = info[0]
            lat = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")
            if len(lat)==2:
                lat1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[0]
                lng1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[1]
            else:
                lat1 = "<MISSING>"
                lng1 = "<MISSING>"
            city = info[1].split(',')[1]
            st = info[1].split(',')[0]
            state = info[1].split(',')[2].split( )[0]
            zip1 = info[1].split(',')[2].split( )[1]
            phone = info[-1]
            hours = (" ".join(info[2:][:-3]).split("order")[0].replace("|",""))
        elif len(info[1].split(','))==4:
            name = info[0]
            state = info[1].split(',')[-1].split( )[0]
            zip1 = info[1].split(',')[-1].split( )[1]
            city = info[1].split(',')[-2]
            st = (" ".join(info[1].split(',')[:-2]))
            lat = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")
            if len(lat)==2:
                lat1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[0]
                lng1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[1]
            else:
                lat1 = "<MISSING>"
                lng1 = "<MISSING>"
            phone = (info[-1])

        elif len(info[1].split(','))==2:
            name = info[0]
            city = info[1].split('.')[1].split(',')[0]
            st = info[1].split('.')[0]
            state = info[1].split('.')[1].split(',')[1].split( )[0]
            zip1 = info[1].split('.')[1].split(',')[1].split( )[1]
            hours = info[2]
            phone = info[-1]
            lat = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")
            if len(lat)==2:
                lat1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[0]
                lng1 = soup1.find("a",{"href":re.compile("https://www.google")})['href'].split("/@")[1].split(",")[1]
            else:
                lat1 = "<MISSING>"
                lng1 = "<MISSING>"
        # print(name)
        tem_var.append("https://www.honeygrow.com")
        tem_var.append(name.replace("\u202c",""))
        tem_var.append(st.replace("\u202c",""))
        tem_var.append(city.replace("\u202c",""))
        tem_var.append(state.replace("\u202c",""))
        tem_var.append(zip1.replace("\u202c",""))
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone.replace("\u202c",""))
        tem_var.append("<MISSING>")
        tem_var.append(lat1)
        tem_var.append(lng1)
        tem_var.append(hours.replace("\u202c",""))
        tem_var.append("https://www.honeygrow.com"+i.a['href'])
        # print(tem_var)
        return_main_object.append(tem_var)
        

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


