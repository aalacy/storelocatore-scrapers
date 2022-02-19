# -*- coding: utf-8 -*-
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep
from random import uniform

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="de")
    scraped_urls = []
    start_url = "https://www.edeka.de/marktsuche.jsp"
    domain = "edeka.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//ul[@class="o-store-search-outro__links"]/li/a/@href')
    for url in all_cities:
        region_url = urljoin(start_url, url)
        response = session.get(region_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = (
            dom.xpath('//script[contains(text(), "storeSearchResults")]/text()')[0]
            .split("storeSearchResults = ")[-1]
            .split(";\n']")[0]
            .strip()[:-1]
        )
        all_locations = json.loads(all_locations)
        more_locations = dom.xpath(
            '//ul[@class="o-store-search-outro__links"]/li/a/@href'
        )
        if more_locations:
            for url in more_locations:
                sub_url = urljoin(region_url, url)
                if sub_url in scraped_urls:
                    continue
                sleep(uniform(0, 3))
                scraped_urls.append(sub_url)
                response = session.get(sub_url, headers=hdr)
                passed = True if "storeSearchResults" in response.text else False
                while not passed:
                    sleep(uniform(5, 10))
                    session = SgRequests()
                    response = session.get(sub_url, headers=hdr)
                    passed = True if "storeSearchResults" in response.text else False
                dom = etree.HTML(response.text)
                more_poi = (
                    dom.xpath(
                        '//script[contains(text(), "storeSearchResults")]/text()'
                    )[0]
                    .split("storeSearchResults = ")[-1]
                    .split(";\n']")[0]
                    .strip()[:-1]
                )
                all_locations += json.loads(more_poi)

        for poi in all_locations:
            hoo = []
            for day, hours in poi["businessHours"].items():
                if day == "additionalInfo":
                    continue
                if poi["businessHours"][day]:
                    opens = hours["from"]
                    closes = hours["to"]
                    hoo.append(f"{day}: {opens} - {closes}")
                else:
                    hoo.append(f"{day}: closed")
            hoo = " ".join(hoo)
            page_url = poi["url"] if poi["url"] else sub_url

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["contact"]["address"]["street"],
                city=poi["contact"]["address"]["city"]["name"],
                state=poi["contact"]["address"]["federalState"],
                zip_postal=poi["contact"]["address"]["city"]["zipCode"],
                country_code="DE",
                store_number=poi["id"],
                phone=poi["contact"]["phoneNumber"],
                location_type="",
                latitude=poi["coordinates"]["lat"],
                longitude=poi["coordinates"]["lon"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
