import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import pgeocode
import re


logger = SgLogSetup().get_logger("hollandandbarrett_com")
DOMAIN = "https://www.hollandandbarrett.com"
URL_LOCATION = "https://www.hollandandbarrett.com/stores/"
MISSING = "<MISSING>"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Accept": "*/*",
    "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
    "Referer": "https://www.hollandandbarrett.com/stores/",
    "Origin": "https://www.hollandandbarrett.com",
    "Connection": "keep-alive",
    "TE": "Trailers",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

session = SgRequests()


def get_country_code(zip_postal):
    pgeo_uk = pgeocode.Nominatim("GB")
    pgeo_ie = pgeocode.Nominatim("IE")
    pgeo_uk_results = pgeo_uk.query_postal_code(zip_postal)
    logger.info(f"pgeo uk results type: {type(pgeo_uk_results)}")
    pgeo_uk_results_nan_replaced = pgeo_uk_results.fillna("")
    logger.info(f"pgeo uk results type: {pgeo_uk_results_nan_replaced}")
    country_code_uk = pgeo_uk_results_nan_replaced.country_code
    logger.info(f"Country Code UK: {country_code_uk}")

    # Netherlands Postal Code Regex Pattern
    pattern_postal_code_nl = r"^(?:NL-)?(?:[1-9]\d{3} ?(?:[A-EGHJ-NPRTVWXZ][A-EGHJ-NPRSTVWXZ]|S[BCEGHJ-NPRTVWXZ]))$"

    # Belgium Postal Code Regex Pattern
    pattern_postal_code_be = r"^(?:(?:[1-9])(?:\d{3}))$"

    country_code = ""

    if country_code_uk:
        country_code = country_code_uk
    else:
        # Ireland
        pgeo_ie_results = pgeo_ie.query_postal_code(zip_postal)
        pgeo_ie_results_nan_replaced = pgeo_ie_results.fillna("")
        country_code_ie = pgeo_ie_results_nan_replaced.country_code
        if country_code_ie:
            country_code = country_code_ie
            logger.info(f"Country Code for Ireland found: {country_code}")
        else:
            ccnl = re.findall(pattern_postal_code_nl, zip_postal)
            if ccnl:
                country_code = "NL"
            else:
                ccbe = re.findall(pattern_postal_code_be, zip_postal)
                if ccbe:
                    country_code = "BE"
                else:
                    country_code = MISSING
    return country_code


def fetch_data():
    start_url = (
        "https://cdn1.assets.hollandandbarrett.com/page-data/stores/page-data.json"
    )
    response = session.get(start_url, headers=headers, timeout=180)
    page_data = json.loads(response.text)
    data_json = page_data["result"]["pageContext"]["storeDetails"]
    for idx, data in enumerate(data_json):
        data_store = data["store"]
        data_store = json.loads(data_store)
        logger.info(f"Data: {data}")
        logger.info(f"Store Data {idx}: {data_store}\n\n")
        locator_domain = DOMAIN
        location_name = data_store["branchName"]
        location_name = location_name if location_name else MISSING
        page_url = f'{DOMAIN}{data["storePath"]}'
        street_address = data_store["addressLine1"]
        street_address = street_address if street_address else MISSING
        city_raw = data_store["town"]
        city_town = data_store["town"]
        city = city_town if city_town else MISSING

        state = data_store["county"]
        if state is not None:
            state = state
        else:
            state = MISSING

        zip_postal = data_store["postcode"]
        zip_postal = (
            zip_postal.replace("3527HE", "3527 HE")
            .replace("DONT KNOW", "")
            .replace("IRELAND", "")
            .replace("BURTON", "")
            .replace("CRICK", "")
        )
        zip_postal = zip_postal if zip_postal else MISSING
        if MISSING not in zip_postal:
            country_code = get_country_code(zip_postal)
        else:
            country_code = MISSING

        if zip_postal == "N9 0AL":
            country_code = "GB"
        if zip_postal == "CV11":
            country_code = "GB"
        if zip_postal == "BT":
            country_code = "IE"
        if zip_postal == "IRE":
            country_code = "IE"

        phone = data_store["phoneNumber"]
        phone = phone if phone else MISSING

        store_number = data["branchNo"]
        store_number = store_number if store_number else MISSING

        location_type = "<MISSING>"
        latitude = data_store["latitude"]
        if str(latitude) == str(0):
            latitude = MISSING
        else:
            latitude = latitude if latitude else MISSING

        longitude = data_store["longitude"]
        if str(longitude) == str(0):
            longitude = MISSING
        else:
            longitude = longitude if longitude else MISSING

        raw_address = f'{data_store["addressLine1"]},{data_store["addressLine2"]}, {city_raw}, {zip_postal}'
        hours_of_operation = ""
        hoo = f'Mon {data_store["openMon"]}; Tue {data_store["openTue"]}; Wed {data_store["openWed"]}; Thu {data_store["openThu"]}; Fri {data_store["openFri"]}; Sat {data_store["openSat"]}; Sun {data_store["openSun"]}'
        if "Mon ; Tue ; Wed ; Thu ; Fri ; Sat ; Sun " in hoo:
            hours_of_operation = MISSING
        else:
            hours_of_operation = hoo

        if MISSING not in zip_postal and MISSING in country_code:
            raise Exception("Update the crawler to add new countires")
            # There are 4 countries i.e., GB, IE, BE and NL  data at the moment,
            # if any new country/countries added, crawler will fail allowing
            # us to update the country code for new countries' data
        if str(state) == str(0):
            state = MISSING
        yield SgRecord(
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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
