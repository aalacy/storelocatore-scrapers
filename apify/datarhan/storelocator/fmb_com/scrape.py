import json
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    domain = "fmb.com"
    start_url = "https://www.fmb.com/locations"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        data = (
            dom.xpath('//script[contains(text(), "CONFIGURATION")]/text()')[0]
            .split("CONFIGURATION =")[-1]
            .split(";\n        \n\n        function")[0]
        )
        data = json.loads(
            data.replace("weekdayHoursOpen1", '"weekdayHoursOpen1"')
            .replace("weekdayHoursClose1", '"weekdayHoursClose1"')
            .replace("fridayHoursOpen1", '"fridayHoursOpen1"')
            .replace("fridayHoursClose1", '"fridayHoursClose1"')
            .replace("hours1", '"hours1"')
            .replace("hours2", '"hours2"')
            .replace("hours3", '"hours3"')
            .replace("county1", '"county1"')
            .replace("county2", '"county2"')
            .replace("county3", '"county1"')
            .replace("hours4", '"hours4"')
            .replace("hours5", '"hours5"')
            .replace("weekdayHoursClose2", '"weekdayHoursClose2"')
            .replace("weekdayHoursOpen2", '"weekdayHoursOpen2"')
            .replace("fridayHoursOpen2", '"fridayHoursOpen2"')
            .replace("fridayHoursClose2", '"fridayHoursClose2"')
        )

        for poi in data["locations"]:
            page_url = "https://www.fmb.com/locations/" + poi["url"]
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)
            phone = loc_dom.xpath(
                '//div[contains(text(), "get in touch")]/following-sibling::div//span/text()'
            )[0].split()[0]
            hoo = " ".join(
                loc_dom.xpath(
                    '//div[contains(text(), " hours ")]/following-sibling::p/text()'
                )[0].split()
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["title"],
                street_address=poi["address1"],
                city=poi["address2"].split(", ")[0],
                state=poi["address2"].split(", ")[1].split()[0],
                zip_postal=poi["address2"].split(", ")[1].split()[1],
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude=poi["coords"]["lat"],
                longitude=poi["coords"]["lng"],
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
