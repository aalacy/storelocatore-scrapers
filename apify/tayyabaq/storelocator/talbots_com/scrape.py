import csv
import os
import requests
from bs4 import BeautifulSoup
import re, time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    store_links =[]
    clear_links =[]
    #outlet stores
    url = 'https://www.talbots.com/outlets'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store=soup.find_all('a')
    for i in store:
        if i['href'].startswith("/store?"):
            link='https://www.talbots.com'+i['href']
            store_links.append(link)
    for link in store_links:
        street=""
        st=requests.get(link)
        soup=BeautifulSoup(st.content,"html.parser")
        loc=soup.find('h1',class_='store-locator-header').text
        details=soup.find('div',class_='store-details')
        add=details.text
        add2=(add.split("Address:")[1]).split("Store")[0]
        add1=usaddress.parse(add2)
        if link in ['https://www.talbots.com/store?StoreID=04906','https://www.talbots.com/store?StoreID=04401','https://www.talbots.com/store?StoreID=04001','https://www.talbots.com/store?StoreID=04014','https://www.talbots.com/store?StoreID=04026','https://www.talbots.com/store?StoreID=04058']:
            for key,values in add1:
                if values in ['AddressNumber','StreetName','StreetNamePostType','StreetNamePostDirectional','Recipient','OccupancyIdentifier',"USPSBoxType",'USPSBoxID']:
                    street+=" "
                    street+=key
                elif values in ['PlaceName']:
                    cty=key
                elif values in ['StateName']:
                    sts=key
                elif values in ['ZipCode']:
                    zcode=key
        else:
            for key,values in add1:
                if values in ['AddressNumber','StreetName','StreetNamePostType','StreetNamePostDirectional','OccupancyIdentifier',"USPSBoxType",'USPSBoxID']:
                    street+=" "
                    street+=key
                elif values in ['PlaceName']:
                    cty=key
                elif values in ['StateName']:
                    sts=key
                elif values in ['ZipCode']:
                    zcode=key
        num=soup.find("div",class_="number").text
        num=num.replace("Store #","")
        ph=soup.find("a",class_="alt-link").text
        hours= str(soup.find('div',class_="hours"))
        hours=hours.replace("<br/>"," ")
        hours=(hours.split("</div>")[1]).split("</div")[0]
        data.append([
                'https://www.talbots.com/',
                 link,
                 loc,
                 street,
                 cty,
                 sts,
                 zcode,
                 'US',
                 num,
                 ph,
                 "Outlet",
                 '<MISSING>',
                 '<MISSING>',
                 hours
                 ])
    #clearance stores    
    url = 'https://www.talbots.com/clearance'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    store=soup.find_all('a')
    for i in store:
        if i['href'].startswith("/store?"):
            link='https://www.talbots.com'+i['href']
            clear_links.append(link)
    for link in clear_links:
        street=""
        st=requests.get(link)
        soup=BeautifulSoup(st.content,"html.parser")
        loc=soup.find('h1',class_='store-locator-header').text
        details=soup.find('div',class_='store-details')
        add=details.text
        add=(add.split("Address:")[1]).split("Store")[0]
        if link == 'https://www.talbots.com/store?StoreID=00830':
            ctry='CA'
            zcode=add[-10:]
            sts=add[-13:-10]
            add=usaddress.parse(add)
            for key,values in add:
                if values in ['AddressNumber','StreetName','StreetNamePostType','StreetNamePostDirectional','OccupancyIdentifier',"USPSBoxType",'USPSBoxID']:
                    street+=" "
                    street+=key
                elif values in ['PlaceName']:
                    cty=key                 
        else:
            add=usaddress.parse(add)
            for key,values in add:
                if values in ['AddressNumber','StreetName','StreetNamePostType','StreetNamePostDirectional','OccupancyIdentifier',"USPSBoxType",'USPSBoxID']:
                    street+=" "
                    street+=key
                elif values in ['PlaceName']:
                    cty=key
                elif values in ['StateName']:
                    sts=key
                elif values in ['ZipCode']:
                    zcode=key
            ctry= 'US'        
        num=soup.find("div",class_="number").text
        num=num.replace("Store #","")
        ph=soup.find("a",class_="alt-link").text
        hours= str(soup.find('div',class_="hours"))
        hours=hours.replace("<br/>"," ")
        hours=(hours.split("</div>")[1]).split("</div")[0]
        data.append([
                'https://www.talbots.com/',
                 link,
                 loc,
                 street,
                 cty,
                 sts,
                 zcode,
                 ctry,
                 num,
                 ph,
                 "Clearance",
                 '<MISSING>',
                 '<MISSING>',
                 hours
                 ])
    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()