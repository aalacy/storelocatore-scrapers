import json
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.walterswholesale.com/locations/anaheim"
    domain = "walterswholesale.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        loc_dom = etree.HTML(driver.page_source)
        data = (
            loc_dom.xpath('//script[contains(text(), "currentBranchData")]/text()')[0]
            .split("BranchData =")[1]
            .split(";        var")[0]
        )
        data = json.loads(data)
        for store_number, poi in data.items():
            city = location_name = poi["city"]
            page_url = f"https://www.walterswholesale.com/locations/{city.lower()}"
            street_address = poi["addressLine1"]
            if poi["addressLine2"]:
                street_address += " " + poi["addressLine2"]
            hoo = []
            for day, hours in poi["hours"].items():
                hoo.append(f'{day} {hours["from"]} - {hours["to"]}')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zip"],
                country_code=poi["country"],
                store_number=store_number,
                phone=poi["phone"],
                location_type="",
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
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
