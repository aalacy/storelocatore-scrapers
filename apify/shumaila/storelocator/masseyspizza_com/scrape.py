# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
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
    url = 'https://www.masseyspizza.com/locations/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup)
    repo_list = soup.findAll('div', {'class': 'et_pb_text_inner'})
    cleanr = re.compile('<.*?>')
    state = ""
    p = 1
    for repo in repo_list:
        try:
            detail = repo.text
            detail = detail.replace("\n","|")
            detail = detail[1:len(detail)]
            detail = detail.replace("||","|")
            #print(detail)

            start = detail.find("|")
            if start == len(detail)-1:
                state = detail[0:start]
                if state.find("Sports Bar & Wings") > -1:
                    state = "<MISSING>"
            else:
                end = start
                start = 0
                title = detail[start:end]
                city = title
                if title.find("NOW OPEN!") > -1:
                    start = detail.find("|") + 1
                    end = detail.find("|", start)
                    title = detail[start:end]
                    start =end +1
                    end = detail.find("|", start)
                    city = detail[start:end]

                if city.find("/") > 1:
                    city = city[0:city.find("/")]


                start = end + 1
                end = detail.find("|", start)
                street = detail[start:end]

                start = end + 1
                end = detail.find("|", start)
                phone = detail[start:end]
                if phone.find("(") == -1:
                    street = street + phone
                    start = end + 1
                    end = detail.find("|", start)
                    phone = detail[start:end]

                start = end + 1
                end = detail.find("|", start)
                hours = detail[start:end]

                start = end + 1
                end = detail.find("|", start)
                temp = detail[start:end]
                if temp.find("am") > -1:
                    hours = hours + " | " + temp

                links = repo.findAll('a')
                link = links[1]
                try:
                    link = link['href']
                    start = link.find("@")
                    if start == -1:
                        lat = "<MISSING>"
                        longt = "<MISSING>"
                    else:
                        end = link.find(",",start)
                        start = start + 1
                        lat = link[start:end]
                        start = end + 1
                        end = link.find(",",start)
                        longt = link[start:end]

                except:
                    lat = "<MISSING>"
                    longt = "<MISSING>"

                print(p)
                print(title)
                print(street)
                print(city)
                print(state)
                print(phone)
                print(hours)
                print(lat)
                print(longt)
                data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    '<MISSING>',
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    lat,
                    longt,
                    hours
                ])

                p += 1
                print("..............")

        except:
            print("Empty div")
        # title = re.sub(cleanr, '', title)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
