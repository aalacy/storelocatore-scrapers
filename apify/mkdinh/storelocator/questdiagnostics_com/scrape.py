import re
import ssl
import time
import json
from bs4 import BeautifulSoup
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import threading

logger = SgLogSetup().get_logger("questdiagonstics.com")

try:
    _create_unverified_https_context = ssl._create_unverified_context
    logger.info("_create_unverified_context")
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    logger.info("wah wah")


local = threading.local()


def get_session():
    if not hasattr(local, "session"):
        local.session = SgRequests()

    return local.session


def get_urls(driver):
    driver.get("https://www.bluenile.com/jewelry-stores")
    driver.execute_script("open('https://www.bluenile.com/jewelry-stores')")
    time.sleep(30)
    driver.execute_script("open('https://www.bluenile.com/jewelry-stores')")
    driver.refresh()
    time.sleep(30)
    driver.refresh()
    time.sleep(30)
    source = driver.page_source
    tree = html.fromstring(source)
    return tree.xpath("//a[@class='store-name']/@href")


def get_locations(session):
    response = session.get(
        "https://www.questdiagnostics.com/locations/search.html/27612/50000/1"
    )
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find_all("div", class_="tab paginatable-item")


def fetch_location(location):
    locator_domain = "questdiagnostics.com"
    title = location.find("a", class_="site-name")
    location_name = re.sub(
        r"\s*- (All Urine Drug Screens by Appointment Only|Employer Drug Testing Not Offered)",
        "",
        title.text,
        re.IGNORECASE,
    )
    page_url = f'https://www.questdiagnostics.com{title["href"]}'

    soup = BeautifulSoup(get_session().get(page_url).text)
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        data = json.loads(re.sub(r"\n", " ", script.string))

        if data["@type"] == "LocalBusiness":
            phone = data["telephone"]

            address = data["address"]
            street_address = address["streetAddress"]
            city = address["addressLocality"]
            state = address["addressRegion"]
            postal = address["postalCode"]
            country_code = address["addressCountry"]

            latitude = location.find("div", class_="latitude").text
            longitude = location.find("div", class_="longitude").text

            hours = location.find_all("div", class_="day")
            hours_of_operation = ", ".join(
                re.sub(r"\n", "", hour.text.strip()) for hour in hours
            )

            return SgRecord(
                page_url=page_url,
                locator_domain=locator_domain,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def fetch_data():
    with ThreadPoolExecutor() as executor, SgRequests() as session:
        locations = get_locations(session)
        futures = [executor.submit(fetch_location, location) for location in locations]
        for future in as_completed(futures):
            yield future.result()


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)
