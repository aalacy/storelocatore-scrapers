# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://bell.bank/api/bell/locationsapi/all?type=branch",
        "https://bell.bank/api/bell/locationsapi/all?type=loan",
        "https://bell.bank/api/bell/locationsapi/all?type=insurance",
    ]
    domain = "bell.bank"

    for start_url in start_urls:
        all_locations = session.get(start_url).json()
        for poi in all_locations:
            page_url = poi["url"]
            if "http" not in page_url:
                page_url = "https://bell.bank" + poi["url"]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//p[contains(text(), "LOBBY HOURS")]/following-sibling::p/text()'
            )
            hoo = ", ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["locationShortName"],
                street_address=poi["streetAddress"],
                city=poi["city"],
                state=poi["state"],
                zip_postal=poi["zip"],
                country_code="",
                store_number="",
                phone=poi["mainPhone"],
                location_type=poi["locationName"].split(", ")[0],
                latitude=poi["lat"],
                longitude=poi["lon"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
