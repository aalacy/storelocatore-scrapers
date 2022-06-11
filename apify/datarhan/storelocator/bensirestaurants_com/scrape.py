from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bensirestaurants.com"
    store_urls = [
        "https://www.bensirestaurants.com/",
        "https://www.bensirestaurants.com/bensi-denville.html",
    ]

    for store_url in store_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath('//font[contains(text(), "Bensi Restaurant")]/text()')
        if raw_data:
            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=raw_data[0].split("-")[0],
                street_address=raw_data[1].split(", ")[0],
                city=raw_data[1].split(", ")[1],
                state=raw_data[1].split(", ")[-1].split()[0],
                zip_postal=raw_data[1].split(", ")[-1].split()[1],
                country_code="",
                store_number="",
                phone=raw_data[0].split(" - ")[-1].replace("Call", ""),
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation="",
            )

            yield item
        else:
            raw_data = loc_dom.xpath(
                '//font[contains(text(), "Bensi Whitehouse Station")]/text()'
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=raw_data[0],
                street_address=raw_data[2].split(",")[0],
                city=raw_data[3].split(", ")[0],
                state=raw_data[3].split(", ")[-1].split()[0],
                zip_postal=raw_data[3].split(", ")[-1].split()[-1],
                country_code="",
                store_number="",
                phone=raw_data[1].replace("Tel", "").strip(),
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=raw_data[4],
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
