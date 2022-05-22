# -*- coding: utf-8 -*-
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

    start_url = "https://company.modepark.de/standorte"
    domain = "modepark.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="mf-storefinder-listitem"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[contains(text(), "Mehr Informationen")]/@href')[
            0
        ]
        page_url = urljoin(start_url, page_url)
        raw_address = poi_html.xpath(
            './/div[@class="mf-storefinder-listitem-inner"]/p[1]/text()'
        )
        phone = poi_html.xpath('.//p[strong[contains(text(), "Telefon")]]/text()')
        phone = phone[-1].strip().split(": ")[-1] if phone else ""
        geo = poi_html.xpath("@data-options-mf-storefinder-listitem")[0]
        geo = json.loads(geo)
        hoo = poi_html.xpath(
            './/div[@class="mf-storefinder-listitem-inner-openingtime"]/p/text()'
        )
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .split("Bei")[0]
            .replace("Viel Spaß beim Shoppen!", "")
            .strip()
        )
        state = raw_address[-1]
        zip_code = raw_address[1].split()[0]
        state = state.replace(zip_code, "").strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name="",
            street_address=raw_address[0],
            city=" ".join(raw_address[1].split()[1:]),
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo["lat"],
            longitude=geo["lng"],
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
