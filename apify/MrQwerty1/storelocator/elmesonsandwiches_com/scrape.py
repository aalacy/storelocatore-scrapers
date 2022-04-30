from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import json
from urllib.parse import unquote

from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "elmesonsandwiches.com"
map_url = "https://www.google.com/maps/dir//{},{}/@{},{}z"
website = "https://www.elmesonsandwiches.com"
MISSING = SgRecord.MISSING
page_url = f"{website}/restaurantes"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def request_with_retries(url):
    return session.get(url, headers=headers)


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def address_cleanup(adr):
    cleaned_address = (
        adr.replace("Avenida Jose V. Caro frente Terminal American Airlines", "")
        .replace("Applebee's Grill + Bar,", "")
        .replace("La Parrilla Argentina,", "")
        .replace("Galería 100 Shopping Center,", "")
        .replace("Pearle Vision,", "")
        .replace("Plaza Centro Mall (Caguas),", "")
        .replace("Made Electronics,", "")
        .replace("Chili's Grill & Bar,", "")
        .replace("Quebrada Maga,", "")
        .replace("Caimito,", "")
        .replace("La Patisserie De France,", "")
        .replace("Di Morini", "")
        .replace("El Meson Sandwiches (San Germán),", "")
        .replace("Edificio González Padín,", "")
    )
    return cleaned_address


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            raw_address = address_cleanup(raw_address)
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
            if city == "Nte":
                city = "Hato Rey Nte"
            if "Ponce" in street_address:
                city = "Ponce"
                street_address = street_address.replace("Ponce", "")
            if "San Germán" in street_address:
                street_address = street_address.replace("San Germán", "")
                city = "San Germán"
            if "Santa Isabel" in street_address:
                street_address = street_address.replace("Santa Isabel", "")
                city = "Santa Isabel"
            if "Plaza Del Caribe" in street_address:
                street_address = "Plaza Del Caribe"
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Missing, {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_stores():
    response = request_with_retries(page_url)
    body = html.fromstring(response.text, "lxml")
    text = unquote("".join(body.xpath("//div/@data-elfsight-google-maps-options")))
    return json.loads(text)["markers"]


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = MISSING
        location_type = MISSING
        description = get_JSON_object_variable(store, "infoDescription")
        location_name = get_JSON_object_variable(store, "infoTitle")
        log.info(f"Location: {location_name}")
        country_code = "US" if "Monday" in description else "PR"
        phone = get_JSON_object_variable(store, "infoPhone").replace("Tel: ", "")
        if phone == "":
            phone = get_phone(description)
        latitude, longitude = get_JSON_object_variable(store, "coordinates").split(", ")
        lines = (
            description.replace("<br>", "")
            .replace("<div>", "\n")
            .replace("</div>", "")
            .replace("&nbsp;", " ")
            .replace("<strong>", "")
            .replace("</strong>", " ")
            .replace("<b>", "")
            .replace("</b>", " ")
            .split("\n")
        )
        hoo = []
        for line in lines:
            if ":00" in line or ":15" in line or ":30" in line or ":45" in line:
                hoo.append(line)
        hoo_joined = " ".join((" ".join(hoo)).split())
        # leave only the main hours, remove Autoservicio hours
        separator = "Autoservicio"
        hours_of_operation = hoo_joined.split(separator, 1)[0]

        if country_code == "US":
            raw_address = get_JSON_object_variable(store, "position")
            street_address, city, state, zip_postal = get_address(raw_address)
        else:
            with SgChrome(is_headless=True, user_agent=user_agent) as driver:

                driver.get(map_url.format(latitude, longitude, latitude, longitude))
                time.sleep(40)
                htmlSource = driver.page_source
                sp1 = bs(htmlSource, "html.parser")
                addr = (
                    sp1.select("input.tactile-searchbox-input")[-1]["aria-label"]
                    .replace("Destination", "")
                    .strip()
                )
                street_address, city, state, zip_postal = get_address(addr)
                zip_postal = zip_postal.replace("HUMACAO", "")
                country_code = "US"
                state = "PR"
        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
