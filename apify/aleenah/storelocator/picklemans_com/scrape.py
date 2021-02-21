import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("picklemans_com")
driver = SgSelenium().chrome()


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
    driver.get("https://www.picklemans.com/locations.php")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    urls = soup.find_all("p", {"class": "storemapper-address"})
    logger.info(len(urls))
    for url in urls:
        a = url.find_all("a")
        if a == []:
            continue
        url = "https://www.picklemans.com/" + a[0].get("href")
        logger.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        if "permanently closed" in soup.text.lower():
            continue
        try:
            loc = soup.find("h6", {"itemprop": "name"}).text.replace("\n", " ").strip()
        except:
            loc = soup.find("h1", {"itemprop": "name"}).text.replace("\n", " ").strip()
        street = soup.find("span", {"itemprop": "streetAddress"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        try:
            state = soup.find("span", {"itemprop": "addressRegion"}).text
        except:
            state = soup.find_all("span", {"itemprop": "addressLocality"})[1].text
        zip = soup.find("span", {"itemprop": "postalCode"}).text

        timli = soup.find_all("bd1")
        if timli == []:
            timl = soup.find("h5").text
        else:
            timl = timli[0].text
            if "menu" in timl.lower():
                timl = timli[1].text
            if "temporarily closed" in timl.lower():
                type = re.findall(r"(Temporarily.*)", timl)[0].strip()
                if "Hours:" not in timl:
                    timl = timli[1].text
            else:
                type = "open"

        try:
            tim = (
                re.findall(
                    r"(Temporary Hours:.*)",
                    timl.replace("\n", " ").replace(".", ""),
                    re.DOTALL,
                )[0]
                .strip()
                .replace("\t", "")
                .replace("    ", "")
            )
        except:
            tim = re.findall(
                r"Hours:(.*)", timl.replace("\n", " ").replace(".", ""), re.DOTALL
            )[0].strip()
            if "Hours:" in tim:
                tim = re.findall(r"Hours:(.*)", tim)[0]
        if "CLOSED" == tim.strip():
            continue
        phone = soup.find("span", {"itemprop": "telephone"}).text

        long, lat = re.findall(
            r".*!2d(.*)!3d([\d\.]+)!", soup.find("iframe").get("src")
        )[0]

        all.append(
            [
                "https://www.picklemans.com/",
                loc,
                street,
                city,
                state.replace(",", "").strip(),
                zip,
                "US",
                "<MISSING>",  # store #
                phone,  # phone
                type,  # type
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
