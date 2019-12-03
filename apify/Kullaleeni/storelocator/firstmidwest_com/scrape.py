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

    data = []
    p = 1
    links = []
    pattern = re.compile(r'\s\s+')
    url = 'https://www.firstmidwest.com/locations/'
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text, "html.parser")
    mainlist = soup.find('div',{'class':'rio-regionList'})
    mainlist = mainlist.findAll('a',{'class':'gaq-link'})
    print(len(mainlist))
    mainlist.append('https://www.firstmidwest.com/locations/')
    for states in mainlist:
        if states == 'https://www.firstmidwest.com/locations/':
            statelink = states
        else:
            statelink = "https://www.firstmidwest.com"+ states['href']
        #print(statelink)
        page = requests.get(statelink, verify=False)
        soup = BeautifulSoup(page.text, "html.parser")

        maindiv = soup.find('div',{'id':'rls-map'})
        #print(maindiv)
        maindiv = str(maindiv)
        start = 0
        num = 0
        while True:
            start = maindiv.find('a href=',start)
            if start != -1:
                start =  maindiv.find('"',start)+1
                end = maindiv.find('"', start)
                link = maindiv[start:end]
                if link.find("google") == -1:
                    link = link.replace("/","")
                    link = link.replace('\\', "/")
                    link = link[0:len(link)-1]
                    flag = True
                    i = 0
                    while i < len(links):
                        if link == links[i]:
                            flag = False
                            break
                        i += 1
                    if flag:
                        links.append(link)
                        num += 1
                    #print(link)
                start = end + 1
            else:
                break
        #print(num)

    print(len(links))
    ind = 0
    while True:
        try:
        #print(link)
            link = links[ind]
            page = requests.get(link, verify=False)
            soup = BeautifulSoup(page.text, "html.parser")
            title = soup.find('div',{'id':'rio-locName'}).text
            address = soup.find('div', {'class': 'rio-addrText'})
            address = address.findAll('span')
            if len(address) == 4:
                street = address[0].text
                city = address[1].text
                state = address[2].text
                pcode = address[3].text
            elif len(address) == 5:
                street = address[0].text + " " + address[1].text
                city = address[2].text
                state = address[3].text
                pcode = address[4].text
            try:
                phone = soup.find('span',{'class':'rio-phoneText'}).text
            except:
                phone = "<MISSING>"
            try:
                hoursd =  soup.find('div',{'id':'rio-locHoursServices'})
                hoursd = hoursd.findAll('div',{'class':'hours'})
                lhours = hoursd[0].text
                lhours = re.sub(pattern," ",lhours)
                dhours = hoursd[1].text
                dhours = re.sub(pattern, " ", dhours)
                hours = "Lobby Hours : " + lhours + " | Drive Up Hours : " + dhours



            except:
                hours= "<MISSING>"
            try:
                hoursd = soup.find('div', {'id': 'rio-atmHours'})
                hoursd = hoursd.find('div', {'class': 'hours'}).text
                hoursd = re.sub(pattern, " ",hoursd)
                if hours == "<MISSING>":
                    temp = "ATM Hours : "
                    hours = temp + hoursd
                else:
                    temp ="|ATM Hours : "
                    hours = hours + temp + hoursd

            except:
                pass
            try:
               services = soup.find('div', {'id': 'rio-locServices'}).text
               services= services.replace("\n","|")
               services = services[1:len(services)-2]
               services = services[services.find("|")+1:len(services)]
               services = services.replace("ATM|ATM 24 Hr","ATM")
            except:
                pass
            soup = str(soup)
            start = soup.find('RLS.centerLat')
            start = soup.find('=',start) + 2
            end =  soup.find(';',start)
            lat = soup[start:end]
            start = soup.find('RLS.centerLng')
            start = soup.find('=', start) + 2
            end = soup.find(';', start)
            longt = soup[start:end]

            start = link.find('banking-')
            start = link.find('-',start)+1
            end = link.find('.', start)
            store = link[start:end]
            store = store.replace("atm","")
            if store.isdigit():
                pass
            else:
                store = "<MISSING>"
            data.append([
                'https://www.firstmidwest.com',
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                services,
                lat,
                longt,
                hours
            ])
            #print(p,",",data[p-1])
            p += 1
            ind += 1
            if ind == len(links):
                break
        except:
            pass

    return data




def scrape():
    data = fetch_data()
    write_output(data)

scrape()

