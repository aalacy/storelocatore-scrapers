from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "warbyparker.com"
    start_url = "https://www.warbyparker.com/retail"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//h1/a/@href")
    for url in all_locations:
        store_url = urljoin(start_url, url)
        poi_url = "https://www.warbyparker.com/api/v2/retail/locations" + url.replace(
            "/retail", ""
        )
        poi = session.get(poi_url)
        if poi.status_code != 200:
            continue
        poi = poi.json()
        hoo = []
        for day, hours in poi["schedules"][0]["hours"].items():
            if hours.get("open"):
                hoo.append(f'{day}: {hours["open"]} - {hours["close"]}')
            else:
                hoo.append(f"{day}: closed")
        hoo = " ".join(hoo)
        phone = poi["cms_content"]["phone"]
        if not phone:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/@href')[0].split(":")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=poi["address"]["street_address"],
            city=poi["address"]["locality"],
            state=poi["address"]["region_code"],
            zip_postal=poi["address"]["postal_code"],
            country_code=poi["address"]["country_code"],
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["cms_content"]["map_details"]["latitude"],
            longitude=poi["cms_content"]["map_details"]["longitude"],
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
