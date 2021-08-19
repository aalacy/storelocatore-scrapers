import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
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


def fetch_data():
    # Your scraper here

    all = []
    session = SgRequests()
    res = session.get("http://thaibbqla.com/location.html")
    soup = BeautifulSoup(res.text, "html.parser")
    try:
        locs = soup.find_all("table")[-2].find_all("p")
    except:
        res = session.get("http://thaibbqla.com/location.html")
        soup = BeautifulSoup(res.text, "html.parser")
        locs = soup.find_all("table")[-2].find_all("p")

    tims = (
        locs[-1]
        .text.replace("HOURS OF OPERATION:", "")
        .replace(" ", " ")
        .strip()
        .split("\n")
    )
    tim = ""
    for t in tims:
        tim += t.strip() + " "

    for loc in locs:
        if "THAI" not in loc.text:
            continue
        datas = (
            loc.text.replace("(IN THE HEART OF THAI TOWN)", "")
            .replace(" ", " ")
            .strip()
            .split("THAI")
        )
        for data in datas:
            if data.strip() == "":
                continue
            data = "THAI" + data
            data = data.split("\n")

            name = data[0]
            del data[0]
            addr = data[0].strip()
            del data[0]
            if "TEL" not in data[0]:
                addr += " " + data[0].strip()
                del data[0]

            addr = usaddress.tag(addr)[0]
            street = (
                addr["AddressNumber"]
                + " "
                + addr["StreetName"]
                + " "
                + addr["StreetNamePostType"]
            )
            city = addr["PlaceName"]
            state = addr["StateName"]
            zip = addr["ZipCode"]

            phone = ""
            for d in data:
                if "T1" in d or "TEL" in d:
                    phone = d.replace("T1:", "").replace("TEL:", "")
                    phone = re.findall(r"[\d\-\(\) ]+", phone)[0].strip()
            if phone == "":
                phone = "<MISSING>"

            all.append(
                [
                    "http://thaibbqla.com/",
                    name,
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
                    "http://thaibbqla.com/location.html",
                ]
            )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
