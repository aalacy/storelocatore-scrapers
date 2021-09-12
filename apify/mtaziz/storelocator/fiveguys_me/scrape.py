from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import ssl
from urllib.parse import urlparse

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="fiveguys_me")
MISSING = SgRecord.MISSING
DOMAIN = "fiveguys.me"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

api_endpoint_urls = [
    "https://restaurants.fiveguys.me/en_bh/search?country=BH&qp=Bahrain&l=en_BH",
    "https://restaurants.fiveguys.me/en_bh/search?country=QA&qp=Qatar&l=en_BH",
    "https://restaurants.fiveguys.me/en_bh/search?country=KW&qp=Kuwait&l=en_BH",
    "https://restaurants.fiveguys.ae/en_ae/search?country=AE&qp=United%20Arab%20Emirates&l=en_AE",
    "https://restaurants.fiveguys.at/en_at/search?country=AT&qp=Austria&l=en_AT",
    "https://restaurants.fiveguys.nl/en_nl/search?country=NL&qp=Netherlands&l=en_NL",
]


@retry(stop=stop_after_attempt(5))
def fetch_data(http, url):
    data = http.get(url, headers=HEADERS).json()
    entities = data["response"]["entities"]
    return entities


def fetch_records(http: SgRequests):
    for api_endpoint_url in api_endpoint_urls:
        res_ent = fetch_data(http, api_endpoint_url)
        for idx, _ in enumerate(res_ent):
            profile = _["profile"]

            # locator_domain = ""
            parsed_url = urlparse(api_endpoint_urls[0]).netloc
            locator_domain = parsed_url.replace("restaurants.", "")
            logger.info(f"[{idx}] domain: {locator_domain}")

            # Page URL
            page_url = profile["c_pagesURL"]
            logger.info(f"[{idx}] purl: {page_url}")

            # Location Name
            locname = profile["c_aboutSectionHeading"].replace("About ", "")
            location_name = locname if locname else MISSING
            logger.info(f"[{idx}] Locname: {location_name}")

            add = profile["address"]

            # Street Address
            line1 = add["line1"]
            line2 = add["line2"]
            line3 = add["line3"]
            street_address = ""
            if line1 is not None:
                street_address = line1
            elif line1 is not None and line2 is not None:
                street_address = line1 + " " + line2
            elif line1 is not None and line2 is not None and line3 is not None:
                street_address = line1 + " " + line2 + " " + line3
            else:
                street_address = MISSING
            logger.info(f"[{idx}] st_add: {street_address}")

            city = add["city"]
            logger.info(f"[{idx}] st_add: {street_address}")

            state = add["region"]
            if state is not None:
                state = state
            else:
                state = MISSING
            logger.info(f"[{idx}] state: {state}")

            zip_postal = add["postalCode"]
            if zip_postal is not None:
                zip_postal = zip_postal
            else:
                zip_postal = MISSING
            logger.info(f"[{idx}] zip: {zip_postal}")

            # Country Code
            country_code = add["countryCode"]
            logger.info(f"[{idx}] country_code: {country_code}")

            # Store Number
            store_number = profile["meta"]["id"]
            store_number = store_number if store_number else MISSING
            logger.info(f"[{idx}] store_number: {store_number}")

            # Phone
            phone = profile["mainPhone"]["number"]
            phone = phone if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            # location_type
            loct = profile["meta"]["schemaTypes"]
            loct = ", ".join(loct)
            location_type = loct if loct else MISSING
            logger.info(f"[{idx}] location_type: {location_type}")

            # Latitude
            lat = profile["yextDisplayCoordinate"]["lat"]
            latitude = lat if lat else MISSING
            logger.info(f"[{idx}] lat: {latitude}")

            # Longitude
            lng = profile["yextDisplayCoordinate"]["long"]
            longitude = lng if lng else MISSING
            logger.info(f"[{idx}] long: {longitude}")

            # Hours of Operation
            hoo = ""
            for i in profile["hours"]["normalHours"]:
                day_se = (
                    i["day"]
                    + " "
                    + str(i["intervals"][0]["start"])
                    + " - "
                    + str(i["intervals"][0]["end"])
                )
                hoo += day_se + "; "
            hoo = hoo.strip().rstrip(";")
            hours_of_operation = hoo
            logger.info(f"[{idx}] hoo: {hours_of_operation}")

            raw_address = MISSING
            logger.info(f"[{idx}] raw_add: {raw_address}")
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
    count = 0
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
