import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import io
import re
import json

session = SgRequests()


def write_output(data):
    with io.open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )

        for row in data:
            writer.writerow(row)


def fetch_data():

    addressess = []
    base_url = "https://www.caesars.com"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.gulfoil.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = bs(session.get(base_url, headers=headers).text, "lxml")
    j_ = json.loads(
        data.find(
            "div", {"class": "hero aem-GridColumn aem-GridColumn--default--12"}
        ).find("cet-hero")["data-model"]
    )
    for it in j_["booker"]["markets"]:
        for pro in it["properties"]:
            location_name = pro["label"]

            url = "https://www.caesars.com/api/v1/properties/" + str(
                pro["value"].upper()
            )

            try:
                adr = session.get(url, headers=headers).json()
                street_address = adr["address"]["street"]
                city = adr["address"]["city"]
                state = adr["address"]["state"]
                zipp = adr["address"]["zip"]
                phone = adr["phone"]
                location_type = adr["brand"]
                page_url = adr["bookHotelURL"]
                latitude = adr["location"]["latitude"]
                longitude = adr["location"]["longitude"]
                ca_zip_list = re.findall(
                    r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", str(zipp)
                )
                country_code = "US"
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"

                store = []
                store.append("https://www.caesars.com/")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append("<MISSING>")
                store.append(page_url)
                if str(store[2] + store[-1]) in addressess:
                    continue
                addressess.append(str(store[2] + store[-1]))
                store = [x.replace("’", "'") if type(x) == str else x for x in store]
                yield store

            except:
                pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
