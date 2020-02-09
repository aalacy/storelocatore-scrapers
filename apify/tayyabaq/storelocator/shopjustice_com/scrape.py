from bs4 import BeautifulSoup
import re
import csv
import requests
import time


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(
            ["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
             "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        for row in data:
            writer.writerow(row)

data_list = []
def fetch_data():
    try:
        base = 'https://stores.shopjustice.com/'
        urls = 'https://stores.shopjustice.com/directory'
        html = requests.get(urls).text
        soup = BeautifulSoup(html)
        content = soup.find("div", class_="Directory-content").findAll("a")
        unique = []
        state = []
        citi = []

        for i in content:
            state_loc = (base + i.get('href'))
            state.append(state_loc)
            url = re.findall(r'.*\D+\d+\-.*', state_loc)
            if url != []:
                unique.append(url[0])
        for i in state:
            if i not in unique:
                page = requests.get(i)
                if page.status_code == 200:
                    bs = BeautifulSoup(page.text, "html.parser")
                    cont = bs.find("div", class_="Directory-content")
                    cnt = cont.findAll("a", class_="Directory-listLink")

                    for i in cnt:
                        city_loc = (base + i.get('href'))
                        citi.append(city_loc)
                        url = re.findall(r'.*\d.+.\d*.\-.*', city_loc)
                        #                     url = re.findall(r'.*\d+\d*.\-.*', city_loc)
                        if url != []:
                            unique.append(url[0])

        for i in citi:
            if i not in unique:
                page = requests.get(i)
                bs = BeautifulSoup(page.text, "html.parser")
                cont = bs.findAll("a", class_="Teaser-titleLink")

                for i in cont:
                    city_links = (base + i.get('href'))
                    unique.append(city_links)

        for j in unique:
            try:
                page = requests.get(j, timeout=6)
            except Exception as e:
                continue
            if page.status_code == 200:
                soup1 = BeautifulSoup(page.text, "html.parser")
#                 page.close()
                try:
                    add = soup1.find("div", class_="c-AddressRow")
                    addr = add.text
                    add1 = soup1.find("span", class_="c-address-street-2")
                    addr1 = add1.text
                    street = addr + addr1
                    print(street)

                except Exception as e:
                    street = "<MISSING>"

                try:
                    city = soup1.find("span", class_="c-address-city").text

                except Exception as e:
                    city = "<MISSING>"

                try:
                    state = soup1.find("abbr").text

                except Exception as e:
                    state = "<MISSING>"

                try:
                    zp = soup1.find("span", class_="c-address-postal-code").text
                    if len(zp) < 3:
                        zp = "<MISSING>"

                except Exception as e:
                    zp = "<MISSING>"

                try:
                    ph = soup1.find("a", class_="Phone-link").text.strip()
                    if len(ph) < 3:
                        ph = "<MISSING>"

                except Exception as e:
                    ph = "<MISSING>"

                h = []
                try:
                    m = soup1.findAll("td", class_='c-hours-details-row-day')
                    n = soup1.findAll("td", class_="c-hours-details-row-intervals")

                    for i in m:
                        l = i.text

                    for i in n:
                        b = i.text.strip()

                        hoo = l + ' ' + b + ' '
                        h.append(hoo)

                    hour = ' '.join(h)

                    if len(hour) < 3:
                        hour = "<MISSING>"

                except Exception as e:
                    hour = "<MISSING>"

                try:
                    lat = soup1.find("meta", itemprop="latitude").get("content")
                    if len(lat) < 2:
                        lat = "<MISSING>"

                except Exception as e:
                    lat = "<MISSING>"

                try:
                    long = soup1.find("meta", itemprop="longitude").get("content")
                    if len(long) < 2:
                        long = "<MISSING>"

                except Exception as e:
                    long = "<MISSING>"

                page_url = j
                locator_domain = "www.shopjustice.com"
                try:
                    country_code = soup1.find("abbr", itemprop="addressCountry").text

                except Exception as e:
                    country_code = "<MISSING>"

                store_numbr = "<MISSING>"
                ltype = "<MISSING>"
                try:
                    location_name = soup1.find("div", class_="Hero-title--geomod Heading--lead").text

                except Exception as e:
                    location_name = "<MISSING>"

                new_list = [locator_domain, page_url, location_name, street, city, state, zp, country_code,
                            store_numbr, ph, ltype, lat, long, hour]
                data_list.append(new_list)
        return data_list

    except Exception as e:
        print(str(e))

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
