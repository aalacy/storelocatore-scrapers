import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
import lxml.html

logger = SgLogSetup().get_logger("daysinn_ca")

session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }

    base_url = "http://daysinn.ca"
    r = session.get(
        "https://www.wyndhamhotels.com/en-ca/days-inn/locations", headers=headers
    )
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("ul", {"class": "property-list"}):
        for semi_parts in parts.find_all("li", {"class": "property"}):
            return_object = []
            try:
                store_request = session.get(
                    "https://www.wyndhamhotels.com" + semi_parts.find("a")["href"]
                )
            except:
                continue

            store_soup = BeautifulSoup(store_request.text, "lxml")
            page_url = "https://www.wyndhamhotels.com" + semi_parts.find("a")["href"]
            logger.info(page_url)
            store_sel = lxml.html.fromstring(store_request.text)
            json_text = "".join(
                store_sel.xpath('//script[@type="application/ld+json"]/text()')
            ).strip()

            if len(json_text) > 0:
                coords = json.loads(json_text)

                latitude = coords["geo"]["latitude"]
                longitude = coords["geo"]["longitude"]

            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            if store_soup.find("div", {"class": "property-info"}):
                locationDetails = store_soup.find("div", {"class": "property-info"})
                temp_storeaddresss_raw = list(locationDetails.stripped_strings)
                temp_storeaddresss = []
                for temp in temp_storeaddresss_raw:
                    if len("".join(temp).strip()) > 0 and "".join(temp).strip() != ",":
                        temp_storeaddresss.append("".join(temp).strip())
                if temp_storeaddresss[-2].strip() not in ["US", "CA"]:
                    continue
                location_name = temp_storeaddresss[0]
                street_address = temp_storeaddresss[1]
                if "," in street_address[-1]:
                    street_address = "".join(street_address[:-1]).strip()
                city = temp_storeaddresss[2]
                store_zip = ""
                if len(temp_storeaddresss) == 7:
                    state = temp_storeaddresss[3]
                    store_zip = temp_storeaddresss[4]
                    phone = temp_storeaddresss[-1].replace("+1-", "").strip()
                else:
                    logger.info(temp_storeaddresss)
                    logger.info(len(temp_storeaddresss))
                    logger.info("---------------")

                ca_zip_list = re.findall(
                    r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
                    str(store_zip),
                )
                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(store_zip)
                )
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country = "CA"
                elif us_zip_list:
                    zipp = us_zip_list[-1]
                    country = "US"

                else:
                    if "CA" == temp_storeaddresss[-2].strip():
                        zipp = temp_storeaddresss[-3].strip()
                        country = "CA"
                    else:
                        continue

                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append(street_address)
                return_object.append(city)
                return_object.append(state)
                return_object.append(zipp)
                return_object.append(country)
                return_object.append("<MISSING>")
                return_object.append(phone)
                return_object.append("<MISSING>")
                return_object.append(latitude)
                return_object.append(longitude)
                return_object.append("<MISSING>")
                return_object.append(page_url)
                yield return_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
