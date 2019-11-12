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
    url = 'https://www.storagepro.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    codedetail = soup.find('div',{'class':'column_second us_can_states'})
    link_list = codedetail.findAll('a',{'class':'state_name'})
    for link in link_list:
        links.append(link['href'])
        ccode.append("US")
    codedetail = soup.find('div', {'class': 'column_second canada_state us_can_states'})
    link_list = codedetail.findAll('a', {'class': 'state_name'})
    for link in link_list:
        links.append(link['href'])
        ccode.append("CA")
    print(len(links))
    print(len(ccode))
    for i in range(0,len(links)):
        statelink = "https://www.storagepro.com" + links[i] #['href']
        #print("State ", statelink)
        page1 = requests.get(statelink)
        soup1 = BeautifulSoup(page1.text, "html.parser")
        city_list =  soup1.findAll('a',{'class':'popular_city'})
        if len(city_list) == 0:
            try:
                title = soup1.find("h1").text
                street = soup1.find('span', {'itemprop': 'streetAddress'}).text
                city = soup1.find('span', {'itemprop': 'addressLocality'}).text
                state = soup1.find('span', {'itemprop': 'addressRegion'}).text
                pcode = soup1.find('span', {'itemprop': 'postalCode'}).text
                phone = soup1.find('a', {'class': 'green_text ga_phone_call phone_customize'}).text
                coord = soup1.find('a', {'class': 'map_it_tag green_text ga_outbound_link'})
                lat = coord['data-lat']
                longt = coord['data-long']
                hours = soup1.find('div', {'class': 'gate_access_wrapper right'}).text
                hours = re.sub(pattern, " ", hours)
                soup1 = str(soup1)
                start = soup1.find('setCustomDimension')
                start = soup1.find("9,", start) + 1
                start = soup1.find('"', start) + 1
                end = soup1.find('"', start)
                store = soup1[start:end]
                hours = hours.lstrip()
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
                #print(ccode[i])
               # print(phone)
                #print(lat)
                #print(longt)
                #print(hours)
                #print(p)
                p += 1
                flag = True
                m = 0
                while i < len(data) and flag:
                    if store == data[m][8] and street == data[m][3]:
                        flag = False
                        break
                    else:
                        m += 1
                if flag:
                    data.append([
                        'https://www.storagepro.com/',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode[i],
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                    ])
            except:
                pass
        #print(len(city_list))
        for city in city_list:
            count = city.find('span',{'class': 'facilities_count right'}).text
            count = count.replace(" Facilities","")
            count = count.replace(" Facility", "")
            count = count.strip()
            #print("Count=", count)
            if count != "0":
                citylink = "https://www.storagepro.com" + city['href']
                #print("City= ", citylink)
                #return
                page2 = requests.get(citylink)
                soup2 = BeautifulSoup(page2.text, "html.parser")
                detail_list = soup2.findAll('a',{'class': 'ajax-slider'})
                #print("LEN = ",len(detail_list))
                if len(detail_list) == 0:
                    try:
                        title = soup2.find("h1").text
                        street = soup2.find('span', {'itemprop': 'streetAddress'}).text
                        city = soup2.find('span', {'itemprop': 'addressLocality'}).text
                        state = soup2.find('span', {'itemprop': 'addressRegion'}).text
                        pcode = soup2.find('span', {'itemprop': 'postalCode'}).text
                        phone = soup2.find('a', {'class': 'green_text ga_phone_call phone_customize'}).text
                        coord = soup2.find('a', {'class': 'map_it_tag green_text ga_outbound_link'})
                        lat = coord['data-lat']
                        longt = coord['data-long']
                        hours = soup2.find('div', {'class': 'gate_access_wrapper right'}).text
                        hours = re.sub(pattern, " ", hours)
                        soup2 = str(soup2)
                        start = soup2.find('setCustomDimension')
                        start = soup2.find("9,", start) + 1
                        start = soup2.find('"', start) + 1
                        end = soup2.find('"', start)
                        store = soup2[start:end]
                        hours = hours.lstrip()
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
                        #print(ccode[i])
                        #print(phone)
                        #print(lat)
                        #print(longt)
                        #print(hours)
                        #print(p)
                        p += 1
                        flag = True
                        m = 0
                        while m < len(data) and flag:
                            if store == data[m][8] and street == data[m][3]:
                                flag = False
                                break
                            else:
                                m += 1
                        if flag:
                            data.append([
                                'https://www.storagepro.com/',
                                link,
                                title,
                                street,
                                city,
                                state,
                                pcode,
                                ccode[i],
                                store,
                                phone,
                                "<MISSING>",
                                lat,
                                longt,
                                hours
                            ])
                    except:
                        pass
                for link in detail_list:
                    link = "https://www.storagepro.com" +  link['href']
                    #print("Branch = ", link)

                    page3 = requests.get(link)
                    soup3 = BeautifulSoup(page3.text, "html.parser")
                    title = soup3.find("h1").text
                    street = soup3.find('span', {'itemprop': 'streetAddress'}).text
                    city = soup3.find('span', {'itemprop': 'addressLocality'}).text
                    state = soup3.find('span', {'itemprop': 'addressRegion'}).text
                    pcode = soup3.find('span', {'itemprop': 'postalCode'}).text
                    phone = soup3.find('a',{'class': 'green_text ga_phone_call phone_customize'}).text
                    coord = soup3.find('a',{'class': 'map_it_tag green_text ga_outbound_link'})
                    lat = coord['data-lat']
                    longt = coord['data-long']
                    hours= soup3.find('div',{'class': 'gate_access_wrapper right'}).text
                    hours = re.sub(pattern," ",hours)
                    soup3 = str(soup3)
                    start = soup3.find('setCustomDimension')
                    start = soup3.find("9,", start) + 1
                    start = soup3.find('"', start) + 1
                    end = soup3.find('"', start)
                    store = soup3[start:end]
                    hours = hours.lstrip()
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
                    #print(ccode[i])
                    #print(phone)
                    #print(lat)
                    #print(longt)
                    #print(hours)
                    #print(p)
                    p += 1
                    flag = True
                    m = 0
                    while m < len(data) and flag:
                        if store == data[m][8] and street == data[m][3]:
                            flag = False
                            break
                        else:
                            m += 1
                    if flag:
                        data.append([
                        'https://www.storagepro.com/',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode[i],
                        store,
                        phone,
                        "<MISSING>",
                        lat,
                        longt,
                        hours
                        ])
            #print("............................")

    return data



def scrape():
    data = fetch_data()
    write_output(data)

scrape()

