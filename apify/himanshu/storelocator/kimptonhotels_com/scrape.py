import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kimptonhotels_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = (
        "https://www.ihg.com/kimptonhotels/content/us/en/stay/find-a-hotel#location=all"
    )
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for data in soup.findAll("div", {"class", "hotel-tile-info-wrapper"}):
        data_url = "https:" + data.find("a").get("href")
        page_url = data_url
        detail_url = session.get(data_url, headers=headers)
        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        latitude = detail_soup.find("meta", {"property": "place:location:latitude"})[
            "content"
        ]
        longitude = detail_soup.find("meta", {"property": "place:location:longitude"})[
            "content"
        ]
        detail_block = detail_soup.select(".brand-logo .visible-content")
        if detail_block:
            for br in detail_soup.select(".brand-logo .visible-content")[0].find_all(
                "br"
            ):
                br.replace_with(",")

            address = (
                detail_soup.select(".brand-logo .visible-content")[0]
                .get_text()
                .strip()
                .split(",")
            )
            if "United States" in address[-1] or "Canada" in address[-1]:

                location_name = detail_soup.select(".name")[0].get_text().strip()
                phone = detail_soup.select(".phone-number")[0].get_text().strip()[8:]
                if phone == "()":
                    phone = (
                        detail_soup.select(".phone-number")[1]
                        .get_text()
                        .strip()[8:]
                        .split("ions:")[1]
                        .strip()
                    )
                street_address = " ".join(address[:-2]).strip()

                ca_zip_list = re.findall(
                    r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
                    str(" ".join(address[-2].split(" "))),
                )
                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
                    str(" ".join(address[-2].split(" "))),
                )
                if us_zip_list:
                    zip = us_zip_list[0].strip()
                    country_code = "US"
                    city = " ".join(address[-2].split(" ")[:-2]).strip()
                    state = address[-2].split(" ")[-2].strip()

                elif ca_zip_list:
                    zip = ca_zip_list[0].strip()
                    country_code = "CA"
                    city = "".join(address[-2].split(" ")[0]).strip()
                    state = address[-2].split(" ")[1].strip()

            else:

                continue
            store = []
            store.append("https://www.kimptonhotels.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            return_main_object.append(store)
        else:
            pass
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
