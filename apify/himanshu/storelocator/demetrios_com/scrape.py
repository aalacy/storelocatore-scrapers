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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://apps.demetrios.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    address1=[]
    return_main_object=[]
    address = soup.find_all("address")
    latitude = soup.find_all("latitude")
    longitude = soup.find_all("longitude")
    phone = soup.find_all("telephone")
    name = soup.find_all("location")
    
    for index,i in enumerate(address,start=0):
        tem_var=[]
        # print(i.text)
        tem_var.append("https://apps.demetrios.com")
        tem_var.append(name[index].text.encode('ascii', 'ignore').decode('ascii').strip() if name[index].text else "<MISSING>" )
        tem_var.append("<INACCESSIBLE>")
        tem_var.append("<INACCESSIBLE>")
        tem_var.append("<INACCESSIBLE>")
        tem_var.append("<INACCESSIBLE>")
        tem_var.append("US")
        tem_var.append("<MISSING>")
        if phone[index].text.strip():
           tem_var.append(phone[index].text.encode('ascii', 'ignore').decode('ascii').strip() if phone[index].text else "<MISSING>" )
        else:
           tem_var.append("<MISSING>")  
        # tem_var.append(phone[index].text.encode('ascii', 'ignore').decode('ascii').strip().replace('','<MISSING>'))
        tem_var.append("demetrios")
        tem_var.append(latitude[index].text)
        tem_var.append(longitude[index].text)
        tem_var.append("<MISSING>")
        tem_var.append(i.text.replace("\u0393","").replace("\x81","").replace("\u0158","").encode('ascii', 'ignore').decode('ascii').strip())
        if tem_var[-1] in address1:
           continue
        address1.append(tem_var[-1])
        # print(tem_var)
        return_main_object.append(tem_var)


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


