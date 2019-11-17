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
    url = 'https://papemachinery.com/locations'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    repo_list = soup.findAll('a', {'class': 'location-name'})
    cleanr = re.compile('<.*?>')
    phoner = re.compile('(.*?)')
    for repo in repo_list:
        print(repo['href'])
        link = repo['href']
        page = requests.get(link)
        det = BeautifulSoup(page.text, "html.parser")
        detail = str(det)
        start = detail.find("@context")
        start = detail.find("name", start)
        start = detail.find(':', start)+3
        end = detail.find(',', start)
        title = detail[start:end-1]
        print(title)
        start = detail.find("streetAddress", end)
        start = detail.find(':', start) + 3
        end = detail.find(',', start)
        street = detail[start:end - 1]
        print(street)
        start = detail.find("addressLocality", end)
        start = detail.find(':', start) + 3
        end = detail.find(',', start)
        city = detail[start:end - 1]
        print(city)
        start = detail.find("addressRegion", end)
        start = detail.find(':', start) + 3
        end = detail.find(',', start)
        state = detail[start:end - 1]
        if state == "Washington":
            state = "WA"
        print(state)
        start = detail.find("postalCode", end)
        start = detail.find(':', start) + 3
        end = detail.find(',', start)
        pcode = detail[start:end - 1]
        print(pcode)
        start = detail.find("addressCountry", end)
        start = detail.find(':', start) + 3
        end = detail.find('}', start)
        ccode = detail[start:end - 3]
        ccode = re.sub("\r", "", ccode)
        ccode = re.sub("\n", "", ccode)
        ccode = re.sub('"', "", ccode)
        print(ccode)
        start = detail.find("latitude", end)
        start = detail.find(':', start) + 2
        end = detail.find(',', start)
        lat = detail[start:end - 1]
        print(lat)
        start = detail.find("longitude", end)
        start = detail.find(':', start) + 2
        end = detail.find('}', start)
        longt = detail[start:end - 3]
        longt = re.sub("\r", "", longt)
        longt = re.sub("\n", "", longt)
        longt = re.sub('"', "", longt)
        print(longt)
        start = detail.find("telephone", end)
        start = detail.find(':', start) + 3
        end = detail.find('}', start)
        phone = detail[start:end - 3]
        phone = re.sub("\r", "", phone)
        phone = re.sub("\n", "", phone)
        phone = re.sub('"', "", phone)
        print(phone)
        try:
            hourd = det.find('table',{'class': 'simple'})
            tbody =hourd.find('tbody')
            trows = tbody.findAll('tr')
            hours = ""
            for detrows in trows:
                tempt = ""
                tds = detrows.findAll('td')
                for tdetail in tds:
                    tempt = tempt + " " + tdetail.text

                hours = hours + " " + tempt

            hours = hours.lstrip()
        except:
            hours = "<MISSING>"
        print(hours)
        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            ccode,
            "<MISSING>",
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
