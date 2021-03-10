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

    base_link = "https://www.thefreshworks.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}
    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="entry-content").findAll(
        class_="wp-block-columns has-background"
    )

    data = []
    for item in items:
        if "Coming Soon" in item.text:
            continue
        locator_domain = "thefreshworks.com"
        location_name = item.find("h2").text.strip()
        raw_data = (
            str(item.p)
            .strip()
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("<strong>", "")
            .replace("\n", "")
            .split("<br/>")
        )
        street_address = raw_data[0]
        if len(street_address) < 10:
            street_address = "<MISSING>"
        city = raw_data[1][: raw_data[1].find(",")].strip()
        state = raw_data[1][raw_data[1].find(",") + 1 : raw_data[1].rfind(" ")].strip()
        zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()
        if not state:
            state = zip_code
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = item.find("a").get_text(separator=u" ").strip()
            phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", phone)[0]
        except:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
