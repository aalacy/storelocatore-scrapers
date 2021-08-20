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

    res = session.get("https://www.burkeoilandpropane.com/stores")
    soup = BeautifulSoup(res.text, "html.parser")
    divs = soup.find_all("div", {"class": "_3Mgpu"})
    del divs[0]

    for div in divs:

        data = div.text.replace("\xa0", " ").strip().split("\n")
        if "office" in data[0].lower():
            continue

        loc, phone = re.findall(r"(.*)Tel: (.*)", data[0])[0]
        id = re.findall(r"#([\d]+)", loc)[0]
        street = data[1]
        csz = data[2].strip().split(",")
        city = csz[0]
        csz = csz[1].strip().split(" ")
        try:
            zip = csz[1]
        except:
            zip = "<MISSING>"
        state = csz[0]
        type = data[3]
        type = (
            type.replace("(", "")
            .replace(")", "")
            .replace("$", "Burke oil payment center")
            .replace("K", "Kerosene")
            .replace("G", "Gasoline with no ethanol")
            .replace("E", "Gasoline containing ethanol")
            .replace("D", "Highway diesel")
        )

        all.append(
            [
                "https://www.burkeoilandpropane.com/",
                loc,
                street,
                city,
                state.strip(),
                zip,
                "US",
                id,  # store #
                phone,  # phone
                type,  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                "<MISSING>",  # timing
                "https://www.burkeoilandpropane.com/stores",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
