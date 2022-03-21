import json
import random
from lxml import etree
from time import sleep

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sglogging import sglog

log = sglog.SgLogSetup().get_logger("doitbest.com")


def fetch_data():
    session = SgRequests()

    domain = "doitbest.com"
    start_url = "https://doitbest.com/StoreLocator/Submit"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get("https://doitbest.com/store-locator", headers=hdr)
    dom = etree.HTML(response.text)
    csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')[0]
    token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]

    headers = {
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-mod-sbb-ctype": "xhr",
        "x-requested-with": "XMLHttpRequest",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=30
    )
    for code in all_codes:
        str_zip = str(code)
        if len(str_zip) == 4:
            str_zip = "0" + str_zip
            log.info(f"appended zero:{code} => {str_zip}")
        if len(str_zip) == 3:
            str_zip = "00" + str_zip
            log.info(f"appended zeros:{code} => {str_zip}")
        log.info(f"Fetching location for: {str_zip}")
        body = {
            "StoreLocatorForm": {
                "Location": str_zip,
                "Filter": "All Locations",
                "Range": "50",
                "CSRFID": csrfid,
                "CSRFToken": token,
            }
        }
        sleep(random.uniform(0.5, 5.9))
        response = session.post(start_url, headers=headers, json=body)
        code = response.status_code
        while code != 200:
            sleep(random.uniform(5.5, 15.9))
            session = SgRequests()
            response = session.get("https://doitbest.com/store-locator", headers=hdr)
            dom = etree.HTML(response.text)
            csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')
            if not csrfid:
                continue
            csrfid = csrfid[0]
            token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]
            body = {
                "StoreLocatorForm": {
                    "Location": str_zip,
                    "Filter": "All Locations",
                    "Range": "50",
                    "CSRFID": csrfid,
                    "CSRFToken": token,
                }
            }
            response = session.post(start_url, headers=headers, json=body)
            code = response.status_code
        while "online attacks" in response.text:
            session = SgRequests()
            response = session.get("https://doitbest.com/store-locator", headers=hdr)
            dom = etree.HTML(response.text)
            csrfid = dom.xpath('//input[@id="StoreLocatorForm_CSRFID"]/@value')
            if not csrfid:
                continue
            csrfid = csrfid[0]
            token = dom.xpath('//input[@id="StoreLocatorForm_CSRFToken"]/@value')[0]
            body = {
                "StoreLocatorForm": {
                    "Location": str_zip,
                    "Filter": "All Locations",
                    "Range": "50",
                    "CSRFID": csrfid,
                    "CSRFToken": token,
                }
            }
            response = session.post(start_url, headers=headers, json=body)

        if not response.text:
            continue

        data = json.loads(response.text)
        if not data["Response"].get("Stores"):
            continue
        all_locations = data["Response"]["Stores"]

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
