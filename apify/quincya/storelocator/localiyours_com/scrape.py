import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://www.localiyours.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    content = base.find(class_="pm-map-wrap pm-location-search-list")
    items = content.find_all("section")

    js = base.find(class_="js-react-on-rails-component").contents[0]
    lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(js))
    lngs = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(js))

    if len(lats) > len(items):
        lats.pop(0)
        lngs.pop(0)

    data = []

    for i, item in enumerate(items):
        locator_domain = "localiyours.com"
        location_name = item.h4.text

        raw_data = list(item.a.stripped_strings)

        street_address = " ".join(raw_data[:-1]).split("1st Floor")[0].strip()
        city = raw_data[-1][: raw_data[-1].find(",")].strip()
        state = raw_data[-1][
            raw_data[-1].find(",") + 1 : raw_data[-1].rfind(" ")
        ].strip()
        zip_code = (
            raw_data[-1].replace("</a>", "")[raw_data[-1].rfind(" ") + 1 :].strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.findAll("p")[1].text.strip()
        location_type = "<MISSING>"

        hours_of_operation = (
            item.find("div", attrs={"class": "hours"})
            .text.replace("\xa0", " ")
            .replace("pmF", "pm F")
            .replace("pmS", "pm S")
        )
        hours_of_operation = re.sub(" +", " ", hours_of_operation)
        latitude = lats[i].split(":")[1]
        longitude = lngs[i].split(":")[1]

        data.append(
            [
                locator_domain,
                base_link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
