# -*- coding: utf-8 -*-
import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.igaliquor.com.au/store-locator/results/{}%2C{}?from=3000&postcode={}"
    domain = "igaliquor.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA], expected_search_radius_miles=200
    )
    for code, coords in all_codes:
        lat, lng = coords
        response = session.get(start_url.format(lat, lng, code), headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(text(), "DETAILS")]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/text()")[0]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            street_address = loc_dom.xpath(
                '//div[@property="schema:streetAddress"]/text()'
            )[0]
            city = loc_dom.xpath('//span[@property="schema:addressLocality"]/text()')[0]
            state = loc_dom.xpath('//span[@property="schema:addressRegion"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@property="schema:postalCode"]/text()')[0]
            country_code = loc_dom.xpath(
                '//span[@property="schema:addressCountry"]/text()'
            )[0]
            latitude = re.findall('"latitude":(.+?),', loc_response.text)[-1]
            longitude = re.findall(r'"longitude":(.+?)\}', loc_response.text)[-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
