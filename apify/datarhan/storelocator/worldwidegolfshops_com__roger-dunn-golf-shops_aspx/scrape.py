import re
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.worldwidegolfshops.com/roger-dunn-golf-shops"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)
        data = dom.xpath('//script[contains(text(), "find-a-store")]/text()')[2].split(
            "__RUNTIME__ ="
        )[-1]
        data = json.loads(data)
        all_poi = []
        for k, v in data.items():
            if (
                "store.custom.find-a-store#roger-dunn-golf-shops/flex-layout.row#find-a-store-rogerDunnContainer"
                in k
            ):
                all_poi.append(v)

        all_locations = []
        for poi in all_poi:
            if not poi["content"].get("text"):
                continue
            poi_html = etree.HTML(poi["content"]["text"])
            url = poi_html.xpath(".//a/@href")
            if url:
                all_locations.append(url[0])

        for url in all_locations:
            page_url = urljoin(start_url, url)
            print(page_url)
            driver.get(page_url)
            sleep(5)
            loc_dom = etree.HTML(driver.page_source)
            if "worldwidegolfshops.com" in page_url:
                poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
                poi = json.loads(poi)
                location_name = loc_dom.xpath(
                    '//h1[contains(@class, "storeTitle")]/text()'
                )[0]
                hoo = []
                for e in poi["openingHoursSpecification"]:
                    hoo.append(f'{e["dayOfWeek"]} {e["opens"]} {e["closes"]}')
                hours_of_operation = " ".join(hoo)
                street_address = poi["address"]["streetAddress"]
                city = poi["address"]["addressLocality"]
                state = poi["address"]["addressRegion"]
                zip_code = poi["address"]["postalCode"]
                store_number = poi["@id"]
                phone = poi["telephone"]
                location_type = poi["@type"][0]
                latitude = poi["geo"]["latitude"]
                longitude = poi["geo"]["longitude"]
                country_code = SgRecord.MISSING
            else:
                poi = loc_dom.xpath("//@data-block-json")[0]
                poi = json.loads(poi)
                location_name = poi["location"]["addressTitle"]
                street_address = poi["location"]["addressLine1"]
                city = poi["location"]["addressLine2"].split(", ")[0]
                state = poi["location"]["addressLine2"].split(", ")[-1].split()[0]
                zip_code = poi["location"]["addressLine2"].split(", ")[-1].split()[-1]
                store_number = SgRecord.MISSING
                phone = loc_dom.xpath(
                    '//p[strong[contains(text(), "Phone")]]/following-sibling::p/text()'
                )
                phone = phone[0] if phone else SgRecord.MISSING
                location_type = SgRecord.MISSING
                latitude = poi["location"]["mapLat"]
                longitude = poi["location"]["mapLng"]
                hoo = loc_dom.xpath(
                    '//p[strong[contains(text(), "HOURS")]]/following-sibling::p/text()'
                )
                hoo = [e.strip() for e in hoo if "(" not in e]
                hours_of_operation = " ".join(hoo)
            if len(state) > 2:
                state = SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
