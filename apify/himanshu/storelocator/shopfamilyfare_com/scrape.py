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

    store_name=[]
    store_detail=[]
    addressess =[]
    return_main_object=[]
    for  q  in range(0,10):
        base_url= "https://www.shopfamilyfare.com/locations?page="+str(q+1)
        r = session.get(base_url)
        soup= BeautifulSoup(r.text,"lxml")
        k= soup.find_all("div",{"class":"col-xs-12 col-lg-7"})
        for i in k:
            st = i.find_all("div",{"class":"brief"})
            names = i.find_all("h3")
            for name in names:
                store_name.append(name.text.replace("\n",""))

            for index,j in enumerate(st):
                tem_var =[]
                address = j.find('p',{"class":"address"})
                phone  = j.find('p',{"class":"phone"}).text.replace("\n","")
                # hours = j.find('p',{"class":"hours"}).text.replace("\n","")
                address1 = list(address.stripped_strings)[0]
                city = list(address.stripped_strings)[1].split(',')[0]
                state = " ".join(list(address.stripped_strings)[1].split(',')[1].split( )[:-1])
                zipcode = list(address.stripped_strings)[1].split(',')[1].split( )[-1]
                r = session.get(j.find('p', {'class': 'details'}).find('a')['href'])
                soup = BeautifulSoup(r.text, "lxml")
                # print(j.find('p', {'class': 'details'}).find('a')['href'])
                jk = soup.find('table', {'class': 'hours'}).find("tbody").find_all('tr',recursive=False)
                vk = []
                for x in jk:
                    jk = ''
                    if x.find('td', {'scope': 'rowgroup'}) != None:
                        jk = x.find('td', {'scope': 'rowgroup'}).text.strip()
                    
                    ck = ''
                    if x.find('td', {'data-title': 'Grocery'}) != None:
                        ck =' GROCERY HOURS :' + x.find('td', {'data-title': 'Grocery'}).text.strip()
                    mk = ''
                    if x.find('td', {'data-title': 'Pharmacy'}) != None:
                        mk =' PHARMACY HOURS :'  +  x.find('td', {'data-title': 'Pharmacy'}).text.strip()
                    pk = ''
                    if x.find('td', {'data-title': 'Fuel'}) != None:
                        pk =' FUEL HOURS :' + x.find('td', {'data-title': 'Fuel'}).text.strip()

                    vk.append(jk  + ck  + mk  + pk)

                hours = ' '.join(vk)
                # print(hours)

                lat = soup.find('div', {'id': 'map-canvas'})['data-latitude']
                long1 = soup.find('div', {'id': 'map-canvas'})['data-longitude']
                page_url = base_url

                # if address1 in addresses:
                #     continue
                # addresses.append(address1)
                tem_var.append("https://www.shopfamilyfare.com")
                tem_var.append(store_name[index])
                tem_var.append(address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(long1)
                tem_var.append(hours)
                tem_var.append(j.find('p', {'class': 'details'}).find('a')['href'])
                # print("===============================")
                if tem_var[2] in addressess:
                    continue
                addressess.append(tem_var[2])
                yield tem_var
    #             store_detail.append(tem_var)

    # print("==========",store_detail)
    # print("=====================================",store_name)
    # for i in range(len(store_name)):
    #     store = list()
    #     store.append("https://www.shopfamilyfare.com")
    #     store.append(store_name[i])
    #     store.extend(store_detail[i])
    #     print("data===",str(store))
    #     yield store
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


