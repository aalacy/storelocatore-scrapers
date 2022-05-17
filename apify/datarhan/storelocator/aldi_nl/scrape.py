from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    start_url = "https://uberall.com/api/storefinders/ALDINORDNL_8oqeY3lnn9MTZdVzFn4o0WCDVTauoZ/locations/all?v=20211005&language=nl&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&"
    domain = "aldi.nl"
    class_name = "ubsf_details-phone"
    data = session.get(start_url).json()
    for poi in data["response"]["locations"]:
        city = poi["city"]
        street_address = poi["streetAndNumber"]
        store_number = poi["id"]
        page_url = f"https://www.aldi.nl/supermarkt.html/l/{city.lower().replace(' ', '-')}/{street_address.lower().replace(' ', '-').replace('é', 'e').replace('ë', 'e')}/{store_number}"

        with SgFirefox() as driver:
            driver.get(page_url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            loc_dom = etree.HTML(driver.page_source)

        hoo = loc_dom.xpath(
            '//div[@class="ubsf_location-page-opening-hours-list"]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip() and e != "gesloten"])
        phone = loc_dom.xpath('//li[@class="ubsf_details-phone"]/span/text()')
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["province"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=store_number,
            phone=phone,
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

# https://www.aldi.nl/supermarkt.html/l/hardenberg/isra▒l-emanuelplein-9/3187516
