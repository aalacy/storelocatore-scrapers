# https://www.llbean.com/llb/shop/1000001703?nav=gn-hp
# https://www.storagepro.com/


import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    p = 1
    data = []
    links = []
    ccode = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.lifestorage.com/storage-units/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    city_list = soup.findAll('a',{'class':'current-city'})
    for city in city_list:
        pagenum = 1
        ccity = city['href']
        while True:
            try:
                citylink = "https://www.lifestorage.com" + ccity + "?pagenum=" + str(pagenum)
                print(citylink)
                page1 = requests.get(citylink)
                soup1 = BeautifulSoup(page1.text, "html.parser")
                link_list = soup1.findAll('a', {'class': 'btn store'})
                if len(link_list) == 0:
                    break
                else:
                    pagenum += 1
                    #print(pagenum)
                for link in link_list:
                    link = "https://www.lifestorage.com" + link['href']
                    print(link)
                    page2 = requests.get(link)
                    soup2 = BeautifulSoup(page2.text, "html.parser")
                    detail = str(soup2)
                    start = detail.find("alternateName")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end =  detail.find('"', start)
                    title = detail[start:end]
                    start = detail.find("branchCode")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    store = detail[start:end]
                    start = detail.find("streetAddress")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    street = detail[start:end]
                    start = detail.find("addressLocality")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    city = detail[start:end]
                    start = detail.find("addressRegion")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    state = detail[start:end]
                    start = detail.find("postalCode")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    pcode = detail[start:end]
                    start = detail.find("addressCountry")
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    ccode = detail[start:end]
                    start = detail.find("latitude")
                    start = detail.find(":", start) + 2
                    end = detail.find(',', start)
                    lat = detail[start:end]
                    start = detail.find("longitude")
                    start = detail.find(":", start) + 2
                    end = detail.find('}', start)
                    longt = detail[start:end]
                    start = detail.find('"telephone"')
                    start = detail.find(":", start)
                    start = detail.find('"', start) + 1
                    end = detail.find('"', start)
                    phone = detail[start:end]
                    maind = soup2.find('div', {'id':'hours'})
                    hdetail = maind.find("ul",{'class': 'noList'})
                    hdetail = hdetail.findAll('li')
                    hours = ""
                    for li in hdetail:
                        hours = hours + li.text + " "
                    hours = re.sub(pattern," ",hours)
                    hours = hours.replace("\n","")
                    if len(hours) < 3:
                        hours = "<MISSING>"
                    if len(phone) < 5:
                        phone = "<MISSING>"

                    #print(title)
                    #print(store)
                    #print(street)
                    #print(city)
                    #print(state)
                    #print(pcode)
                    #print(ccode)
                    #print(phone)
                    #print(lat)
                    #print(longt)
                    #print(hours)
                    print(p)
                    p += 1
                    flag = True
                    i = 0
                    while i < len(data) and flag:
                        if store == data[i][8] and street == data[i][3]:
                            flag = False
                            break
                        else:
                            i += 1

                    if flag:
                        data.append([
                            'https://www.lifestorage.com/',
                            link,
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            ccode,
                            store,
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            hours
                        ])
            except:
                pass



    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

