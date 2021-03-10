import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("houlihans_com")


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


driver = SgSelenium().chrome()
session = SgRequests()


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    phones = []
    zips = []
    timing = []
    page_url = []
    urls = []

    driver.get("https://houlihans.com/find-a-location")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    lis = soup.find("div", {"class": "sf_cols"}).find_all("a")
    logger.info(len(lis))

    for li in lis:

        u = li.get("href")

        if "www.houlihans.com" not in u:

            if "//bit.ly" not in u:
                urls.append("https://houlihans.com" + u)
                locs.append(li.text)
        else:

            locs.append(li.text)
            urls.append(u)

    for url in urls:
        logger.info(url)
        if url == "https://houlihans.comeats-and-drinks/richfield":
            url = "https://houlihans.com/eats-and-drinks/richfield"
        try:
            res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")

        except:
            try:
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, "html.parser")
            except:

                continue
        page_url.append(url)
        addr = soup.find("p", {"class": "loc-address"}).text.strip().split("\r\n")
        street.append(addr[0].strip())
        csz = addr[-1].strip().split(",")
        cities.append(csz[0])
        csz = csz[-1].strip().split(" ")
        states.append(csz[0])
        zips.append(csz[-1])

        ph = soup.find("p", {"class": "loc-phone"}).text.strip()
        if ph != "":
            phones.append(ph)
        else:
            phones.append("<MISSING>")

        tim = (
            soup.find("p", {"class": "loc-hours"})
            .text.strip()
            .replace("\r\n", ", ")
            .replace("\n", ", ")
        )
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://houlihans.com")
        row.append(locs[urls.index(page_url[i])])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
