# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "hema.nl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    countries = {
        "NL": "https://www.hema.nl/on/demandware.store/Sites-HemaNL-Site/nl_NL/Stores-Load?start=0&count=1000&shipmentId=&isSunday=&mode=fullpage&services=&format=ajax&mode=fullpage",
        "BE": "https://www.hema.com/on/demandware.store/Sites-HemaBE-Site/nl_BE/Stores-Load?start=0&count=1000&shipmentId=&isSunday=&mode=fullpage&services=&format=ajax&mode=fullpage",
        "DE": "https://www.hema.com/on/demandware.store/Sites-HemaDE-Site/de_DE/Stores-Load?start=0&count=1000&shipmentId=&isSunday=&mode=fullpage&services=&format=ajax&mode=fullpage",
        "FR": "https://www.hema.com/on/demandware.store/Sites-HemaFR-Site/fr_FR/Stores-Load?start=6&count=5&shipmentId=&isSunday=&mode=fullpage&services=&format=ajax&mode=fullpage",
    }
    page_urls = {
        "FR": "https://www.hema.com/fr-fr/magasins",
        "DE": "https://www.hema.com/de-de/filiale-suchen",
        "BE": "https://www.hema.com/nl-be/winkels",
        "NL": "https://www.hema.nl/winkel-zoeken",
    }
    for country, start_url in countries.items():
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//li[@class="store "]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(
                './/div[@class="store-info-main store-info js-selected-store-info"]/h4/text()'
            )[0]
            raw_address = poi_html.xpath(
                './div/div[1]/div[@class="store-info-main store-info js-selected-store-info"][1]/span/span/text()'
            )
            phone = poi_html.xpath('.//a[@class="store-info-phone"]/text()')
            phone = phone[0] if phone else ""
            hoo = poi_html.xpath(
                './/ul[@class="js-selected-store-opening-hours"]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            location_type = poi_html.xpath(
                './/ul[@class="usp-list js-selected-store-usp-list"]/li/span/text()'
            )
            location_type = ", ".join([e.strip() for e in location_type])
            geo = (
                poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
                .split("@")[-1]
                .split(",")[:2]
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_urls[country],
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[2].split("(")[0],
                state="",
                zip_postal=raw_address[1],
                country_code=country,
                store_number="",
                phone=phone,
                location_type=location_type,
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
