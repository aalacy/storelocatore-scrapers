from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import ssl
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from lxml import html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("bankofamerica_com__atm")
MISSING = "<MISSING>"
DOMAIN = "https://www.bankofamerica.com/"
headers_authority_simple = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}

EXPECTED_SEARCH_RADIUS_MILES_US = 300


def get_state_name_list():
    s = set()
    state_name_list = []
    with SgRequests() as http:
        rs = http.get(
            "https://locators.bankofamerica.com/", headers=headers_authority_simple
        )
        sel = html.fromstring(rs.text, "lxml")
        state_links = sel.xpath(
            '//a[contains(@class, "ga-link") and contains(@href, "https://locators.bankofamerica.com") and contains(@name, "State_")]'
        )
        for sl in state_links:
            slink = "".join(sl.xpath("./@href"))
            sname_abb = slink.split("/")[-2]
            sname = "".join(sl.xpath("./text()"))
            if slink not in s:
                state_name_list.append((sname, sname_abb))
            s.add(slink)
    return state_name_list


def get_phone(data):
    phone_list = []
    maplist = data["maplist"]
    maplist_ph = maplist.split('"local_phone":"')
    for p in maplist_ph[1:]:
        phone = p.split('"')[0]
        if phone:
            phone_list.append(phone)
        else:
            phone_list.append("<MISSING>")
    return phone_list


def get_atm_hours(data):
    atm_hours_list = []
    maplist = data["maplist"]
    maplist_ph = maplist.split('"local_phone":"')
    for p in maplist_ph[1:]:
        ah = (
            " ".join(p.split('"atm_hours":')[1].split('"atm_services"')[0].split())
            .rstrip(",")
            .replace('"', "")
        )
        if ah:
            atm_hours_list.append(ah)
        else:
            atm_hours_list.append("<MISSING>")
    return atm_hours_list


