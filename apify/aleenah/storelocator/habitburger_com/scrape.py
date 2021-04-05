import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("habitburger_com")


session = SgRequests()


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
    res = session.get("https://www.habitburger.com/locations/all/")
    soup = BeautifulSoup(res.text, "html.parser")
    uls = soup.find("ul", {"class": "reglist"})

    all = []
    urls = set([])
    for ul in uls:
        data = ul.text.lower()
        if "china" not in data or "combodia" not in data:
            sa = ul.find_all("a")
            for a in sa:
                url = a.get("href")
                if "/locations/" in url:
                    urls.add(a.get("href"))

    for url in urls:
        url = "https://www.habitburger.com" + url
        logger.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        uls = soup.find_all(id="coming_soon")
        if uls != []:
            continue

        the_script = soup.find_all("script", {"type": "application/ld+json"})[1]
        the_script = str(the_script)

        loc = re.findall(r'.*"name": "([^"]*)"', the_script, re.DOTALL)[0]

        city = re.findall(r'.*"addressLocality": "([^"]*)"', the_script, re.DOTALL)[0]

        state = re.findall(r'.*"addressRegion": "([^"]*)"', the_script, re.DOTALL)[0]

        zip = re.findall(r'.*"postalCode": "([^"]*)"', the_script, re.DOTALL)[0]

        street = (
            re.findall(r'.*"streetAddress": "([^"]*)"', the_script, re.DOTALL)[0]
            .replace(zip, "")
            .replace(state, "")
            .replace(city, "")
            .strip()
        )

        try:
            tim = re.findall(
                r'.*"openingHours": \[.*"([^"]*)".*\],', the_script, re.DOTALL
            )[0]
            if "<br>" in tim:
                tim = tim.replace("<br>", " ")
            if "> " in tim:
                tim = tim.replace("> ", "")
            if tim.strip() == ">":
                tim = "<MISSING>"

            remove = re.findall(
                r"(https://habitburger.fbmta.com/shared/images/275/275_[\d]*.jpg)", tim
            )
            if remove != []:
                remove = remove[0]
                tim = tim.replace(remove, "")

        except:
            tim = "<MISSING>"

        if tim.strip() == "":

            tim = re.findall("(Hours:.*pm|Hours:.*am)", str(soup), re.DOTALL)

            if tim == []:
                tim = "<MISSING>"
            else:
                tim = (
                    tim[0]
                    .replace("<br/>", " ")
                    .replace("</h2>", " ")
                    .replace("&amp; ", " ")
                    .replace('<h2 class="hdr">', "")
                    .replace("\n", " ")
                    .replace("Hours:", "")
                    .strip()
                )
        if "temporarily closed" in tim.lower():
            tim = "Temporarily Closed"
        if tim.strip() == "":
            tim = "<MISSING>"
        try:
            phone = re.findall(r'.*"telephone": "([^"]*)"', the_script, re.DOTALL)[0]

        except:
            phone = "<MISSING>"

        lat = re.findall(r"lat: (-?[\d\.]*),", str(soup), re.DOTALL)[0]
        long = re.findall(r"lng: (-?[\d\.]*)", str(soup), re.DOTALL)[0]

        all.append(
            [
                "https://www.habitburger.com/locations/all/",
                loc,
                street,
                city,
                state,
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                tim,  # timing
                url,
            ]
        )
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
