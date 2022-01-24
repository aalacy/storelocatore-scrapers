from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "healthworksfitness.com"
BASE_URL = "https://healthworksfitness.com"
LOCATION_URL = "https://healthworksfitness.com/our-locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    page_urls = (
        soup.find(
            "div",
            {
                "class": "wpb_row vc_row-fluid vc_row full-width-section standard_section"
            },
        )
        .find("ul")
        .find_all("li")
    )
    for row in page_urls:
        page_url = row.find("a")["href"]
        content = pull_content(page_url)
        if "healthworksfitness" not in page_url:
            info = row.text.replace("\n", ",").split("–")
            location_name = info[0].strip()
            raw_address = info[1].strip()
            if "gymit" in page_url:
                location_type = "gymit"
                phone = content.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
                hours_of_operation = (
                    content.find("strong", text="HOURS")
                    .find_next("p")
                    .get_text(strip=True, separator=",")
                )
                coord = content.find("iframe", {"src": re.compile(r"\/maps\/.*")})[
                    "src"
                ]
                latitude, longitude = get_latlong(coord)
            elif "republicbos" in page_url:
                location_type = "republicbos"
                coord = content.find("div", {"class": "map-marker"})
                latitude = coord["data-lat"]
                longitude = coord["data-lng"]
                phone = coord["data-mapinfo"].split("-")[1].strip()
                hours_of_operation = MISSING
            else:
                phone = content.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
                location_type = "healthworksfitness"
                hoo = content.select(
                    "div.col.sqs-col-4.span-4 h2[style='white-space:pre-wrap;']"
                )
                hours_of_operation = ""
                for hday in hoo:
                    hours_of_operation += hday.text.strip() + ","
                hours_of_operation = (
                    hours_of_operation.replace("day,", "day: ")
                    .replace("day ", "day: ")
                    .rstrip(",")
                )
                latitude = MISSING
                longitude = MISSING
        else:
            location_name = row.text.strip()
            info = content.find("strong", text="Location & Hours").find_next("div")
            if len(info.text) < 1:
                info = info.find_next("div").find_next("div")
            info = re.sub(
                r"@Healthworks Outdoors:.*",
                "",
                info.get_text(strip=True, separator="@"),
            ).split("@Club Hours@")
            raw_address = info[0]
            hours_of_operation = info[1].replace("@", ",")
            phone = content.find(
                "strong", text=re.compile(r"Telephone:.*")
            ).next_sibling
            location_type = "healthworksfitness"
            coord = content.find("div", {"class": "map-marker"})
            latitude = coord["data-lat"]
            longitude = coord["data-lng"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "us"
        store_number = MISSING
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
            raw_address=raw_address,
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
