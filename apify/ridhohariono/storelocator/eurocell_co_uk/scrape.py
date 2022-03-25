from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "eurocell.co.uk"
SITE_MAP = "https://www.eurocell.co.uk/sitemap.xml"
API_URL = "https://www.eurocell.co.uk/storeslocatorhandler.ashx"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_data(url):
    soup = pull_content(url)
    latitude = soup.find("input", {"name": "dlat"})["value"]
    longitude = soup.find("input", {"name": "dlng"})["value"]
    HEADERS["Referer"] = url
    store_info = bs(
        session.post(
            API_URL,
            headers=HEADERS,
            data={"latitude": latitude, "longitude": longitude},
        ).content,
        "lxml",
    ).find("marker")
    store_content = bs(
        session.post(
            API_URL,
            headers=HEADERS,
            data={"mode": "address", "bid": store_info["id"]},
        ).content,
        "lxml",
    )
    data = {
        "info": store_info,
        "content": store_content,
        "latitude": latitude,
        "longitude": longitude,
    }
    return data


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITE_MAP)
    urls = soup.find_all("loc", text=re.compile(r"\/branch-finder\/.*"))
    for row in urls:
        page_url = row.text.strip()
        store = get_data(page_url)
        location_name = store["info"]["name"]
        city = store["info"]["city"].replace("-", " ")
        street_address = (
            store["info"]["address"]
            .strip()
            .replace("\n", "")
            .replace(city, "")
            .replace(
                ", Holyrood CloseUnit 6, Chancery Gate Trade Centre, Holyrood Close", ""
            )
            .strip()
        ).rstrip(",")
        state = MISSING
        zip_postal = store["info"]["postcode"]
        phone = store["info"]["tel"]
        country_code = "GB"
        hoo = ""
        for hdays in store["content"].find_all("span", {"class": "time"}):
            hoo += hdays.get_text(strip=True, separator=" ").strip() + ", "
        hours_of_operation = hoo.strip().rstrip(",")
        store_number = store["info"]["id"]
        location_type = MISSING
        latitude = store["latitude"]
        longitude = store["longitude"]
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
