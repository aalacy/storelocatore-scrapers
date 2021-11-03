import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgSelenium
import re
import time

logger = SgLogSetup().get_logger("habitburger_com")


session = SgRequests()
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


def fetch_data():
    # Your scraper here
    res = session.get("https://www.marketbroiler.com/locations")
    soup = BeautifulSoup(res.text, "html.parser")

    s = soup.find_all(
        class_="s_usaAWRichTextClickableSkin_richTextContainer s_usaAWRichTextClickableSkinrichTextContainer"
    )

    evens = s[::2]
    odds = s[1::2]
    sas = soup.find_all("a", {"class": "wixAppsLink"})
    sa = []
    for a in sas:
        a = a.get("href")
        if "direction" not in a and "maps.google" not in a:
            sa.append(a)

    all = []
    for even in evens:
        loc = even.find("em").text.strip()
        ps = odds[evens.index(even)].find_all("p")
        url = sa[evens.index(even)]
        type = ps[0].text + " " + ps[1].text
        del ps[0]
        del ps[0]
        street = ps[0].text
        csz = ps[1].text.split(",")
        city = csz[0]
        csz = csz[1].strip().split(" ")
        if csz[0] == "":
            del ps[1]
            csz = ps[1].text.split(",")[1].strip().split(" ")

        state = csz[0]
        del csz[0]

        zip = csz[0]
        phone = ps[2].text.replace("Phone.", "").strip()

        driver.get(url)
        time.sleep(10)
        wix_frames = driver.find_elements_by_tag_name("wix-iframe")
        coord = ""
        for frame in wix_frames:

            driver.switch_to.frame(frame.find_element_by_tag_name("iframe"))
            try:
                coord = driver.find_element_by_tag_name("iframe").get_attribute("src")
                if "/maps/" not in coord:
                    coord = ""
                    driver.switch_to.default_content()
                    continue
                break
            except:
                driver.switch_to.default_content()
                continue

        if coord == "":
            lat = long = "<MISSING>"
        else:
            long, lat = re.findall(r"!2d(-?[\d\.]+)!3d([\d\.]+)", coord)[0]

        tim = re.findall(r"(Monday.*pm)", soup.text, re.DOTALL)
        if tim == []:
            tim = re.findall(r"(Sunday.*pm)", soup.text, re.DOTALL)

        try:
            tim = tim[0].replace("\xa0", "").replace("\n", " ")
        except:
            tim = "<MISSING>"
        all.append(
            [
                "https://www.marketbroiler.com",
                loc,
                street,
                city,
                state,
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
