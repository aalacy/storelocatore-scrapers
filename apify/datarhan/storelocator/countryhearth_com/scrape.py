import json
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.stayinns.com/hotels"
    domain = "countryhearth.com"

    with SgFirefox(block_third_parties=True) as driver:
        driver.get(start_url)
        all_hotels = driver.find_elements_by_xpath(
            '//select[@id="edit-property"]/option'
        )
        for i, h in enumerate(all_hotels):
            driver.find_element_by_id("edit-property").click()
            sleep(2)
            all_hotels[i].click()
            sleep(2)
            driver.find_element_by_id("edit-submit").click()

            loc_dom = etree.HTML(driver.page_source)
            data = loc_dom.xpath('//script[contains(text(), "INITIAL_STATE__")]/text()')
            if not data:
                driver.get(start_url)
                sleep(10)
                all_hotels = driver.find_elements_by_xpath(
                    '//select[@id="edit-property"]/option'
                )
                continue
            data = json.loads(data[0].split("STATE__=")[1].split(";window")[0])
            poi = data["hotelAvailability"]["hotelDetails"]
            street_address = " ".join(poi["hotelAddress"]["AddressLine"]).replace(
                ".", ""
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["hotelName"],
                street_address=street_address,
                city=poi["hotelAddress"]["City"],
                state=poi["hotelAddress"]["StateProv"]["Code"],
                zip_postal=poi["hotelAddress"]["PostalCode"],
                country_code=poi["hotelAddress"]["CountryName"]["Code"],
                store_number=data["hotelAvailability"]["selectedHotel"],
                phone=poi["contactDetails"]["ContactNumberList"][0]["Number"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation="",
            )

            yield item

            driver.get(start_url)
            sleep(10)
            all_hotels = driver.find_elements_by_xpath(
                '//select[@id="edit-property"]/option'
            )


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
