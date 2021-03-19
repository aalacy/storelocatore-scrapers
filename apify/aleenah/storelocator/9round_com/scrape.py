import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("9round_com")


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
    ids = []
    page_url = []
    countries = []
    res = session.get("https://www.9round.com/kickboxing-classes/directory")
    soup = BeautifulSoup(res.text, "html.parser")
    divs = soup.find_all("div", {"class": "col-md-12"})

    sa = divs[0].find_all("a")
    del sa[0]
    s = divs[1].find_all("a")
    del s[0]
    sa += s

    for a in sa:
        url = "https://www.9round.com/" + a.get("href")
        try:
            res = session.get(url)
        except:
            res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        l = soup.find_all("div", {"class": "d-block city-list"})
        if l == []:
            continue

        l = l[0]
        lis = l.find_all("li")
        for li in lis:
            ca = li.find_all("a")
            del ca[0]
            for aa in ca:
                page_url.append(aa.get("href"))

    for url in page_url:
        logger.info(url)
        try:
            res = session.get(url)
        except:
            res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        data = str(soup.find("script", {"type": "application/ld+json"}))

        street.append(
            re.findall(r'"streetAddress": "([^"]*)"', data)[0]
            .strip()
            .replace("\u202a", "")
        )
        cities.append(
            re.findall(r'"addressLocality": "([^"]*)"', data)[0]
            .strip()
            .replace("\u202a", "")
        )
        states.append(
            re.findall(r'"addressRegion": "([^"]*)"', data)[0]
            .strip()
            .replace("\u202a", "")
        )
        zips.append(
            re.findall(r'"postalCode": "([^"]*)"', data)[0]
            .strip()
            .replace("\u202a", "")
        )
        tim = (
            re.findall(r'"openingHours": "([^"]*)"', data)[0]
            .strip()
            .replace("\u202a", "")
            .replace("Mo", "Monday")
            .replace("Tu", "Tuesday")
            .replace("We", "Wednesday")
            .replace("Th", "Thursday")
            .replace("Fr", "Friday")
            .replace("Sa", "Saturday")
            .replace("Su", "Sunday")
        )
        if "Sunday" not in tim:
            tim += ", Sunday: CLOSED"
        timing.append(tim)
        if re.findall(r'"addressCountry": "([^"]*)"', data)[0] == "Canada":
            countries.append("CA")
        else:
            countries.append("US")
        locs.append(
            re.findall(r'"name": "([^"]*)"', data)[0].strip().replace("\u202a", "")
        )
        lat.append(
            re.findall(r'"latitude": "([^"]*)"', data)[0].strip().replace("\u202a", "")
        )
        long.append(
            re.findall(r'"longitude": "([^"]*)"', data)[0].strip().replace("\u202a", "")
        )
        m = soup.find_all(
            "div",
            {"class": "d-flex justify-content-center flex-column flex-lg-row mb-3"},
        )
        if m == []:
            ids.append("<MISSING>")
            phones.append("<MISSING>")
            continue
        m = m[0]

        ph = m.find_all("a")
        if ph != []:
            ph = ph[0].text.strip().replace("\u202a", "")
            if "or" in ph:
                ph = ph.split("or")[0].strip()

        if ph == "" or ph == []:
            ph = "<MISSING>"
        phones.append(
            ph.replace("Call", "")
            .replace("- Texting us is preferred!", "")
            .replace("OR Text", "")
        )

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.9round.com")
        row.append(locs[i].replace("&amp;", "&"))
        row.append(street[i].replace("&amp;", "&"))
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
        row = ["<MISSING>" if x == "" else x for x in row]
        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
