from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "thechickenriceshop.com"
LOCATION_URL = "https://www.thechickenriceshop.com/find-us"
API_URL = "https://www.thechickenriceshop.com/wp-content/themes/hello-elementor-child/outlets.json"
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


def remove_opt_addr(street_address):
    return re.sub(
        r"Jalan\s?$",
        "",
        street_address.replace(
            ", PTD 120470 Persiaran Pelangi Indah, Taman Pelangi Indah Ulu Tiram, Bahru",
            "",
        )
        .replace("Mitsui Shopping Park LaLaport Bukit Bintang City Centre,", "")
        .replace("Sunway Iskandar Bandar Medini Iskandar", "")
        .replace("Bandar Indahpura Kulaijaya", "")
        .replace("Legenda Heights", "")
        .replace("AEON Mall", "")
        .replace("Genting Highlands, Mukim", "")
        .replace("Putra Square", "")
        .replace("Kemasik Daerah Kemaman", "")
        .replace("Kampung Banggol,", "")
        .replace("Pantai Hospital KL,", "")
        .replace("Aeon Big Shopping Centre Wangsa Maju,", "")
        .replace("Perniagaan Mas Jaya Jalan Salleh", "")
        .replace("Persiaran Komersial KLIA", "")
        .replace("AEON Big Bukit Rimau,", "")
        .replace("Bandar Bukit Tinggi 2", "")
        .replace("Mines Resort City", "")
        .replace("Kota Damansara", "")
        .replace("Daerah Seberang Perai", "")
        .replace("Sogo (KL) Department Store,", "")
        .replace("AEON Alpha Angle Shopping Centre,", "")
        .replace("Ara Damansara, PJU 1A", "")
        .replace("Jalan PJU 7/4 Mutiara Damansara", "")
        .replace("PTD 120470 Persiaran Pelangi Indah", "")
        .replace("Malaysia", "")
        .replace("Cyber12", "")
        .replace("Bukit Rimau", "")
        .replace("Bandar Bukit Tinggi Pandamaran", "")
        .replace("Persiaran Gurney", "")
        .strip()
        .rstrip(","),
    )


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in data:
        location_name = re.sub(r"\d+\.", "", row["name"])
        raw_address = row["address"].strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        if city == MISSING:
            city = row["city"]
        if state == MISSING:
            state = row["state"]
        if zip_postal == MISSING:
            zip_postal = row["postcode"]
        street_address = remove_opt_addr(
            re.sub(
                r",?\s?"
                + city
                + r".*,?|,?"
                + state
                + r",?\s?|,?\s?"
                + str(zip_postal)
                + r",?|Taman.*|Jalan\s?$|Mid Valley City|Jalan\s+\D{3}\s+\d{1,2}\D{1,2}\/\d{1,2}\D{1,2}",
                "",
                row["address"],
            )
            .strip()
            .rstrip(",")
        )
        city = city.replace(".", " ").strip()
        state = state.replace(".", " ").strip()
        phone = row["contact"]
        country_code = "MY"
        hoo = ""
        for day in days:
            hoo += day.title() + ": " + row[day] + ","
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        store_number = row["name"].split(".")[0]
        latitude = row["latitude"] if float(row["latitude"]) < 7.0 else row["logitude"]
        longitude = (
            row["logitude"] if float(row["logitude"]) > 98.0 else row["latitude"]
        )
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
