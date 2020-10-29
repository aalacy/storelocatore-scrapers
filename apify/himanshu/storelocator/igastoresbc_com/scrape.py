import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('igastoresbc_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        # 'Content-Type': 'application/json; charset=utf-8'
        'Content-Type': 'text/html; charset=utf-8',
        'Accept': '*/*'

    }

    # it will used in store data.
    locator_domain = "https://www.igastoresbc.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "igastoresbc"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    r = session.get(
        "https://www.igastoresbc.com/find-a-store/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    # logger.info(soup.prettify())
    table = soup.find('table', {'id': 'stores-data'})
    # logger.info(table.prettify())
    tbody = table.find('tbody')
    for rows in tbody.findChildren('tr'):
        # logger.info(rows)
        list_rows = list(rows.stripped_strings)
        # logger.info(list_rows)
        # logger.info(len(list_rows))
        # logger.info("~~~~~~~~~~~~")

        location_name = "".join(list_rows[1].strip())
        zipp = "".join(list_rows[3].strip())
        state = "".join(list_rows[4].strip())
        city = "".join(list_rows[5].strip())
        latitude = "".join(list_rows[6].strip())
        longitude = "".join(list_rows[7].strip())
        last_td = rows.find_all('td')[-2]
        list_td = list(last_td.stripped_strings)
        # logger.info(list_td )
        list2 = [x.replace('\n', '').replace(
            '\t', '').replace('<br />', ' ') for x in list_td]
        p1 = "".join(list2).split(
            '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')
        # logger.info(p1)
        # logger.info(len(p1))
        # logger.info("~~~~~~~~~~~~~~~`")
        if len(p1) == 4:
            phone = "".join(list2).split(
                '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[2].split('<td>')[-1].split('</td>')[0].replace('Phone:', "").strip()
              
        else:
            if "&nbsp;</td></tr></tbody></table></td></tr><tr>" == "".join(list2).split('<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[4].strip():
                phone = "".join(list2).split(
                    '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[6].split('</td>')[0].strip().replace('Bakery / Deli 250-493-7713 Customer Service ','')
                # logger.info(phone1)
               
            else:
                phone = "".join(list2).split(
                    '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[4].split('</td>')[0].strip()
            # logger.info(phone1)
        hours = "".join(list2).split(
            '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')
        # logger.info(hours)
        # logger.info(len(hours))
        # logger.info("~~~~~~~~~~")
        if len(hours) == 4:
            hours_of_operation = "".join(list2).split(
                '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[3].split('<td>')[1].split('</td>')[0].replace('<p>', "").replace('</p>', "").replace("Hours:", '').strip()
        else:
            if "Bakery / Deli 250-493-7713 Customer Service 250-493-1737</td></tr><tr>" == "".join(list2).split(
                    '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[6]:
                hours_of_operation = "".join(list2).split(
                    '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[8].split('</td>')[0].strip()

            else:
                hours_of_operation = "".join(list2).split(
                    '<td style="line-height: 1.5em; padding: 3px 0px; vertical-align: top;">')[6].split('</td>')[0].strip()
                # logger.info(hours_of_operation)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
        store = ["<MISSING>" if x == "" else x for x in store]
        return_main_object.append(store)
        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