def fetch_data_using_dzs():
    # If Radius  is greater than 1000 it does not work, meaning the URL does not work
    # We must keep the radius at 1000 or less than 1000 miles
    # 'level' must be equal to 1000 or less than 1000
    start_url = "https://maps.bankofamerica.com/api/getAsyncLocations?template=search&radius=1000&limit=1000&level=search&search="
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=EXPECTED_SEARCH_RADIUS_MILES_US,
        use_state=False,
    )
    s = set()
    for zipcode in search:
        url = f"{start_url}{zipcode}"  # noqa
        logger.info(f"Pulling the data from at: {zipcode}| {url} ")
        try:
            with SgRequests(verify_ssl=False) as http:
                data = http.get(url, headers=headers_authority_simple).json()
                data_markers = data["markers"]

                # Phone Number
                plist = get_phone(data)

                # ATM Hours of Operations
                atm_hours_l = get_atm_hours(data)
                if data_markers:
                    logger.info(f"Number of stores found: {len(data_markers)}")
                    for idx1, markers in enumerate(data_markers):
                        info_raw = markers["info"]
                        info_raw1 = info_raw.replace(
                            '<div class="tlsmap_popup">', ""
                        ).replace("</div>", "")
                        info_json = json.loads(info_raw1)

                        locator_domain = DOMAIN
                        page_url = info_json["url"]
                        if info_json["address_1"]:
                            street_address = info_json["address_1"]
                            if info_json["address_2"]:
                                street_address = (
                                    street_address + ", " + info_json["address_2"]
                                )
                            else:
                                street_address = street_address
                        else:
                            street_address = MISSING
                        location_name = info_json["location_name"]
                        location_name = location_name if location_name else MISSING
                        city = info_json["city"]
                        city = city if city else MISSING
                        state = info_json["region"]
                        state = state if state else MISSING
                        zip_postal = info_json["post_code"]
                        zip_postal = zip_postal if zip_postal else MISSING
                        country_code = "US"
                        store_number = info_json["lid"]
                        store_number = store_number if store_number else MISSING

                        # Phone Number
                        phone = plist[idx1]
                        location_type = "ATM"
                        latitude = info_json["lat"]
                        latitude = latitude if latitude else MISSING
                        longitude = info_json["lng"]
                        longitude = longitude if longitude else MISSING

                        hours_of_operation = atm_hours_l[idx1]
                        if "Limited" in hours_of_operation:
                            hours_of_operation = "<MISSING>"
                        raw_address = "<MISSING>"

                        # Making sure there is no duplicates
                        if store_number in s:
                            continue
                        s.add(store_number)

                        # Make sure it only scrapes the branch/office/ATM which has ATM
                        # services available
                        location_types = []
                        for i in markers["specialties"]:
                            location_types.append(i["group"])
                        if "ATM Services" not in location_types:
                            continue

                        item = SgRecord(
                            locator_domain=locator_domain,
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
                        yield item
        except Exception as e:
            logger.info(f"Please FetchRecordsError =>> {e} <<= at {url}")


def fetch_data_using_state():
    # If Radius  is greater than 1000 it does not work, meaning the URL does not work
    # We must keep the radius at 1000 or less than 1000 miles
    # 'level' must be equal to 1000 or less than 1000
    state_name_list = get_state_name_list()
    start_url = "https://maps.bankofamerica.com/api/getAsyncLocations?template=search&radius=1000&limit=1000&level=search&search="
    s = set()
    for state_name in enumerate(state_name_list[0:]):
        url = f"{start_url}{state_name[1]}"  # noqa
        logger.info(f"Pulling the data from: {state_name[0]} | {url} ")
        try:
            with SgRequests(verify_ssl=False) as http:
                data = http.get(url, headers=headers_authority_simple).json()
                data_markers = data["markers"]

                # Phone Number
                plist = get_phone(data)

                # ATM Hours of Operations
                atm_hours_l = get_atm_hours(data)
                if data_markers:
                    logger.info(f"Number of stores found: {len(data_markers)}")
                    for idx1, markers in enumerate(data_markers):
                        info_raw = markers["info"]
                        info_raw1 = info_raw.replace(
                            '<div class="tlsmap_popup">', ""
                        ).replace("</div>", "")
                        info_json = json.loads(info_raw1)

                        locator_domain = DOMAIN
                        page_url = info_json["url"]
                        if info_json["address_1"]:
                            street_address = info_json["address_1"]
                            if info_json["address_2"]:
                                street_address = (
                                    street_address + ", " + info_json["address_2"]
                                )
                            else:
                                street_address = street_address
                        else:
                            street_address = MISSING
                        location_name = info_json["location_name"]
                        location_name = location_name if location_name else MISSING
                        city = info_json["city"]
                        city = city if city else MISSING
                        state = info_json["region"]
                        state = state if state else MISSING
                        zip_postal = info_json["post_code"]
                        zip_postal = zip_postal if zip_postal else MISSING
                        country_code = "US"
                        store_number = info_json["lid"]
                        store_number = store_number if store_number else MISSING

                        # Phone Number
                        phone = plist[idx1]
                        location_type = "ATM"
                        latitude = info_json["lat"]
                        latitude = latitude if latitude else MISSING
                        longitude = info_json["lng"]
                        longitude = longitude if longitude else MISSING

                        hours_of_operation = atm_hours_l[idx1]
                        if "Limited" in hours_of_operation:
                            hours_of_operation = "<MISSING>"
                        raw_address = "<MISSING>"

                        # Making sure there is no duplicates
                        if store_number in s:
                            continue
                        s.add(store_number)

                        # Make sure it only scrapes the branch/office/ATM which has ATM
                        # services available
                        location_types = []
                        for i in markers["specialties"]:
                            location_types.append(i["group"])
                        if "ATM Services" not in location_types:
                            continue

                        item = SgRecord(
                            locator_domain=locator_domain,
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
                        yield item
        except Exception as e:
            logger.info(f"Please FetchRecordsError =>> {e} <<= at {url}")  # noqa


def scrape1():
    logger.info(" Scraping Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    with SgWriter(deduper) as writer:
        results = fetch_data_using_dzs()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


def scrape2():
    logger.info(" Scraping Started")
    count = 0
    deduper = SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    with SgWriter(deduper) as writer:
        results = fetch_data_using_state()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape1()
    logger.info("Scrape 1 Finished!")
    scrape2()
    logger.info("Scrape 2 Finished!")
