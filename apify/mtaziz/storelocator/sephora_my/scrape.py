from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from lxml import html
import ssl
import re
from tenacity import retry, stop_after_attempt
from urllib.parse import urlparse


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


STORE_LOCATION_URLS = [
    "https://www.sephora.my/store-locations",
    "https://www.sephora.com.au/store-locations",
    "https://www.sephora.sg/store-locations",
    "https://www.sephora.nz/store-locations",
    "https://www.sephora.hk/store-locations",
    "https://www.sephora.co.th/store-locations",
]

MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("sephora_com")
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def remove_tags(text):
    regex_tag = re.compile(r"<[^>]+>")
    return regex_tag.sub("", text)


@retry(stop=stop_after_attempt(5))
def get_store_data(http, url, headers_c, cookies):
    data_results = http.get(url, headers=headers_c, cookies=cookies).json()
    return data_results


def fetch_records(http: SgRequests):
    for slunum, slu in enumerate(STORE_LOCATION_URLS[0:]):
        logger.info(f"[{slunum}] Pulling Data from {slu}")
        r = http.get(slu, headers=headers)
        sel = html.fromstring(r.text, "lxml")

        # Get CSRF Token from earch store locator page url
        X_CSRF_TOKEN = "".join(
            sel.xpath('//meta[contains(@name, "csrf-token")]/@content')
        )

        # Get accept-language
        accept_lang_xpath = '//div[contains(@id, "app_js")]/script[contains(text(), "acceptLanguage")]/text()'
        al = "".join(sel.xpath(accept_lang_xpath))
        accept_language_custom = (
            al.split("acceptLanguage")[-1]
            .split(";")[0]
            .replace("=", "")
            .replace('"', "")
            .strip()
        )

        # Custom headers for API GET request
        headers_custom = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": accept_language_custom,
            "referer": slu,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "x-csrf-token": X_CSRF_TOKEN,
            "x-requested-with": "XMLHttpRequest",
        }

        # Get domain from store locator URL
        api_domain = urlparse(slu).netloc
        API_ENDPOINT_URL = f"https://{api_domain}/api/booking-services/api/v1/stores?include=services.category,events,beauty-classes,schedules"

        # Cookies
        cookies = dict(r.cookies)

        logger.info(
            f"[{slunum}] Pulling data from API ENDPOINT URL: {API_ENDPOINT_URL}"
        )
        data_per_country = get_store_data(
            http, API_ENDPOINT_URL, headers_custom, cookies
        )
        data_json = data_per_country["data"]
        for idx, item in enumerate(data_json[0:]):
            locator_domain = api_domain.replace("www.", "")
            attr = item["attributes"]
            slug_url = attr["slug-url"]
            page_url = f"https://{api_domain}/store-locations/{slug_url}"
            logger.info(f"[{idx}] page_url: {page_url}")

            location_name = attr["name"]
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] location_name: {location_name}")

            add = attr["address"]
            add = add.split()
            add = " ".join(add).replace("<br>", "")
            if "Discover exclusive makeup" in add:
                add = add.split("Discover exclusive makeup")[0].strip()

            pai = parse_address_intl(add)
            sta1 = pai.street_address_1
            sta2 = pai.street_address_2
            sta = ""
            if sta1 is not None and sta2 is not None:
                sta = sta1 + ", " + sta2
            elif sta1 is not None and sta2 is None:
                sta = sta1
            elif sta1 is None and sta2 is not None:
                sta = sta2
            else:
                sta = MISSING
            street_address = sta.replace("**Temporarily Closed Due To Covid-19** ", "")
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = attr["city"]
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = ""
            if pai.state is not None:
                state = pai.state
            else:
                state = MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = ""
            if pai.postcode is not None:
                zip_postal = pai.postcode
            else:
                zip_postal = MISSING
            logger.info(f"[{idx}] Zip Code: {zip_postal}")

            country_code = attr["country"]["iso_alpha2_code"].upper()
            logger.info(f"[{idx}] country_code: {country_code}")

            store_number = item["id"]
            logger.info(f"[{idx}]  store_number: {store_number}")

            phone = attr["phone"]
            phone = phone if phone else MISSING
            logger.info(f"[{idx}]  Phone: {phone}")

            # Location Type
            location_type = item["type"]
            location_type = location_type if location_type else MISSING
            logger.info(f"[{idx}] location_type: {location_type}")

            # Latitude
            latitude = attr["latitude"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] lat: {latitude}")

            # Longitude
            longitude = attr["longitude"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] lng: {longitude}")

            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            open_times = attr["open-times"]
            close_times = attr["close-times"]
            hoo = []
            for otnum, ot in enumerate(open_times[0:]):
                ot_ct = f"{days[otnum]} {ot} - {close_times[otnum]}"
                hoo.append(ot_ct)
            hours_of_operation = "; ".join(hoo)
            if "Temporarily Closed" in sta:
                hours_of_operation = "Templorarily Closed"
            logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

            # Raw Address
            raw_address = attr["address"]
            raw_address = raw_address.split()
            raw_address = " ".join(raw_address).replace("<br>", "")
            if "Discover exclusive makeup" in raw_address:
                raw_address = raw_address.split("Discover exclusive makeup")[0].strip()
            if " **Temporarily Closed" in raw_address:
                hours_of_operation = "Temporarily Closed"
                raw_address = (
                    raw_address.replace(" **Temporarily Closed due to Covid-19**", "")
                    .replace(" **Temporarily Closed due to Covi-19**", "")
                    .strip()
                )

            # Temporarily Closed Stores
            store_message = attr["store-message"]
            if store_message is not None:
                store_message_clean = remove_tags(store_message)
                logger.info(f"[{idx}] store_message: {store_message_clean}")
                if store_message_clean:
                    if "temporarily closed" in store_message_clean.lower():
                        hours_of_operation = "Templorarily Closed"

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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
