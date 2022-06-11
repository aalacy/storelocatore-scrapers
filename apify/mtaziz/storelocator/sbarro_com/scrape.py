from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
from lxml import html
import ssl

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "sbarro.com"
MISSING = SgRecord.MISSING

logger = SgLogSetup().get_logger("sbarro_com")
geolocator = Nominatim(user_agent="sbarro_com_app")

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def get_address_and_hoo_data(purl):
    with SgRequests() as session:
        resp_purl = session.get(purl)
        sel_purl = html.fromstring(resp_purl.text, "lxml")
        try:
            address_data = "".join(
                sel_purl.xpath(
                    '//section[@id="locations-detail"]/script[@type="application/ld+json"]/text()'
                )
            )
            address_data = json.loads(address_data)
            hoo_data = ", ".join(
                sel_purl.xpath('//meta[@itemprop="openingHours"]/@content')
            )
            address_data["hoo"] = hoo_data
            return address_data
        except Exception:
            return {
                "@type": "",
                "address": {
                    "addressLocality": "",
                    "addressRegion": "",
                    "postalCode": "",
                    "streetAddress": "",
                },
                "hoo": "",
                "telephone": "",
            }


def fetch_data():
    with SgRequests() as session:
        RADIUS = "100000"
        URL_WORLDWIDE_SEARCH_RESULTS = f"https://sbarro.com/locations/?user_search=mumbai&radius={RADIUS}&unit=MI&count=All"
        r = session.get(URL_WORLDWIDE_SEARCH_RESULTS, headers=headers)
        sel = html.fromstring(r.text, "lxml")
        sections = sel.xpath(
            '//div[@id="locations-search-form-results"]/section[contains(@class, "locations-result")]'
        )
        for idx, section in enumerate(sections[0:]):
            locator_domain = DOMAIN
            logger.info(f"[Record:{idx}] Locator Domain: {locator_domain}")
            location_name = section.xpath(
                './/h2[contains(@class, "location-name")]//text()'
            )
            location_name = "".join(location_name)
            logger.info(f"[Record:{idx}] Location Name: {location_name}")
            page_url = "".join(
                section.xpath('./h2[contains(@class, "location-name")]/a/@href')
            )
            page_url = f"https://sbarro.com{page_url}"
            logger.info(f"[Record:{idx}] Page URL: {page_url}")

            address_raw = section.xpath(
                './/p[@class="location-address nobottom"]/text()'
            )
            address_raw = "".join(address_raw)

            address_data_json = get_address_and_hoo_data(page_url)
            street_address = address_data_json["address"]["streetAddress"]
            street_address = street_address.replace("&amp;", "&")
            street_address = street_address if street_address else MISSING
            logger.info(f"[Record:{idx}] Street Address: {street_address}")

            city = address_data_json["address"]["addressLocality"]
            city = city if city else MISSING
            logger.info(f"[Record:{idx}] City: {city}")

            state = address_data_json["address"]["addressRegion"]
            state = state if state else MISSING
            logger.info(f"[Record:{idx}] State: {state}")

            zip_postal = address_data_json["address"]["postalCode"]
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[Record:{idx}] Zip Code: {zip_postal}")

            store_number = "".join(section.xpath("./@id")).replace("location-", "")
            logger.info(f"[Record:{idx}] Store Number: {store_number}")

            # Location Type
            location_type = address_data_json["@type"]
            location_type = location_type if location_type else MISSING

            # Phone
            phone = address_data_json["telephone"]

            if phone == "0":
                phone = MISSING
            if phone == "0000000000":
                phone = MISSING
            if "000000" in phone:
                phone = MISSING
            if phone == "-":
                phone = MISSING
            if phone == "tbd":
                phone = MISSING
            phone = phone if phone else MISSING
            logger.info(f"[Record:{idx}] Phone: {phone}")

            # Latlng
            latitude = "".join(section.xpath("./@data-latitude"))
            longitude = "".join(section.xpath("./@data-longitude"))
            latitude = latitude if latitude else MISSING
            longitude = longitude if longitude else MISSING
            if latitude == "0":
                latitude = MISSING
            if longitude == "0":
                longitude = MISSING
            logger.info(f"[Record:{idx}] latitude: {latitude} | longitude: {longitude}")

            # Country Code: Get Country Code using Geolocator
            try:
                # Adding 2 seconds padding between calls
                reverse = RateLimiter(
                    geolocator.reverse,
                    min_delay_seconds=2,
                    return_value_on_exception=None,
                )

                # Returns geopy Location object
                location = reverse(
                    (latitude, longitude), language="en", exactly_one=True
                )
                country_code = location.raw["address"]["country_code"]
                country_code = country_code.upper()
            except Exception:
                country_code = MISSING

            logger.info(f"[Record:{idx}] Country Code: {country_code}")

            # Hours of Operation
            hours_of_operation = address_data_json["hoo"]
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING
            logger.info(f"[Record:{idx}] Hours of Operation: {hours_of_operation}")
            raw_address = address_raw
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
