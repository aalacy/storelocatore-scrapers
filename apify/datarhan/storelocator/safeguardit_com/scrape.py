import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "safeguardit.com"
    start_urls = [
        "https://www.safeguardit.com/florida-storage",
        "https://www.safeguardit.com/illinois-storage",
        "https://www.safeguardit.com/louisiana-storage",
        "https://www.safeguardit.com/new-jersey-storage",
        "https://www.safeguardit.com/new-york-storage",
        "https://www.safeguardit.com/pennsylvania-storage",
    ]

    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="storeAddress"]/h2/a/@href')

        for url in list(set(all_locations)):
            store_url = urljoin(start_urls[0], url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[1]
            poi = demjson.decode(poi.replace("\n", "").replace("\r", ""))

            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = "<MISSING>"
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hours_of_operation = poi["openingHours"].replace("&nbsp;", "")

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
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
