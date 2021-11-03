import ssl
import json
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()
    domain = "wafdbank.com"
    start_url = "https://www.wafdbank.com/locations"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    states_urls = dom.xpath(
        '//h2[contains(text(), "Browse Locations by State")]/following-sibling::p/a/@href'
    )
    for url in states_urls:
        state_response = session.get(
            "https://www.wafdbank.com/page-data/locations/{}/page-data.json".format(
                url.split("/")[-1]
            )
        )
        data = json.loads(state_response.text)
        for elem in data["result"]["pageContext"]["stateData"]["branch_locations"]:
            all_locations.append(elem["PageURL"])

    for url in list(set(all_locations)):
        store_url = "https://www.wafdbank.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath('//script[@data-react-helmet="true"]/text()')
        if store_data:
            poi = json.loads(store_data[0])
            location_name = poi["name"]
            if not location_name:
                continue
            location_name = (
                location_name.replace("&#x27;", "'").replace("&amp;", "")
                if location_name
                else "<MISSING>"
            )
            street_address = poi["address"]["streetAddress"]
            street_address = (
                street_address.replace("&quot;", "") if street_address else "<MISSING>"
            )
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = poi["branchCode"]
            phone = poi["telephone"]
            location_type = poi["@type"]
            latitude = ""
            longitude = ""
            if poi["geo"]:
                latitude = poi["geo"]["latitude"]
                longitude = poi["geo"]["longitude"]
            if "locations/washington" in store_url:
                latitude = "48.646755"
                longitude = "-118.737804"
            else:
                latitude = latitude if latitude else "<MISSING>"
                longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = []
            for elem in poi["openingHoursSpecification"]:
                day = elem["dayOfWeek"].split("/")[-1]
                opens = elem["opens"][:-3]
                closes = elem["closes"][:-3]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            hours_of_operation = ", ".join(hours_of_operation)
            if "Saturday" not in hours_of_operation:
                hours_of_operation += ", Saturday Closed"
            if "Sunday" not in hours_of_operation:
                hours_of_operation += ", Sunday Closed"
        else:
            raw_data = store_dom.xpath(
                '//div[@id="branch-location-container"]//a[contains(@href, "maps")]/text()'
            )
            raw_data = [
                e.replace("Â\xa0Â", "").strip()
                for e in raw_data
                if e.strip() and e != ","
            ]
            raw_data = [e for e in raw_data if e.strip()]
            location_name = store_dom.xpath('//h1[@class="mb-3"]/text()')[-1].strip()
            street_address = raw_data[0]
            city = raw_data[1]
            state = raw_data[2]
            zip_code = raw_data[-1]
            country_code = SgRecord.MISSING
            store_number = SgRecord.MISSING
            phone = store_dom.xpath(
                '//svg[@data-icon="phone"]/following-sibling::a/text()'
            )
            phone = phone[0] if phone else SgRecord.MISSING
            location_type = SgRecord.MISSING
            with SgChrome() as driver:
                driver.get(store_url)
                sleep(10)
                store_dom = etree.HTML(driver.page_source)
                geo = (
                    store_dom.xpath('//a[contains(@href, "maps?ll")]/@href')[0]
                    .split("=")[1]
                    .split("&")[0]
                    .split(",")
                )
                latitude = geo[0]
                longitude = geo[1]
            hours_of_operation = store_dom.xpath('//div[@class="lobbyHours"]//text()')[
                1:
            ]
            hours_of_operation = " ".join(hours_of_operation)

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
