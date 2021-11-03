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

    base_link = "https://perryandsonsmarketandgrille.com/locations-menus"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    link = req.url

    locator_domain = "perryandsonsmarketandgrille.com"
    content = base.find("div", attrs={"class": "col-md-4 col-sm-5"})
    location_name = content.find("h3").text.strip()

    raw_data = (
        str(content.findAll("p")[-3])
        .replace("<p>", "")
        .replace("</p>", "")
        .replace("\n", "")
        .split("<br/>")
    )
    try:
        raw_line = raw_data[1].strip()
    except:
        raw_data = (
            str(content.find(class_="taxonomy-description").p)
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", "")
            .split("<br/>")
        )
        raw_line = raw_data[1].strip()

    street_address = raw_data[0].strip()
    city = raw_line[: raw_line.rfind(",")].strip()
    state = raw_line[raw_line.rfind(",") + 1 : raw_line.rfind(" ")].strip()
    zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", content.text)[0]
    location_type = "<MISSING>"

    raw_gps = content.findAll("p")[-2].a["href"]

    start_point = raw_gps.find("ll=") + 3
    latitude = raw_gps[start_point : raw_gps.find(",", start_point)]
    long_start = raw_gps.find(",", start_point) + 1
    longitude = raw_gps[long_start : raw_gps.find("&", long_start)]
    try:
        int(latitude[4:8])
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"

    hours_of_operation = (
        content.findAll("p")[-1]
        .get_text(separator=u" ")
        .replace("\n", " ")
        .replace("–", "-")
        .replace("\xa0", "")
        .strip()
    )
    hours_of_operation = re.sub(" +", " ", hours_of_operation)

    data.append(
        [
            locator_domain,
            link,
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
