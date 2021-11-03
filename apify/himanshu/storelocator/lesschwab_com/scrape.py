import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lesschwab.com/stores/"
    domain = "lesschwab.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//h5[contains(text(), "Look for Les")]/following-sibling::a/@href'
    )
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(text(), "Store Details")]/@href')
        for url in list(set(all_locations)):
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')
            if poi:
                poi = json.loads(poi[0])
                hoo = loc_dom.xpath(
                    '//section[@class="storeDetails__hoursInformation"]/div/p/text()'
                )
                hoo = " ".join(hoo)
                location_name = poi["name"]
                street_address = poi["address"]["streetAddress"]
                city = poi["address"]["addressLocality"]
                state = poi["address"]["addressRegion"]
                zip_code = poi["address"]["postalCode"]
                phone = poi["telephone"]
                loc_type = poi["@type"]
            else:
                location_name = street_address = loc_dom.xpath(
                    '//a[@title="Store Details"]/text()'
                )[-1].strip()[3:]
                raw_address = (
                    loc_dom.xpath(
                        '//div[@class="storeSearch__resultsSection"]//address[@class="storeDetails__address"]//div[@class="storeDetails__zip"]/text()'
                    )[0]
                    .strip()
                    .split(", ")
                )
                city = raw_address[0]
                state = raw_address[-1].split()[0]
                zip_code = raw_address[-1].split()[0]
                if len(zip_code) == 2:
                    zip_code = ""
                loc_type = ""
                hoo = list(
                    set(
                        loc_dom.xpath(
                            '//h6[contains(text(), "Hours")]/following-sibling::div[1]/p/text()'
                        )
                    )
                )
                hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type=loc_type,
                latitude="",
                longitude="",
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
