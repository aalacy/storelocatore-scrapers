from xml.etree import ElementTree as ET
import time
from typing import Iterable

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

DOMAIN = "vans.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_XML_root(text):
    return ET.fromstring(text)


def get_XML_object_variable(Object, varNames, noVal=MISSING, noText=False):
    Object = [Object]
    for varName in varNames.split("."):
        value = []
        for element in Object[0]:
            if varName == element.tag:
                value.append(element)
        if len(value) == 0:
            return noVal
        Object = value

    if noText is True:
        return Object
    if len(Object) == 0 or Object[0].text is None:
        return MISSING
    return Object[0].text


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days1 = ["m", "t", "w", "thu", "f", "sa", "su"]


def get_hoo(response):
    hours_of_operation = []

    for index in range(len(days)):
        value = get_XML_object_variable(response, days1[index])
        if value is None or len(value) == 0 or value == MISSING:
            continue
        hours_of_operation.append(f"{days[index]}: {value}")
    hours_of_operation = ";".join(hours_of_operation)
    if len(hours_of_operation) == 0:
        return MISSING
    return hours_of_operation


def fetch_data(http: SgRequests, search: DynamicZipSearch) -> Iterable[SgRecord]:
    http = SgRequests()
    count = 0
    for zipCode in search:
        count = count + 1
        countryCode = search.current_country()
        zipCode1 = zipCode.replace(" ", "+")
        log.debug(f"{count}. From {zipCode} :{countryCode} searching ...")

        try:
            response = http.get(
                f"https://locations.vans.com/01062013/where-to-get-it/ajax?lang=en-EN&xml_request=%3Crequest%3E%3Cappkey%3ECFCAC866-ADF8-11E3-AC4F-1340B945EC6E%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Corder%3E_distance%3C%2Forder%3E%3Csoftmatch%3E1%3C%2Fsoftmatch%3E%3Climit%3E20000%3C%2Flimit%3E%3Catleast%3E1%3C%2Fatleast%3E%3Csearchradius%3E5000%3C%2Fsearchradius%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E{zipCode1}%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3Cnobf%3E1%3C%2Fnobf%3E%3Cwhere%3E%3Ccollections%3E%3Cilike%3E%3C%2Filike%3E%3C%2Fcollections%3E%3Ctnvn%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ftnvn%3E%3Cjuliank%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fjuliank%3E%3Cretail_outlets%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fretail_outlets%3E%3Cor%3E%3Coff%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foff%3E%3Cout%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fout%3E%3Caut%3E%3Ceq%3E%3C%2Feq%3E%3C%2Faut%3E%3Coffer%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foffer%3E%3Coffer2%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foffer2%3E%3Coffer3%3E%3Ceq%3E%3C%2Feq%3E%3C%2Foffer3%3E%3Cdisplay_url%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fdisplay_url%3E%3Cname%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fname%3E%3Ccl%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcl%3E%3Cac%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fac%3E%3Cotw%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fotw%3E%3Ckd%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fkd%3E%3Cfootwear%3E%3Ceq%3E%3C%2Feq%3E%3C%2Ffootwear%3E%3Capparel%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fapparel%3E%3Csnowboard_boots%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsnowboard_boots%3E%3Cpro_skate%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpro_skate%3E%3Csurf%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsurf%3E%3Cjustinhenry%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fjustinhenry%3E%3Csci_fi%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fsci_fi%3E%3Clottie_skate%3E%3Ceq%3E%3C%2Feq%3E%3C%2Flottie_skate%3E%3Ccurbside_enabled%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcurbside_enabled%3E%3Cbopis_enabled%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fbopis_enabled%3E%3Cstory1%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory1%3E%3Cstory2%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory2%3E%3Cstory3%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory3%3E%3Cstory4%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory4%3E%3Cstory5%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory5%3E%3Cstore6%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstore6%3E%3Cstory7%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory7%3E%3Cstory8%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory8%3E%3Cstory9%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory9%3E%3Cstory10%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fstory10%3E%3C%2For%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E"
            )
            root = get_XML_root(response.text)
            stores = get_XML_object_variable(root, "collection.poi", [], True)

            for store in stores:
                store_number = get_XML_object_variable(store, "clientkey")
                location_name = get_XML_object_variable(store, "name")
                street_address = get_XML_object_variable(store, "address1")
                street_address = (
                    street_address + " " + get_XML_object_variable(store, "address2")
                )
                street_address = street_address.replace(MISSING, "").strip()

                city = get_XML_object_variable(store, "city")
                zip_postal = get_XML_object_variable(store, "postalcode")
                state = (
                    get_XML_object_variable(store, "state")
                    + get_XML_object_variable(store, "province")
                ).replace(MISSING, "")
                state = state.strip()
                if len(state) == 0:
                    state = MISSING
                country_code = get_XML_object_variable(store, "country")
                log.info(f"Country Code: {country_code}")

                phone = get_XML_object_variable(store, "phone")
                latitude = get_XML_object_variable(store, "latitude")
                longitude = get_XML_object_variable(store, "longitude")
                hours_of_operation = get_hoo(store)

                raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                    MISSING, ""
                )
                raw_address = " ".join(raw_address.split())
                raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
                if raw_address[len(raw_address) - 1] == ",":
                    raw_address = raw_address[:-1]
                if state == MISSING:
                    page_url = MISSING
                else:
                    page_url = f"https://stores.vans.com/{state}/{city.lower().replace(' ', '_')}/{store_number}"
                if "missing" in str(page_url):
                    page_url = MISSING

                location_type = get_XML_object_variable(store, "icon")
                if location_type == "default":
                    location_type = "store"

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
                    raw_address=raw_address,
                )

        except Exception as e:
            log.info(f"No info: {e}")
            pass
    return []


def scrape():
    log.info(f"Start Crawling {DOMAIN} ...")
    start = time.time()
    CrawlStateSingleton.get_instance().save(override=True)
    search = DynamicZipSearch(
        country_codes=SearchableCountries.ALL,
        expected_search_radius_miles=300,
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_data(http, search):
                writer.write_row(rec)

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
