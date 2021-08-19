import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup


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

    res = session.get("https://sweetpeasstore.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")

    ps = soup.find_all("div", {"class": "textwidget"})[2].find_all("p")

    for p in ps:

        addr = p.text.strip().split(", ")
        sz = addr[-1].strip().split(" ")
        zip = sz[-1]
        state = sz[0]
        del addr[-1]
        city = addr[-1]
        del addr[-1]
        street = ", ".join(addr)

        all.append(
            [
                "https://sweetpeasstore.com",
                "<MISSING>",
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                "<MISSING>",  # phone
                "<MISSING>",  # type
                "<MISSING>",  # lat
                "<MISSING>",  # long
                "<MISSING>",  # timing
                "https://sweetpeasstore.com/locations/",
            ]
        )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
