# -*- coding: utf-8 -*-
import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    with open("belgian-cities-geocoded.csv", newline="") as f:
        reader = csv.reader(f)
        all_cities = list(reader)

    start_url = "https://www.texaco.be/handler/fillingstation/list.php"
    domain = "texaco.be"
    hdr = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.texaco.be/nl-be/tankstations?q=belgium",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    for city in all_cities:
        frm = f"type=search&show=private&address={city[1]}&ajax=1"
        data = session.post(start_url, headers=hdr, data=frm).json()

        if data["callback"]:
            for poi in data["callback"][1]["arguments"][0]:
                page_url = (
                    f"https://www.texaco.be/nl-be/tankstations/detail/{poi['id']}"
                )
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)

                phone = (
                    loc_dom.xpath('//p[contains(text(), "Telefoonnummer")]/text()')[0]
                    .split(":")[-1]
                    .strip()
                )
                hoo = loc_dom.xpath('//ul[@class="striplist timetable"]//text()')
                hoo = " ".join([e.strip() for e in hoo if e.strip()])
                zip_code = poi["pc"]
                country_code = ""
                if len(zip_code) == 4:
                    country_code = "Belgium"
                elif len(zip_code.split()) == 2:
                    country_code = "Netherlands"

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["sn"],
                    street_address=poi["st"],
                    city=poi["ct"],
                    state="",
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number="",
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
            SgRecordID({SgRecord.Headers.PAGE_URL}), duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
