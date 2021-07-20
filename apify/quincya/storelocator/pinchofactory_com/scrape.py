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

    base_link = "http://www.pincho.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="locations").findAll(
        "div", attrs={"class": "et_pb_text_inner"}
    )[1:]

    data = []
    for item in items:
        locator_domain = "pincho.com"

        try:
            location_name = item.find("strong").text.strip()
        except:
            location_name = item.find("b").text.strip()
        try:
            raw_data = item.find("p").a
            street_address = item.find("p").a.span.text
            got_street = True
        except:
            got_street = False

        if got_street:
            try:
                raw_data = raw_data.findAll("span")[1].text
            except:
                raw_data = item.findAll("span")[1].text
            city = raw_data[: raw_data.find(",")].strip()
            state = raw_data[raw_data.find(",") + 1 : raw_data.rfind(" ")].strip()
            zip_code = raw_data[raw_data.rfind(" ") + 1 :].strip()
        else:
            raw_data = (
                str(item.find("a")).replace("\n", "").replace("</a>", "").split("<br/>")
            )
            street_address = raw_data[0][raw_data[0].rfind(">") + 1 :].strip()
            raw_data[1] = raw_data[1].strip()
            city = raw_data[1][: raw_data[1].find(",")].strip()
            state = raw_data[1][
                raw_data[1].find(",") + 1 : raw_data[1].rfind(" ")
            ].strip()
            zip_code = raw_data[1][raw_data[1].rfind(" ") + 1 :].strip()

        street_address = street_address.replace("Way,", "Way")
        if "coming soon" in street_address.lower():
            continue
        country_code = "US"
        store_number = "<MISSING>"
        try:
            phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", item.text)[0]
        except:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
