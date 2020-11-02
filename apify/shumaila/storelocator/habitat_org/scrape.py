# Import libraries
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import string
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://www.habitat.org/volunteer/near-you/find-your-local-habitat'
    page = session.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    maindiv = soup.find('select', {'class': 'form-select--white form-select chosen-disable form-item__text'})
    repo_list = maindiv.findAll('option')
    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    for n in range(1,len(repo_list)):
        repo = repo_list[n]
        link = "https://www.habitat.org" + repo['value']
        page = session.get(link)
        soup = BeautifulSoup(page.text, "html.parser")
        maindiv = soup.findAll('article', {'class': 'listing'})
        for card in maindiv:
            detail = card.text
            detail = re.sub(pattern, "|", detail)
            detail = detail.replace("\n", "|")
            detail = detail[1:len(detail)]
            start = detail.find("(")
            if start != -1:
                end = detail.find("|", start)
                phone = detail[start:end]
            else:
                phone = "<MISSING>"
            if detail.find("United States") > -1:
                ccode = 'US'
                maplink = card.find('a')
                maplink = "https://www.habitat.org" + maplink['href']

                start = 0
                end = detail.find("|", start)
                title = detail[start:end]
                start = end + 1
                end = detail.find("|", start)
                tem = detail[start:end]
                if len(tem) < 3:
                    title = title + " " + tem
                    start = end + 1
                    end = detail.find("|", start)
                    tem = detail[start:end]

                if tem.find(",") > -1:
                    start = tem.find(",")
                    city = tem[0:start]
                    start = start + 2
                    state = tem[start:len(tem)]

                    start = end + 1
                    end = detail.find("|", start)
                    street = detail[start:end]

                    start = end + 1
                    end = detail.find("|", start)
                    tem = detail[start:end]
                    if tem.find('United States') == -1:
                        start = tem.find(state)
                        if start != -1:
                            start = start + 3
                            pcode = tem[start:len(tem)]
                        else:
                            street = street + " " + tem
                            start = end + 1
                            end = detail.find("|", start)
                            tem = detail[start:end]
                            if tem.find('United States') == -1:
                                start = tem.find(state)
                                start = start + 3
                                pcode = tem[start:len(tem)]
                            else:
                                pcode = "<MISSING>"

                    else:
                        pcode= "<MISSING>"

                else:
                    city= "M"
                    state = "M"
                    street = tem

                    start = end + 1
                    end = detail.find("|", start)
                    state = detail[start:end]
                    if state.find(",") == -1:
                        street = street + " " + state
                        start = end + 1
                        end = detail.find("|", start)
                        state = detail[start:end]

                    start = state.find(",")
                    city = state[0:start]
                    start = start + 2
                    end = state.find(" ", start)
                    temp = state[start:end]
                    if temp.find("-") > -1:
                        start = temp.find("-") + 1
                        temp = temp[start:len(temp)]

                    start = end + 1
                    pcode = state[start:len(state)]
                    state = temp
                street = street.replace(",", "")
                page = session.get(maplink)
                soup = BeautifulSoup(page.text, "html.parser")
                script = soup.find('script', {'type': 'application/json'})
                script = str(script)
                start = script.find('"lat"')
                start = script.find(':', start) + 1
                end = script.find(',', start)
                lat = script[start:end]
                start = script.find('"lng"')
                start = script.find(':', start) + 1
                end = script.find('}', start)
                longt = script[start:end]

            if detail.find("Canada") > -1:
                ccode = 'CA'
                start = 0
                end = detail.find("|", start)
                title = detail[start:end]
                start = end + 1
                end = detail.find("|", start)
                tem = detail[start:end]
                if tem.find(",") > -1:
                    start = tem.find(",")
                    city = tem[0:start]
                    start = start + 2
                    state = tem[start:len(tem)]

                    start = end + 1
                    end = detail.find("|", start)
                    street = detail[start:end]

                    start = end + 1
                    end = detail.find("|", start)
                    tem = detail[start:end]
                    if tem.find('Canada') == -1:
                        start = tem.find(state)
                        if start != -1:
                            start = start + 3
                            pcode = tem[start:len(tem)]
                        else:
                            street = street + " " + tem
                            start = end + 1
                            end = detail.find("|", start)
                            tem = detail[start:end]
                            if tem.find('Canada') == -1:
                                start = tem.find(state)
                                start = start + 3
                                pcode = tem[start:len(tem)]
                            else:
                                pcode = "<MISSING>"
                    else:
                        pcode = "<MISSING>"

                else:
                    street = tem
                    if street.find(",") > -1:
                        start = end + 1
                        end = detail.find("|", start)
                        street = detail[start:end]

                    start = end + 1
                    end = detail.find("|", start)
                    temp = detail[start:end]
                    start = temp.find(" ")
                    city = temp[0:start]
                    start = start + 1
                    end = temp.find(" ", start)
                    state = temp[start:end]
                    start = state.find("-")
                    if start != -1:
                        state = state[start+1:len(state)]

                    if len(state) > 2:
                        city = city + " " + state
                        start = end + 1
                        end = temp.find(" ", start)
                        state = temp[start:end]
                        start = state.find("-")
                        if start != -1:
                            state = state[start + 1:len(state)]

                    start = end + 1
                    end = len(temp)
                    pcode = temp[start:end]

                lat = "<MISSING>"
                longt = "<MISSING>"

            title = title.replace(",", "")
            street = street.replace(",", "")
            if len(pcode) < 5:
                pcode = "<MISSING>"
            if len(phone) < 5:
                phone = "<MISSING>"
            if len(city) < 3:
                city =  "<MISSING>"
            if len(lat) < 3:
                lat =  "<MISSING>"
            if len(longt) < 3:
                longt = "<MISSING>"
            pcode = pcode.replace(".", "")
            if len(phone) < 14:
                phone = "<MISSING>"

            if len(lat) > 12 or lat.find("<") > -1:
                lat = "<MISSING>"
            if len(longt) > 12 or longt.find("<") > -1:
                longt = "<MISSING>"

            p += 1
            data.append([
                'https://www.habitat.org',
                maplink,
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
                "<MISSING>"
            ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
