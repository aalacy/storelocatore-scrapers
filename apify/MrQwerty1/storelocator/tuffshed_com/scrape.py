from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json


logger = SgLogSetup().get_logger("tuffshed_com")
MISSING = SgRecord.MISSING


def get_bearer_token():
    bearer_token_url = "https://www.tuffshed.com/tsapi/data-shed-api.php"
    js = session.get(bearer_token_url).json()
    response_bearer = json.loads(js["response"])
    bearer_token = "Bearer" + " " + response_bearer["access_token"]
    return bearer_token


def fetch_data(sgw: SgWriter):
    API_ENDPOINT_URL = "https://api.tuffshed.io/sites/Sites/search?SiteTypes=1&SiteTypes=2&SiteTypes=3&SiteTypes=8"
    data = session.get(API_ENDPOINT_URL, headers=headers_new).json()
    logger.info(f"Store Count: {len(data)}")
    for idx, j in enumerate(data):
        page_url = ""
        props = j.get("properties")
        try:
            property_value = ""
            for prop in props:
                if prop["propertyName"] == "MetroPageUrl":
                    property_value = prop.get("propertyValue")

            if property_value:
                page_url = f"https://www.tuffshed.com{property_value}"
            else:
                page_url = MISSING
        except Exception as e:
            page_url = MISSING
            logger.info(f"Fix PageURLError: << {e} >> at {props}")

        location_name = j.get("name") or ""
        logger.info(f"Pulling the store: [{idx}] LocationName: {location_name}")
        g = j.get("siteCoordinates") or {}
        latitude = g.get("siteLatitude")
        longitude = g.get("siteLongitude")
        store_number = location_name.split("-")[0].strip()
        a = j.get("address") or {}
        street_address = a.get("street")
        city = a.get("city")
        state = a.get("stateProvince")
        postal = a.get("postalCode")
        country_code = "US"
        try:
            phone = j["phoneNumbers"][0]["number"]
        except:
            phone = MISSING

        hours = j.get("openingHours") or []
        hours_of_operation = ";".join(hours)
        if not hours_of_operation:
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    logger.info("Scrape started")
    locator_domain = "https://www.tuffshed.com"
    session = SgRequests()
    logger.info("Pulling Bearer Token")
    bearer_token = get_bearer_token()
    headers_new = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": bearer_token,
        "Origin": "https://www.tuffshed.com",
        "Connection": "keep-alive",
        "Referer": "https://www.tuffshed.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
    }

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Scrape Finished")
