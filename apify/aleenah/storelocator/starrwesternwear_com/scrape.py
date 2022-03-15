import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import usaddress


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


session = SgRequests()
all = []


def fetch_data():

    res = session.get("https://starrwesternwear.com/pages/locations")
    soup = BeautifulSoup(res.text, "html.parser")
    rte = soup.find("div", {"class": "rte"})

    locations = rte.find_all("p", {"class", "p2"})
    for location in locations:

        loc = location.find("b").text.strip()
        if location.find("strong"):
            loc += " " + location.find("strong").text.strip()

        tex = location.text.replace(" ", " ").replace(loc, "").strip()
        phone = location.find("a").text.strip()
        tim = re.findall(r"Open (.*)", tex)[0].strip()
        tex = tex.replace(phone, "").replace(tim, "").replace("Open", "").strip()
        tim = tim.replace("pmSunday", "pm, Sunday")

        tagged = usaddress.tag(tex)[0]

        zip = tagged["ZipCode"]
        state = tagged["StateName"]
        city = tagged["PlaceName"]
        street = tagged["AddressNumber"] + " "
        try:
            street += tagged["StreetNamePreDirectional"] + " "
        except:
            pass
        street += tagged["StreetName"] + " " + tagged["StreetNamePostType"]

        all.append(
            [
                "https://starrwesternwear.com",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                tim.strip(),  # timing
                "https://starrwesternwear.com/pages/locations",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
