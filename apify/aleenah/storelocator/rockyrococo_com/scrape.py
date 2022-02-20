import time
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

session = SgRequests()
website = "rockyrococo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://rockyrococo.com"
MISSING = SgRecord.MISSING


def fetch_data():
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    ]
    with SgChrome() as driver:
        driver.get("https://rockyrococo.com/locations")
        time.sleep(10)
        driver.switch_to.frame(driver.find_element_by_id("bullseye_iframe"))
        for us in states:
            log.info(f"Fetching locations from {us}...")
            driver.find_element_by_id("txtCityStateZip").clear()
            driver.find_element_by_id("txtCityStateZip").send_keys(us)
            driver.find_element_by_id("ContentPlaceHolder1_searchButton").click()
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            loclist = soup.findAll("div", {"class": "itemWrap"})
            for loc in loclist:
                temp = loc.find("a", {"id": "website"})["href"]
                if "rockysmadison" in temp:
                    continue
                if "http" in temp:
                    page_url = temp
                elif "https:" not in temp:
                    page_url = "http:" + temp
                page_url = page_url.replace("/http:/", "http:/")
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h1", {"class": "title"}).text
                address = (
                    soup.find("div", {"class": "htmltext1_wp_outer"}).find("a").text
                )
                address = address.replace(",", " ")
                address = usaddress.parse(address)
                i = 0
                street_address = ""
                city = ""
                state = ""
                zip_postal = ""
                while i < len(address):
                    temp = address[i]
                    if (
                        temp[1].find("Address") != -1
                        or temp[1].find("Street") != -1
                        or temp[1].find("Recipient") != -1
                        or temp[1].find("Occupancy") != -1
                        or temp[1].find("BuildingName") != -1
                        or temp[1].find("USPSBoxType") != -1
                        or temp[1].find("USPSBoxID") != -1
                    ):
                        street_address = street_address + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        zip_postal = zip_postal + " " + temp[0]
                    i += 1
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
                phone = soup.select_one("a[href*=tel]").text
                hours_of_operation = r.text.split("Hours:")[1]
                if "View" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("View")[0]
                elif "Apply" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("Apply")[0]
                elif "Click" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("Click")[0]

                hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
                hours_of_operation = (
                    hours_of_operation.get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace("Menu", "")
                    .replace("Apply Now", "")
                    .replace("Click here for local information!", "")
                )
                country_code = "US"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
