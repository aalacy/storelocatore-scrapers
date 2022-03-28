from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
import json
from sglogging import SgLogSetup

MISSING = SgRecord.MISSING
STORE_LOCATOR_URL = "https://www.worldwidegolfshops.com/storelocator"
headers = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}
logger = SgLogSetup().get_logger("worldwidegolfshops_com__roger-dunn-golf-shops_aspx")
API_ENDPOINT_URL = "https://www.worldwidegolfshops.com/_v/private/graphql/v1?workspace=master&maxAge=long&appsEtag=remove&domain=store&locale=en-US&__bindingId=0c4c536d-4f48-4f19-853a-aaf8f2d60702"
PAYLOAD = {
    "operationName": "getStores",
    "variables": {},
    "extensions": {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "d61a03e96dd580828aa9c7e18b97ae262fd1a6115add9d4496798455fcf3bdd4",
            "sender": "vtex.yext-store-locator@0.x",
            "provider": "vtex.yext-store-locator@0.x",
        },
        "variables": "eyJmaWx0ZXIiOiJ7XCJjbG9zZWRcIjp7XCIkZXFcIjpmYWxzZX19IiwibG9jYXRpb24iOm51bGwsImxpbWl0IjoxNX0=",
    },
}


def get_headers():
    with SgFirefox(is_headless=True) as driver:
        driver.get(STORE_LOCATOR_URL)
        cookies_ = driver.get_cookies()

    cookies_custom = []
    for cookie in cookies_:
        cookie_formatted = f"{cookie['name']}={cookie['value']}"
        cookies_custom.append(cookie_formatted)

    headers["cookie"] = "; ".join(cookies_custom)
    return headers


def get_hoo(hoo_raw):
    hoo = []
    for e in hoo_raw:
        dw = e["dayOfWeek"]
        if dw == 0:
            daytime = f'Sun: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 1:
            daytime = f'Mon: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 2:
            daytime = f'Tue: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 3:
            daytime = f'Wed: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 4:
            daytime = f'Thu: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 5:
            daytime = f'Fri: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
        if dw == 6:
            daytime = f'Sat: {e["openingTime"]} - {e["closingTime"]}'
            hoo.append(daytime)
    return hoo


def fetch_data():
    with SgRequests() as http:
        try:
            r = http.post(
                API_ENDPOINT_URL, data=json.dumps(PAYLOAD), headers=get_headers()
            )
            json_data = json.loads(r.text)
            logger.info(f"HTTP Status: {r.status_code}")
            data_items = json_data["data"]["getStores"]["items"]
            for poi in data_items:
                hours = get_hoo(poi["businessHours"])
                hours_of_operation = "; ".join(hours)
                store_number = poi["id"]
                state = poi["address"]["state"]
                zip_postal = poi["address"]["postalCode"]
                page_url = f"https://www.worldwidegolfshops.com/store/edwin-watts-golf-{state.lower()}-{zip_postal}/{store_number}"
                item = SgRecord(
                    locator_domain="worldwidegolfshops.com",
                    page_url=page_url,
                    location_name=poi["name"] or MISSING,
                    street_address=poi["address"]["street"] or MISSING,
                    city=poi["address"]["city"] or MISSING,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=poi["address"]["country"],
                    store_number=store_number,
                    phone=poi["mainPhone"],
                    location_type=SgRecord.MISSING,
                    latitude=poi["address"]["location"]["latitude"] or MISSING,
                    longitude=poi["address"]["location"]["longitude"] or MISSING,
                    hours_of_operation=hours_of_operation,
                )
                logger.info(f"item: {item.as_dict()}")
                yield item
        except Exception as e:
            logger.info(f"Please fix this >>> {e}")


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
