# -*- coding: utf-8 -*-
import json
import datetime
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://rx.publix.com/en/pharmacy/search/results"
    domain = "publix.com/pharmacy"
    hdr = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    token = dom.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
    hdr = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for code in all_codes:
        frm = {"__RequestVerificationToken": token, "SearchInput": code}
        response = session.post(start_url, headers=hdr, data=frm)
        dom = etree.HTML(response.text)
        data = dom.xpath('//script[contains(text(), "Mapper")]/text()')
        if not data:
            continue
        data = data[0].split(" Mapper(")[-1].split(", 'Get")[0]
        data = json.loads(data)
        for poi in data["Pharmacies"]:
            store_number = poi["PharmacySummary"]["FacilityID"]
            hoo = dom.xpath(
                f'//div[@id={store_number}]//div[@class="detail-hours-scrollable"]//text()'
            )[1:]
            hoo = " ".join(hoo)
            today = datetime.datetime.now().strftime("%A")
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            hoo = hoo.replace("Today", today).replace(
                "Tomorrow", tomorrow.strftime("%A")
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["PharmacySummary"]["ShoppingCenterName"],
                street_address=poi["PharmacySummary"]["Address"],
                city=poi["PharmacySummary"]["City"],
                state=poi["PharmacySummary"]["State"],
                zip_postal=poi["PharmacySummary"]["Zip"],
                country_code="",
                store_number=store_number,
                phone=poi["PharmacySummary"]["Phone"],
                location_type="",
                latitude=poi["PharmacySummary"]["Latitude"],
                longitude=poi["PharmacySummary"]["Longitude"],
                hours_of_operation=hoo,
            )

            yield item

        token = dom.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]


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
