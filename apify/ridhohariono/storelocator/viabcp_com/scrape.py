from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "viabcp.com"
LOCATION_URL = "https://www.viabcp.com/canales-presenciales"
API_URL = [
    "https://www.viabcp.com/wcm/connect/resources/userstories/JSON/dataJSON_ubicanos_grupo1.json?subtype=json",
    "https://www.viabcp.com/wcm/connect/resources/userstories/JSON/dataJSON_ubicanos_grupo2.json?subtype=json",
]
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

session = SgRequests(verify_ssl=False)


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


def clean_coords(coord):
    if not coord:
        return MISSING
    coord = (
        re.sub(r"[a-zA-Z]|\s+|-79\.8$", "", coord)
        .rstrip(",")
        .replace(",", "")
        .replace("--", "-")
    )
    coord_split = coord.split("-")
    if len(coord_split) > 2:
        coord = "-" + ".".join(coord_split[1:])
    if "." not in coord:
        coord_list = list(coord)
        if len(coord) > 9:
            coord = "".join(coord_list[:4]) + "." + "".join(coord_list[4:])
        elif len(coord) == 9:
            coord = "".join(coord_list[:3]) + "." + "".join(coord_list[3:])
        else:
            coord = "".join(coord_list[:2]) + "." + "".join(coord_list[2:])
    return coord


def fetch_data():
    log.info("Fetching store_locator data")
    for api in API_URL:
        stores = session.get(api, headers=HEADERS).json()
        log.info(f"Found {len(stores)} locations on => {api}")
        for row in stores:
            if row["Tipo"] == "1":
                location_type = "Agencia"
            elif row["Tipo"] == "2":
                location_type = "Agente"
            else:
                location_type = "Cajero"
            location_name = location_type + " - " + row["Nombre"]
            raw_address = row["Direccion"].strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            if street_address == "S/N":
                street_address = raw_address
            country_code = "PE"
            phone = MISSING
            if not row["HoraAperturaLV"]:
                mon_fri_hours = "Closed"
            else:
                mon_fri_hours = row["HoraAperturaLV"] + "-" + row["HoraCierreLV"]
            if not row["HoraAperturaS"]:
                sat_hours = "Closed"
            else:
                sat_hours = row["HoraAperturaS"] + "-" + row["HoraCierreS"]
            hours_of_operation = (
                "Monday - Friday: " + mon_fri_hours + ", Saturday: " + sat_hours
            ).strip()
            if hours_of_operation == "Monday - Friday: Closed, Saturday: Closed":
                hours_of_operation = MISSING
            store_number = row["Codigo"]
            latitude = clean_coords(row["Latitud"])
            longitude = clean_coords(row["longitud"])
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
