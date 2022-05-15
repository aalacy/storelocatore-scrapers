from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    start_url = "https://uberall.com/api/storefinders/ALDINORDDE_UimhY3MWJaxhjK9QdZo3Qa4chq1MAu/locations/all?v=20211005&language=de&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&"
    domain = "aldi-nord.de"

    data = session.get(start_url).json()
    for poi in data["response"]["locations"]:
        city = poi["city"]
        street_address = poi["streetAndNumber"]
        store_number = poi["id"]
        page_url = f"https://www.aldi-nord.de/filialen-und-oeffnungszeiten.html/l/{city.lower()}/{street_address.lower().replace(' ', '-')}/{store_number}"
        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(10)
            loc_dom = etree.HTML(driver.page_source)

        hoo = loc_dom.xpath(
            '//div[@class="ubsf_location-page-opening-hours-list"]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.aldi-nord.de/filialen-und-oeffnungszeiten.html",
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["province"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=store_number,
            phone="",
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
