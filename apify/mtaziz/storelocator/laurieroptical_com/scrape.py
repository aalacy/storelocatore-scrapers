from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import ssl
from lxml import html
import json


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MISSING = SgRecord.MISSING
DOMAIN = "laurier-optical.com"
logger = SgLogSetup().get_logger(logger_name="laurieroptical_com")
LOCATION_URL = "https://www.laurier-optical.com/locations"
headers = {
    "accept": "application/json, text/plain, */*",
    "Referer": "https://www.laurier-optical.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def get_json_data_from_features_master_page(http, url):
    response1 = http.get(url, headers=headers, verify=False)
    body = html.fromstring(response1.text, "lxml")
    url_features_master_page = body.xpath(
        '//link[contains(@id, "features_") and @id != "features_masterPage"]/@href'
    )[0]
    response2 = http.get(url_features_master_page, headers=headers, verify=False)
    return {"data": json.loads(response2.text), "body": body}


def fetch_records(http: SgRequests):
    r1 = http.get(LOCATION_URL, headers=headers)
    tree1 = html.fromstring(r1.text, "lxml")
    urls_followed_by_province = tree1.xpath(
        '//a[@data-testid="linkElement" and contains(@href, "eye-exam")]/@href'
    )
    logger.info(f"All province based urls: \n{urls_followed_by_province}")
    for idx, url_province in enumerate(urls_followed_by_province):
        logger.info(f"[{idx}] Pulling the data from: {url_province} ")
        response_dict = get_json_data_from_features_master_page(http, url_province)
        data = response_dict["data"]
        for j in data["props"]["render"]["compProps"].values():
            locator_domain = DOMAIN
            page_url = url_province
            skin = j.get("skin") or ""
            if "WRichTextNewSkin" in skin:
                source = j.get("html") or "<html></html>"
                if 'h2 class="font_2"' and 'span style="font-size:38px"' in source:
                    tree = html.fromstring(source)
                    location_name = tree.xpath(".//text()")[0]
                    logger.info(f"[{idx}] Location Name: {location_name}")

                if "Monday" in source:
                    treeh = html.fromstring(source)
                    text = treeh.xpath(".//text()")
                    for t in text:
                        t1 = " ".join(t.split())
                        if not t1.strip() or "Teppan" in t1:
                            continue
                        if "+" in t1:
                            phone = t1

                if "Tuesday" in source:
                    treeh = html.fromstring(source)
                    text = treeh.xpath(".//text()")[1:]
                    logger.info(f"Text except first element: {text}")
                    hours_of_operation = text
                    hours_of_operation = [
                        " ".join(i.split()) for i in hours_of_operation
                    ]
                    hours_of_operation = [i for i in hours_of_operation if i]
                    hours_of_operation = [
                        i.replace("Tuesday:", "Tuesday: ")
                        .replace("Wednesday:", "Wednesday: ")
                        .replace("Thursday:", "Thursday: ")
                        .replace("Friday:", "Friday: ")
                        .replace("Saturday:", "Saturday: ")
                        for i in hours_of_operation
                    ]
                    hours_of_operation = "; ".join(hours_of_operation)
                    logger.info(f"[{idx}] HOO: {hours_of_operation}")

            if "GoogleMapSkin" in skin:
                logger.info("GoogleMapSkin is found in skin")
                locations = j["mapData"]["locations"][0]
                logger.info(f"[{idx}] Locations data:{locations}")
            else:
                continue

            address = locations["address"]
            logger.info(f"[{idx}] Address: {address} ")
            pai = parse_address_intl(address)

            street_address = pai.street_address_1 or MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = pai.city or MISSING
            logger.info(f"[{idx}] City: {city}")

            state = pai.state or MISSING
            logger.info(f"[{idx}] State: {state}")

            zip_postal = pai.postcode or MISSING
            logger.info(f"[{idx}] Zipcode: {zip_postal}")

            country_code = "CA"
            logger.info(f"[{idx}] Country Code: {country_code}")

            store_number = MISSING
            location_type = MISSING

            latitude = locations["latitude"]
            logger.info(f"[{idx}] Latitude: {latitude}")

            longitude = locations["longitude"]
            logger.info(f"[{idx}] Longitude: {longitude}")
            raw_address = address or MISSING
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
