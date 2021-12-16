from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "jopetrol.jo"
LOCATION_URL = "http://www.jopetrol.jo/Pages/viewpage.aspx?pageID=80"
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
            country = data.country
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country is None or len(country) == 0:
                country = MISSING
            return street_address, city, state, zip_postal, country
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_address(lat, lng):
    gmap = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key=AIzaSyCr7eBd94pwm-FAn8E-4L_b_IhEj0_4G3c"
    data = session.get(gmap, headers=HEADERS).json()
    return data["results"][1]["formatted_address"]


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("a.btn.btn-primary.back-color-move.white.js-btn-stationMap")
    for row in contents:
        latitude = row["data-lat"].strip()
        longitude = row["data-lng"].strip()
        if not latitude:
            continue
        location_name = "Jopetrol"
        raw_address = get_address(latitude, longitude)
        street_address, city, state, zip_postal, country = getAddress(raw_address)
        phone = row.parent.parent.select_one(
            "div.text-center div:nth-child(3) span.station-data.fontSizeNewsBreif"
        ).text.strip()
        hours_of_operation = MISSING
        if country == "Jordan":
            country_code = "JO"
        else:
            country_code = country
        store_number = MISSING
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
