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
    p = 1

    url = 'https://www.howardbank.com/branch-locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo = soup.find('div', {'id': 'block-menu-menu-branch-location'})
    repo_list = repo.findAll('a')
    cleanr = re.compile('<.*?>')

    p = 1
    finallinks = []
    comlink = ""
    for link in repo_list:
        print(link.text)
        if link.text.find("Commercial") == -1:
            if link['href'].find(".com") > -1:
                link = link['href']
            else:
                link = "https://www.howardbank.com" + link['href']
            #print(link)
            finallinks.append(link)
        else:
            comlink =  "https://www.howardbank.com" + link['href']

    print(comlink)
    page = requests.get(comlink)
    soup = BeautifulSoup(page.text, "html.parser")
    detail = soup.find('div', {'class': 'field-item even'})
    detp = detail.findAll('p')
    for bank in detp:
        det = str(bank)
        det = det.replace("\n", "")
        print(det)
        start = det.find(">") + 1
        end = det.find("<", start)
        title = det[start:end]
        start = det.find(">", end) + 1
        end = det.find("<", start)
        street = det[start:end]
        start = det.find(">", end) + 1
        end = det.find("<", start)
        state = det[start:end]
        start = det.find(">", end)
        if start == -1:
            phone = "<MISSING>"
        else:
            end = det.find("<", start)
            phone = det[start + 1:end]

        start = state.find(",")

        city = state[0:start]
        start = start + 2
        end = state.find(" ", start)
        temp = state[start:end]
        start = end + 1
        end = len(state)
        pcode = state[start:end]
        state = temp
        city = city.lstrip()
        phone = phone.lstrip()
        ltype = "Branch"
        hours = "<MISSING>"
        if len(phone) < 2:
            phone = "<MISSING>"
        print(title)
        print(ltype)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(hours)
        print(p)
        print("..................................")
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
            ltype,
            "<MISSING>",
            "<MISSING>",
            hours
        ])
        p += 1


    for link in finallinks:
        print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        title = soup.find("h1").text
        detail = soup.find('div',{'class':'branch_address'})
        det = detail.find('p')
        det = str(det)
        start = det.find(">") + 1
        end = det.find("<", start)
        street = det[start:end]
        start = det.find(">", end) + 1
        end = det.find("<", start)
        state = det[start:end]
        start = det.find(">", end)
        if start == -1:
            phone = "<MISSING>"
        else:
            end = det.find("<", start)
            phone = det[start+1:end]

        start = state.find(",")
        flag = 0
        # print(start)
        if start == -1:
            start = state.find(" ", 1)

            flag = 1

        city = state[0:start]

        if flag == 1:
            start = start + 1
        else:
            start = start + 2
        end = state.find(" ", start)
        temp = state[start:end]
        start = end + 1
        end = len(state)
        pcode = state[start:end]
        state = temp

        detail = soup.find('div', {'class': 'branch_hours'})


        hdet = str(detail)
        hdet = re.sub(cleanr,"",hdet)
        hdet = hdet.replace("\n", "|")
        hdet = hdet.replace(" ", "")
        hdet = hdet.replace(": |", ":")
        hdet = hdet.replace(":||", ": ")
        hdet = hdet.replace("\n", "")
        hours = hdet

        detail = soup.find('div', {'class': 'branch_features'})
        hdet = str(detail)
        hdet = re.sub(cleanr, "", hdet)
        if hdet.find("24 hour ATM") > -1:
            ltype = "Branch | ATM"

        else:
            ltype = "Branch"
        hours = hours[1:len(hours)-2]
        city = city.lstrip()
        phone = phone.lstrip()
        title = title.lstrip()
        print(title)
        print(ltype)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(hours)
        print(p)
        print("..................................")
        if title.find("Closing") == -1:
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
                ltype,
                "<MISSING>",
                "<MISSING>",
                hours
            ])
            p += 1





    return data



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
