from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bomgaars.com"
    start_url = "https://www.bomgaars.com//graphql"
    frm = {
        "operationName": "",
        "variables": {"pageSize": 500},
        "query": "# @package     BlueAcorn/StoreLocator\n# @version     2.0.0\n# @author      Blue Acorn iCi. <code@blueacorn.com>\n# @copyright   Copyright © Blue Acorn iCi. All Rights Reserved.\nquery ba_stores($page: Int, $pageSize: Int) {\n    ba_stores(currentPage: $page, pageSize: $pageSize) {\n        page_info {\n            current_page\n            page_size\n            total_pages\n        }\n        total_count\n        items {\n            store_id\n            is_enabled\n            url_key\n            name\n            description\n            short_description\n            store_image\n            store_icon_image\n            latitude\n            longitude\n            zoom\n            phone_number\n            email_address\n            store_address\n            store_city\n            store_state\n            store_zip\n            store_country\n            sunday_status\n            sunday_open\n            sunday_close\n            monday_status\n            monday_open\n            monday_close\n            tuesday_status\n            tuesday_open\n            tuesday_close\n            wednesday_status\n            wednesday_open\n            wednesday_close\n            thursday_status\n            thursday_open\n            thursday_close\n            friday_status\n            friday_open\n            friday_close\n            saturday_status\n            saturday_open\n            saturday_close\n            distance\n        }\n    }\n}\n",
    }
    hdr = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
        "x-newrelic-id": "VwUHUlJWARABVlVaAwcPUVYJ",
        "x-requested-with": "XMLHttpRequest",
    }
    data = session.post(start_url, json=frm, headers=hdr).json()
    for poi in data["data"]["ba_stores"]["items"]:
        page_url = urljoin(start_url, poi["url_key"])
        sun = f'Sunday: {poi["sunday_open"]} - {poi["sunday_close"]}'
        mon = f'Monday: {poi["monday_open"]} - {poi["monday_close"]}'
        tue = f'Tuesday: {poi["tuesday_open"]} - {poi["tuesday_close"]}'
        wed = f'Wednesday: {poi["wednesday_open"]} - {poi["wednesday_open"]}'
        thu = f'Thursday: {poi["thursday_open"]} - {poi["thursday_close"]}'
        fri = f'Friday: {poi["friday_open"]} - {poi["friday_close"]}'
        sat = f'Saturday: {poi["saturday_open"]} - {poi["saturday_close"]}'
        hoo = f"{sun}, {mon}, {tue}, {wed}, {thu}, {fri}, {sat}"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["store_address"],
            city=poi["store_city"],
            state=poi["store_state"],
            zip_postal=poi["store_zip"],
            country_code=poi["store_country"],
            store_number=poi["store_id"],
            phone=poi["phone_number"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
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
