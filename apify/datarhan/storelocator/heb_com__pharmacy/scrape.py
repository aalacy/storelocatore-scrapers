# -*- coding: utf-8 -*-
import ssl
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep
from random import uniform

from sgrequests.sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests(proxy_country="us")
    start_url = "https://www.heb.com/store-locations"
    domain = "heb.com"

    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        "sec-ch-ua-platform": '"macOS"',
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//a[@class="store-card__action"]/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url, headers=hdr)
            while "_Incapsula_Resource" in loc_response.text:
                sleep(uniform(2, 15))
                session = SgRequests(proxy_country="us")
                loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)
            pharmacy = loc_dom.xpath('//h2[contains(text(), "Pharmacy")]')
            if not pharmacy:
                continue
            poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')[0]
            poi = json.loads(poi)
            poi = poi["department"][0]
            hoo = []
            for e in poi["openingHoursSpecification"]:
                hoo.append(f'{e["dayOfWeek"]}: {e["opens"]} - {e["closes"]}')
            hoo = " ".join(hoo)
            geo = (
                loc_dom.xpath("//source/@srcset")[0]
                .split("?center=")[-1]
                .split("&")[0]
                .split("%2C")
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["addressCountry"],
                store_number="",
                phone=poi["telephone"],
                location_type=poi["@type"],
                latitude=geo[0],
                longitude=geo[1],
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
