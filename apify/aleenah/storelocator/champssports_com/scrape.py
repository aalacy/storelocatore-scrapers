import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("champssports_com")


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


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    page_url = []
    countries = []

    res = session.get("https://stores.champssports.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    uls = soup.find("div", {"class": "Directory-content"}).find_all("ul")
    usa = uls[0].find_all("a") + uls[2].find_all("a") + uls[3].find_all("a")
    can = uls[1].find_all("a")

    for a in usa:

        if a.get("data-count") == "(1)":

            page_url.append(
                "https://stores.champssports.com/" + a.get("href").replace("../", "")
            )
            countries.append("US")
        else:

            url = "https://stores.champssports.com/" + a.get("href").replace("../", "")

            res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            sa = soup.find("div", {"class": "Directory-content"}).find_all("a")

            for d in sa:
                if d.get("data-count") == "(1)":
                    if (
                        "https://stores.champssports.com/"
                        + d.get("href").replace("../", "")
                        not in page_url
                    ):
                        page_url.append(
                            "https://stores.champssports.com/"
                            + d.get("href").replace("../", "")
                        )
                        countries.append("US")
                else:
                    url = "https://stores.champssports.com/" + d.get("href").replace(
                        "../", ""
                    )

                    res = session.get(url)
                    soup = BeautifulSoup(res.text, "html.parser")
                    sas = soup.find_all("a", {"class": "Teaser-titleLink"})
                    for s in sas:
                        if (
                            "https://stores.champssports.com/"
                            + s.get("href").replace("../", "")
                            not in page_url
                        ):
                            page_url.append(
                                "https://stores.champssports.com/"
                                + s.get("href").replace("../", "")
                            )
                            countries.append("US")

    for a in can:
        if a.get("data-count") == "(1)":
            page_url.append(
                "https://stores.champssports.com/" + a.get("href").replace("../", "")
            )
            countries.append("CA")

        else:

            url = "https://stores.champssports.com/" + a.get("href")

            res = session.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            sa = soup.find("div", {"class": "Directory-content"}).find_all("a")

            for d in sa:
                if d.get("data-count") == "(1)":
                    page_url.append(
                        "https://stores.champssports.com/"
                        + d.get("href").replace("../", "")
                    )
                    countries.append("CA")
                else:
                    url = "https://stores.champssports.com/" + d.get("href").replace(
                        "../", ""
                    )

                    res = session.get(url)
                    soup = BeautifulSoup(res.text, "html.parser")
                    sas = soup.find_all("a", {"class": "Teaser-titleLink"})
                    for s in sas:
                        if (
                            "https://stores.champssports.com/"
                            + s.get("href").replace("../", "")
                            not in page_url
                        ):
                            page_url.append(
                                "https://stores.champssports.com/"
                                + s.get("href").replace("../", "")
                            )
                            countries.append("CA")

    logger.info(len(page_url))

    key_set = set([])
    for url in page_url:
        logger.info(url)

        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find("div", {"class": "Core-row l-row"})

        c = div.find("span", {"class": "c-address-city"}).text
        s = div.find_all("abbr", {"class": "c-address-state"})
        if s != []:
            s = s[0].text
        else:
            s = "<MISSING>"
        st = div.find("span", {"class": "c-address-street-1"}).text
        z = div.find("span", {"class": "c-address-postal-code"}).text
        if s + c + z + st in key_set:
            logger.info("This is a duplicate, but its data is added to the file")

        key_set.add(s + c + z + st)
        locs.append(soup.find("span", {"class": "LocationName-geo"}).text)
        street.append(st)
        cities.append(c)
        states.append(s)
        zips.append(z)
        try:
            phone = div.find("div", {"id": "phone-main"}).text
        except:
            phone = "<MISSING>"
        phones.append(phone)
        tim = ""
        tims = div.find("tbody").find_all("tr")
        for t in tims:
            tim += t.get("content") + ", "
        timing.append(
            tim.strip()
            .strip(",")
            .replace("Mo", "Monday")
            .replace("Tu", "Tuesday")
            .replace("We", "Wednesday")
            .replace("Th", "Thursday")
            .replace("Fr", "Friday")
            .replace("Sa", "Saturday")
            .replace("Su", "Sunday")
        )

        latlng = soup.find_all("meta")[17].get("content")
        lat.append(re.findall(r"(-?[\d\.]+);", latlng)[0])
        long.append(re.findall(r";(-?[\d\.]+)", latlng)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        # if street[i]=="<MISSING>":
        #  continue
        row.append("https://stores.champssports.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
