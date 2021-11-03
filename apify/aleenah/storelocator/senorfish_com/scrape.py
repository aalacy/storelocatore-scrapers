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
    # Your scraper here

    res = session.get("http://www.xn--seorfish-e3a.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")
    urls = soup.find_all("div", {"class": "fl-rich-text"})
    for url in urls:
        text = re.sub(r"  +", "  ", url.text.replace(u"\xa0", ""),).split(
            "MAP"
        )[0]

        tim = re.findall(r"(HOURS.*)", text)[0]
        text = text.replace(tim, "")
        tim = tim.replace("HOURS", "").replace(":", "")
        text = text.replace(tim, "")
        phone = re.findall(r"[\d\-]+", text)[-1]

        text = text.replace(phone, "").strip()
        zip = re.findall(r"\d{5}", text)
        if zip == []:
            zip = re.findall(r"(\dOO\d\d)", text)
        zip = zip[-1]
        text = text.replace(zip, "").strip()
        zip = zip.replace("OO", "00")
        text = text.split(" ")
        state = text[-1].replace(".", "")
        del text[-1]
        text = " ".join(text)
        try:

            tagged = usaddress.tag(text.replace("  ", " "))[0]

            loc = text.split(tagged["AddressNumber"])[0]
            text = text.replace(loc, "")
            street = (
                text.strip().split(tagged["StreetNamePostType"])[0]
                + " "
                + tagged["StreetNamePostType"]
            ).replace("  ", " ")
            city = text.replace(street, "").strip()
        except:

            text = text.split("  ")
            city = text[-1]
            del text[-1]
            text = "  ".join(text)
            tagged = usaddress.tag(text)[0]
            loc = text.split(tagged["AddressNumber"])[0]
            text = text.replace(loc, "").strip()
            street = (
                text.split(tagged["StreetNamePostType"])[0]
                + " "
                + tagged["StreetNamePostType"]
            )

        all.append(
            [
                "http://www.xn--seorfish-e3a.com",
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
                tim,  # timing
                "http://www.xn--seorfish-e3a.com/locations/",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
