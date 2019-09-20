# Import libraries
import xml
import lxml
import requests
from bs4 import BeautifulSoup
import csv
import string
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'http://pizzafusion.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('a',{'class': 'borderImg'})
    cleanr = re.compile('<.*?>')
    temp = "1"
    end = 0
    for repo in repo_list:
        check = repo['href']
        if check != '#':
            try:
                link = "http://pizzafusion.com" + repo['href']
                print(link)
                page = requests.get(link)
                soup = BeautifulSoup(page.text, "html.parser")
                detail = soup.find('td', {'class': 'locations'})
                title = detail.find('strong').text
                try:
                    store = detail.find('small').text
                    storeline = str(detail)
                    start = storeline.find('Store#')
                    start = storeline.find('>', start)+1
                    end = storeline.find('<', start)
                    store = storeline[start:end]
                    if len(store) == 0:
                        store = "<MISSING>"
                except:
                    store = "<MISSING>"
                temp = detail.findAll('span')
                print("................")
                print(len(temp))
                if len(temp) < 2:
                    temp = str(temp)
                    detail = str(detail)
                    start = detail.find('<br')+3
                    if store != "<MISSING>":
                        print("NOOOOT")
                        start = detail.find('<br', start) + 3
                    start = detail.find('<br', start) + 5
                    end = detail.find('<br',start)
                    street = detail[start:end]
                    street = re.sub(cleanr, '', street)
                    street = re.sub("\r\n", '', street)
                    print("Street>>>>"+street)
                    start = end + 5
                    end = detail.find('<br', start)
                    state = detail[start:end]
                    state = re.sub(cleanr, '', state)
                    state = re.sub("\r\n", '', state)
                    start = state.find(",")
                    city = state[0:start]
                    print(city)
                    start = start + 2
                    state = state[start:len(state)]
                    state,xip = state.split(" ")
                    print(state)

                    if len(xip) == 4:
                        xip = "0" + xip
                    print(xip)
                    start= detail.find("Phone")+7
                    end = detail.find("<",start)
                    phone = detail[start:end]
                    print(phone)
                    start = detail.find("Hours",end) + 7
                    end = detail.find("<td", start) - 4
                    hours = detail[start:end]
                    hours = re.sub(cleanr, ' ', hours)
                    hours = re.sub("\r\n", '', hours)
                    hours = re.sub("/strong>", '', hours)
                    hours = re.sub("amp;", '', hours)

                else:
                    num = detail.findAll('span')
                    if len(num) == 7:
                        street = str(num[0])
                        street = re.sub(cleanr, '', street)
                        state = str(num[1])
                        state = re.sub(cleanr, '', state)
                        start = state.find(",")
                        city = state[0:start]
                        print(city)
                        start = start + 2
                        state = state[start:len(state)]
                        state, xip = state.split(" ")
                        print(state)
                        print(xip)
                        phone = str(num[3])
                        phone = re.sub(cleanr, '', phone)
                        phone = phone[7:len(phone)]
                        hours = str(num[5]) + " " + str(num[6])


                    elif len(num) == 8:
                        street = str(num[1])
                        street = re.sub(cleanr, '', street)
                        state = str(num[2])
                        state = re.sub(cleanr, '', state)
                        start = state.find(",")
                        city = state[0:start]
                        print(city)
                        start = start + 2
                        state = state[start:len(state)]
                        state, xip = state.split(" ")
                        print(state)
                        print(xip)
                        phone =  str(num[4])
                        phone = re.sub(cleanr, '', phone)
                        phone = phone[7:len(phone)]
                        hours = str(num[6]) + " " + str(num[7])

                    hours = re.sub(cleanr, ' ', hours)
                    hours = re.sub("\r\n", '', hours)
                    hours = re.sub("amp;", '', hours)

                if hours.find("Fast") > 0:
                    start = hours.find("Fast")
                    hours = hours[0:start-2]
                    hours =  hours = re.sub("\n\r", '', hours)
                print(hours)



                data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    xip,
                    'US',
                    store,
                    phone,
                    '<MISSING>',
                    '<MISSING>',
                    '<MISSING>',
                    hours
                    ])
            except:
                print("Not Found")









    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
