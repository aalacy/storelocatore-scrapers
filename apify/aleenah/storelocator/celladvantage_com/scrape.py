import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("celladvantage_com")


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

    res = session.get("https://stores.uscellular.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    sa = soup.find("div", {"id": "accordionUnitedStates"}).find_all("a")
    urls = []
    for a in sa:

        a = str(a.get("href"))
        if "cellular-advantage" not in a:
            continue
        else:
            url = "https://stores.uscellular.com" + a
            if url not in urls:
                urls.append(url)
            else:
                continue

            res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            street = soup.find("div", {"class": "streetaddress"}).text
            csz = soup.find("div", {"class": "citystate"}).text.split(",")

            city = csz[0]
            csz = csz[1].strip().split(" ")

            state = csz[0]
            zip = csz[1]
            phone = soup.find("a", {"class": "mobile-click"}).text
            timings = soup.find_all("div", {"class": "timings"})
            days = soup.find_all("div", {"class": "day"})

            tim = ""
            for t in range(len(timings)):
                tim += days[t].text.strip() + ": " + timings[t].text.strip() + " "
            if tim == "":
                tim = "<MISSING>"

            all.append(
                [
                    "http://celladvantage.com/",
                    city,
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
                    url,
                ]
            )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
