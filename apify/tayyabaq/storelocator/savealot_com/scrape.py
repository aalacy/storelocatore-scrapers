from bs4 import BeautifulSoup
import csv
import re
import requests
import pandas as pd
import json

url = "https://savealot.com/grocery-stores/"
base = 'https://savealot.com'


def write_output(df):
    df.to_csv('data.csv', index=False)


def fetch_data():
    states = []
    hours = []
    zip_codes = []
    phones = []
    street_address = []
    lats = []
    longts = []
    location_names = []
    locator_domains = []
    page_urls = []
    country_codes = []
    store_numbrs = []
    location_types = []

    try:
        pattern = re.compile(r'\s+')

        cities = []
        html = requests.get(url).text
        soup = BeautifulSoup(html)
        content = soup.find("div", class_="content")
        lis = content.findAll('a')
        for tag in lis:
            state_loc = (base + tag.get('href'))
            page = requests.get(state_loc)
            if page.status_code == 200:
                bs = BeautifulSoup(page.text, "html.parser")
                ent = bs.find("div", class_="content")
                lis = ent.find('ul')
                lis = lis.findAll('a')
                for tag in lis:
                    city_loc = (base + tag.get('href'))
                    try:
                        page = requests.get(city_loc)
                    except:
                        continue
                    if page.status_code == 200:
                        bso = BeautifulSoup(page.text, "html.parser")
                        ent = bso.find("div", class_="content")

                        lis = ent.find('ul')
                        lis = lis.findAll('a')

                        for tag in lis:
                            loc = (tag.get('href'))
                            try:
                                response = requests.get(loc, timeout=5)
                            except Exception as e:
                                continue
                            if response.status_code == 200:
                                page_urls.append(loc)
                                res = response
                                response.close()
                                try:
                                    strn = loc.split('-')[-1]
                                    strnum = re.findall(r"\d{3,}", strn)
                                    store_num = strnum[0]
                                    if len(store_num) < 3:
                                        store_num = '<MISSING>'
                                except Exception as e:
                                    store_num = "<MISSING>"

                                print(store_num)
                                store_numbrs.append(store_num)

                                try:
                                    city = city_loc.split('/')[-2]
                                except Exception as e:
                                    city = "<MISSING>"
                                print(city)
                                cities.append(city)

                                data = res.text
                                soup = BeautifulSoup(data, 'html.parser')

                                try:
                                    for wrapper in soup.find('div', {"class": "address"}).findAll('p'):
                                        add = wrapper.text
                                        address = re.sub(pattern, " ", add)

                                except Exception as e:
                                    address = "<MISSING>"

                                try:
                                    for wrapper in soup.find('div', {"class": "address"}).findAll('p'):
                                        street = wrapper.contents[0].strip()

                                except Exception as e:
                                    street = "<MISSING>"

                                #                                 print(street)
                                street_address.append(street)

                                try:
                                    st = address.split(',')[1]
                                    state = st.split()[0]

                                except Exception as e:
                                    state = "<MISSING>"
                                print(state)
                                states.append(state)

                                try:
                                    zp = address.split()[-1]
                                    zp_code = re.findall(r"\d{5}", zp)
                                    zip_code = zp_code[0]

                                except Exception as e:
                                    zip_code = "<MISSING>"
                                #                                 print(zip_code)
                                zip_codes.append(zip_code)

                                try:
                                    phn = soup.find('div', attrs={'class': 'phone'}).text.strip()
                                    phone = re.sub(pattern, " ", phn)

                                except Exception as e:
                                    phone = "<MISSING>"
                                    #                                 print(phone)
                                phones.append(phone)

                                try:
                                    result = soup.findAll('div', class_='day-row')

                                    hour = ''
                                    for i in result:
                                        m = i.findAll("p", attrs={'class': 'hours'})
                                        n = i.find('p').text.strip()
                                        for j in m:
                                            mm = j.text.strip()
                                            pat = re.sub(pattern, "", mm)
                                        hoo = n + ' ' + pat + ' '
                                        hour = hour + hoo + '|' + ' '

                                    if len(hour) < 3:
                                        hour = "<MISSING>"

                                except Exception as e:
                                    hour = "<MISSING>"

                                print(hour)
                                hours.append(hour)

                                try:
                                    s = soup.find('script', {'type': 'application/ld+json'})
                                    j_file = json.loads(s.text)
                                    lat = j_file["geo"]['latitude']

                                except Exception as e:
                                    lat = "<MISSING>"
                                lats.append(lat)

                                try:
                                    s = soup.find('script', {'type': 'application/ld+json'})
                                    j_file = json.loads(s.text)
                                    longt = j_file["geo"]['longitude']

                                except Exception as e:
                                    longt = "<MISSING>"
                                longts.append(longt)

                                try:
                                    locn = soup.find('div', attrs={'class': 'ib-text'})
                                    location_name = locn.h1.text

                                except Exception as e:
                                    location_name = "<MISSING>"
                                location_names.append(location_name)

                                country_code = "US"
                                country_codes.append(country_code)
                                #         # print(ccode)

                                location_type = "<MISSING>"
                                location_types.append(location_type)
                                #         # print(location_type)

                                # store_numbr = "<MISSING>"
                                # store_numbrs.append(store_numbr)
                                # #         # print(store_number)

                                locator_domain = "https://www.savealot.com"
                                locator_domains.append(locator_domain)

        dic = {'locator_domain': locator_domains, 'page_url': page_urls, 'location_name': location_names,
               'street_address': street_address, 'city': cities, 'state': states,
               'zip': zip_codes, 'country_code': country_codes, 'phone': phones, 'location_type': location_types,
               'latitude': lats, 'longitude': longts, 'hours_of_operation': hours, 'store_number': store_numbrs}
        d = pd.DataFrame(dic)
        df = d.drop_duplicates()
        return df

    except Exception as e:
        print(str(e))


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
