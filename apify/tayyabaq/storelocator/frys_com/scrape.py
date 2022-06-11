import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


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
            if row:
                writer.writerow(row)


def fetch_data():
    data = []

    base_link = "https://www.frys.com/ac/storeinfo/storelocator/?site=csfooter_B"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)

    base = BeautifulSoup(req.text, "lxml")

    location = base.find(id="submenu-stores").find_all(
        "a", {"href": re.compile(r"/ac/storeinfo/.+hours-maps-directions")}
    )
    location_href = [
        "https://www.frys.com" + location[n]["href"] for n in range(0, len(location))
    ]

    for n in range(0, len(location_href)):
        link = location_href[n]
        req = session.get(link, headers=HEADERS)
        base = BeautifulSoup(req.text, "html.parser")
        title = base.find(id="text1").text.strip()
        try:
            address = list(base.find(id="address").stripped_strings)
        except:
            continue
        street = address[0]
        city = address[1].split(",")[0]
        state = address[1].split(",")[1].split()[0]
        pcode = address[1].split(",")[1].split()[1]
        phone = address[2].split("Phone ")[1]
        try:

            lat, longt = (
                base.select_one("a[href*=google]")["href"]
                .split("ll=", 1)[1]
                .split("&", 1)[0]
                .split(",")
            )
        except:
            lat = longt = "<MISSING>"
        data.append(
            [
                "https://www.frys.com",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                "<INACCESSIBLE>",
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
