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
    url = 'https://www.katahdintrust.com/Locations-Hours'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # print(soup)
    repo_list = soup.findAll('table', {'class': 'Subsection-Table'})
    p=0
    for repo in repo_list:
        if p == 0:
            p = 1
        else:
            text = str(repo.find('h3'))
            start = text.find(">")+1
            end = text.find("<",start)
            title = text[start:end]
            repo = str(repo)
            start = repo.find("/h4", start)

            start = repo.find("<p", start) + 3
            end = repo.find("</p", start)
            next = end + 4
            text = repo[start:end]
            # print(text)
            start = text.find("<br")
            mid = text.find("<br",start+5)
            if mid == -1:
                address = text[0:start]

            else:
                address = text[0:start]
                address = address + text[start+6:mid]
                start = mid

            start = start + 6
            state = text[start:len(text)]
            start = state.find(",")
            city = state[0:start]
            state = state[start+2:len(state)]
            start = state.find(" ")
            xip = state[start+1:len(state)]
            print(xip)
            state = state[0:start]

            hours = ' '
            phone = ' '
            loctype = ' '
            start = next
            i = 1
            while i < 4:
                start = repo.find("<h4", start) + 4
                end = repo.find("<", start)
                temp = repo[start:end]
                # print(temp)
                start = temp.find("Hours")

                if start == -1:

                    start = temp.find("Phone")
                    if start == -1:
                        start = temp.find("ATM")
                        if start > -1:
                            start = repo.find("<p", end) + 3
                            end = repo.find("</p", start)
                            loctype = repo[start:end]

                    else:
                        start = repo.find("<p", end) + 3
                        start = repo.find(">", start)+1
                        end = repo.find("</p", start)
                        phone = phone + repo[start:end]

                    break
                else:
                    start = repo.find("<p", end) + 3
                    end = repo.find("</p", start)
                    hours = hours + " " + repo[start:end]
                    start = repo.find("<p", end) + 3
                    end = repo.find("</p", start)
                    loctype = repo[start:end]
                    start = loctype.find("ATM")
                    if start == -1:
                        hours = hours + " " + loctype
                        start = repo.find("<p", end) + 3
                        end = repo.find("</p", start)
                        loctype = repo[start:end]
                        start = loctype.find("ATM")
                        if start == -1:
                            loctype = '<MISSING>'

                start = end
                if i == 3:
                    break
                i += 1

            cleanr = re.compile('<.*?>')
            hours = re.sub(cleanr, '', hours)
            phone = re.sub(cleanr, '', phone)
            start = loctype.find("MISSING")
            if start == -1:
                loctype = re.sub(cleanr, '', loctype)
                start = loctype.find(" ")
                loctype = loctype[start + 1:len(loctype)]

            if len(hours) == 1:
                hours = '<MISSING>'
            start = hours.find("class")
            if start > 0:
                hours = hours[0:start]
            if len(phone) == 1:
                phone = '<MISSING>'
            print(len(loctype))
            if len(loctype) < 2:
                loctype = '<MISSING>'
            if phone.find("Toll") != -1:
                start = phone.find("Toll")-2
                phone = phone[0:start]

            data.append([
                url,
                title,
                address,
                city,
                state,
                xip,
                'US',
                "<MISSING>",
                phone,
                loctype,
                "<MISSING>",
                "<MISSING>",
                hours
            ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
