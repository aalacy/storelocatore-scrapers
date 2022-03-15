import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

DOMAIN = "medivet.co.uk"
BASE_URL = "https://www.medivet.co.uk"
LOCATION_URL = "https://www.medivet.co.uk/sitemap.xml"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
    "sec-fetch-site": "same-origin",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def parse_json(soup):
    info = soup.find("script", type="application/ld+json")
    if not info:
        return False
    data = json.loads(info.string)
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    excluded = [
        "https://www.medivet.co.uk/vet-practices/area/Espom/",
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park",
        "https://www.medivet.co.uk/vet-practices/hornsey/cattery/",
        "https://www.medivet.co.uk/vet-practices/south-harrow/thank-you---south-harrow/",
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park-pet-boutique/",
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park-grooming-service/",
    ]
    for val in soup.find_all(
        "loc", text=re.compile(r"\/vet-practices\/\D+|\/24-hour-emergency-vet\/.+")
    ):
        if val.text not in excluded:
            store_urls.append(val.text)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    for page_url in store_urls:
        if "ashby2" in page_url:
            continue
        soup = pull_content(page_url)
        info = parse_json(soup)
        if not info:
            continue
        location_name = info["name"].strip()
        if "Permanently closed" in location_name:
            continue
        address = info["address"][0]
        street_address = address["streetAddress"].replace(" ,", ", ").strip()
        if "https://www.medivet.co.uk/vet-practices/basildon/" in page_url:
            city = address["addressLocality"].strip()
            zip_postal = address["addressRegion"].strip()
            state = MISSING
        else:
            city = address["addressLocality"].strip()
            zip_postal = (
                MISSING
                if "postalCode" not in address
                else address["postalCode"].strip()
            )
            state = (
                MISSING
                if "addressRegion" not in address
                else address["addressRegion"].strip()
            )
        country_code = address["addressCountry"]
        store_number = MISSING
        phone = info["telephone"]
        is_24hour = soup.find("h2", text="Open 24 hours, 365 days a year")
        if is_24hour or "24-hour-emergency-vet" in page_url:
            hours_of_operation = "Open 24 hours"
        else:
            hoo = soup.select("div.operatingHours div[class='hoursTable'] div.day")
            if hoo:
                hours_of_operation = ""
                for hday in hoo:
                    exclude = hday.find_all("span", {"class": "time opening"})
                    for x in exclude:
                        x.decompose()
                    hours_of_operation += (
                        hday.get_text(strip=True, separator=" ") + ", "
                    )
                hours_of_operation = hours_of_operation.strip().rstrip(",")
            else:
                hours_of_operation = ", ".join(info["openingHours"])
        if "Temporarily closed" in location_name:
            location_type = "TEMP_CLOSED"
        else:
            location_type = MISSING
        geo = soup.find("div", {"class": "googleMap loading"})
        latitude = geo["data-lat"]
        longitude = geo["data-lng"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
