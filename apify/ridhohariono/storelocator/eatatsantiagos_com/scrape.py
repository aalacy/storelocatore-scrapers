from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "eatatsantiagos.com"
BASE_URL = "https://eatatsantiagos.com"
LOCATION_URL = (
    "https://eatatsantiagos.com/santiagos-mexican-restaurant-locations-colorado"
)
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("section", {"id": "oms_74527532750"})
    store_info = content.find_all(
        "div", {"class": "col-12 col-sm-6 col-md-4 col-xl-3 my-3 count"}
    )
    for row in store_info:
        info = row.find("div", {"class": "bg-white border shadow p-3 h-100"})
        title = info.find("h5").text
        link = row.find("a", {"class": "btn btn-sm btn-primary"})
        address = info.find("p").text
        store_dict = {
            "title": title,
            "link": BASE_URL + link["href"],
            "address": address,
        }
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = fetch_store_urls()
    for row in store_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        location_name = row["title"].strip()
        address = row["address"].split(",")
        if len(address) == 4:
            street_address = ", ".join(address[:2]).strip()
            city = address[2].strip()
            state = re.sub(r"\d+", "", address[3]).strip()
            zip_postal = re.sub(r"\D", "", address[3]).strip()
        elif len(address) < 4:
            street_address = address[0].strip()
            city = address[1].strip()
            state = re.sub(r"\d+", "", address[2]).strip()
            zip_postal = re.sub(r"\D", "", address[2]).strip()
        country_code = "US"
        store_number = MISSING
        phone = soup.find("div", {"class": "phone"}).text.strip()
        location_type = MISSING
        hours_of_operation = (
            soup.find("div", {"class": "hours"})
            .text.replace("Hours:", "")
            .replace(" ", " ")
            .strip()
        )
        if len(hours_of_operation.split(",")) > 2:
            hoo = soup.find_all("div", {"class": "hours"})
            hours_of_operation = (
                "".join(
                    [hoo[x].text.replace("Hours:", "").strip() for x in range(0, 2)]
                )
                .replace(" ", " ")
                .strip()
            )
        elif (
            "Sundays" not in hours_of_operation
            and len(hours_of_operation.split(",")) == 2
        ):
            hours_of_operation = (
                hours_of_operation
                + soup.find_all("div", {"class": "hours"})[1]
                .text.replace(" ", " ")
                .strip()
            )
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
