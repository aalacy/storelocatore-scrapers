import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import random
import time
from tenacity import retry, stop_after_attempt
import tenacity


API_ENDPOINT_URLS = [
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?search=75022&level=domain&template=domain&limit=5000&radius=5000",
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?template=search&level=search&search=bahrain&radius=10000",
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?template=search&level=search&search=guam&radius=10000",
]
DOMAIN = "ihop.com"
logger = SgLogSetup().get_logger("ihop_com")
MISSING = SgRecord.MISSING
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests(proxy_country="us", timeout_config=300) as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(10, 30))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_hours(raw_hours):
    temp_open_close = []
    hours_of_operation = ""
    tmp_js = json.loads(raw_hours.get("hours_sets:primary")).get("days", {})
    for day in tmp_js.keys():
        octime = tmp_js[day]
        if isinstance(octime, list):
            start = octime[0]["open"]
            close = octime[0]["close"]
            temp_open_close.append(f"{day} {start} - {close}")
        elif isinstance(octime, str):
            temp_open_close.append(f"{day} {octime}")
        else:
            temp_open_close.append(f"{day} {octime}")
    if temp_open_close:
        hours_of_operation = "; ".join(temp_open_close)
    else:
        hours_of_operation = MISSING
    return hours_of_operation


def fetch_data(sgw: SgWriter):
    for idx, api_url in enumerate(API_ENDPOINT_URLS):
        r = get_response(idx, api_url)
        js_init = r.json()["maplist"]
        line = (
            "["
            + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0]
            + "]"
        )
        js = json.loads(line)
        js_markers = r.json()["markers"]
        for idx1, j in enumerate(js):
            page_url = ""
            store_url = j.get("url")
            country_code = j.get("country") or MISSING
            if country_code == "US" or country_code == "PR":
                page_url = store_url.replace(
                    "https://restaurants.ihop.com/",
                    "https://restaurants.ihop.com/en-us/",
                )

            if country_code == "CA":
                page_url = store_url.replace(
                    "https://restaurants.ihop.com/",
                    "https://restaurants.ihop.com/en-ca/",
                )

            if country_code == "PA":
                page_url = store_url

            if not store_url:
                page_url = MISSING

            location_name = j.get("location_name") or MISSING
            logger.info(f"[{idx1}] Location Name: {location_name}")
            street_address = (
                f"{j.get('address_1')} {j.get('address_2')}".strip() or MISSING
            )
            city = j.get("city") or MISSING
            state = j.get("region") or MISSING
            postal = j.get("post_code") or MISSING

            if "MX" in str(country_code):
                continue
            store_number = j.get("fid") or MISSING
            phone = j.get("local_phone") or MISSING
            latitude = js_markers[idx].get("lat") or MISSING
            longitude = js_markers[idx].get("lng") or MISSING
            location_type = j.get("location_type") or MISSING
            hoo = get_hours(j)
            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                locator_domain=DOMAIN,
                hours_of_operation=hoo,
                raw_address=MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    logger.info(f"Scrape Started!")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        fetch_data(writer)
    logger.info(f"Scrape Finished!")  # noqa
