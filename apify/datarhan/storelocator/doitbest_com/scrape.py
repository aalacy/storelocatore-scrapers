from sgselenium import SgChrome
import time
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sglogging import sglog
import json

from tenacity import retry, stop_after_attempt
import tenacity
import random

domain = "doitbest.com"
log = sglog.SgLogSetup().get_logger(domain)

session = SgRequests(retries_with_fresh_proxy_ip=7)

hdr = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

response = session.get("https://doitbest.com/store-locator", headers=hdr)
log.info(f"CSRF & Token Response: {response}")
dom = etree.HTML(response.text)
csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')[0]
token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]

payload = {
    "StoreLocatorForm": {
        "Location": "TX",
        "Filter": "All Locations",
        "Range": "2000",
        "CSRFID": csrfid,
        "CSRFToken": token,
    }
}

headers = {
    "authority": "www.doitbest.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://www.doitbest.com",
    "referer": "https://www.doitbest.com/store-locator",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "x-mod-sbb-ctype": "xhr",
    "x-requested-with": "XMLHttpRequest",
}


def get_headers_cookies(url_location):
    with SgChrome(is_headless=True) as driver:
        driver.get(url_location)
        time.sleep(10)
        cookies_ = driver.get_cookies()

    cookies_custom = []
    for cookie in cookies_:
        cookie_formatted = f"{cookie['name']}={cookie['value']}"
        cookies_custom.append(cookie_formatted)

    headers["cookie"] = "; ".join(cookies_custom)

    return headers


headers = get_headers_cookies("https://doitbest.com/store-locator")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.post(url, headers=headers, json=payload)
        log.info(f"Retry POST RESPONSE: {response} ")
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            log.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_data():
    url = "https://www.doitbest.com/StoreLocator/Submit"
    all_locations = []
    response = session.post(url, headers=headers, json=payload)
    log.info(f"POST RESPONSE: {response} ")
    if response.status_code != 200:
        response = get_response(url)

    data = json.loads(response.text)
    all_locations += data["Response"]["Stores"]
    log.info(f" Total Location: {len(all_locations)}")
    for poi in all_locations:
        store_url = poi["WebsiteURL"]
        store_url = "https://" + store_url if store_url else "<MISSING>"
        try:
            location_name = poi["Name"]
        except TypeError:
            continue
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address1"]
        if poi["Address2"]:
            street_address += ", " + poi["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi.get("ZipCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
