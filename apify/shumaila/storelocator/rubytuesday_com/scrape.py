# Import libraries
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
    url = 'http://www.rubytuesday.com/locations'
    pnumber = 0
    flag = True
    while flag:
        link = url+"?start="+str(pnumber)+"&count=4"
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        repo_list = soup.findAll('div', {'class': 'microInfo text clearfix'})
        cleanr = re.compile('<.*?>')
        pattern = re.compile(r'\s\s+')
        for repo in repo_list:
            title = str(repo.find('h1'))
            address = str(repo.find('address').text)
            phone = repo.find('a')
            phone = str(phone['href'])
            phone = phone[4:len(phone)]
            thour = repo.find('table')
            trow = thour.findAll('tr', {'class': 'hourstr'})
            hours = ""
            for erow in trow:
                htd = erow.findAll('td')
                temp = " "
                for etd in htd:
                    temp = temp + " " + str(etd)
                    #print(temp)

                hours =  hours + "|" + temp

            title = re.sub(cleanr,"",title)
            address = re.sub(pattern, "|", address)
            address = re.sub(cleanr, "", address)
            address = address.replace(",", "")
            start = 2
            start = address.find("|",start)
            street = address[1:start]
            end = address.find("|", start+1)
            city = address[start+1:end]
            start = end + 1
            end = address.find("|", start)
            state = address[start:end]
            pcode = address[end+1: len(address)-1]
            hours = re.sub(cleanr, "", hours)
            hours = hours[3:len(hours)]
            if phone.find("-") == -1 and phone.find(")") == -1:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            if pcode.find("|") != -1:
                street = street + city
                city = state
                state = pcode[0:pcode.find("|")]
                pcode = pcode[pcode.find("|")+1 : len(pcode)]

            if len(hours) < 4:
                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(city) < 3:
                city = "<MISSING>"
            if len(pcode) < 5:
                pcode = "<MISSING>"
            if len(title) < 4:
                title = "<MISSING>"

            print(title)
            print(address)
            print(street)
            print(city)
            print(state)
            print(pcode)
            print(phone)
            print(hours)
            print("...............")

            flag = 0

            for chk in data:
                if chk[2] == street:
                    flag = 1
                    print("Already exist")
                    break

            if flag == 0:

                data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    hours
                  ])

        try:
            pagination = soup.find('ul', {'class': 'pages'})
            nextt = pagination.find('a', {'rel': 'next'})
        except:
            print("ERROR")
        try:
            print(nextt['href'])
            pnumber += 4
            print(str(pnumber))
            flag = True
        except:
            print("END")
            flag = False


    return data



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
