import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.co.jp/dealer/Map/getPref/shop/"
    domain = "suzuki.co.jp"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    user_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    }
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//select[@name="addr_pref"]/option/@value')[1:]
    for r in all_regions:
        frm = {"t_code": r}
        url = f"https://www.suzuki.co.jp/dealer/Map/getCity/{r}"
        response = session.post(url, data=frm, headers=hdr)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath("//option/@value")[1:]
        for c in all_cities:
            url = f"https://www.suzuki.co.jp/dealer/Map/getDealers/shop/{c}"
            response = session.get(url, headers=user_agent)
            dom = etree.HTML(response.text)
            data = (
                dom.xpath('//script[contains(text(), "offices = ")]/text()')[0]
                .split(" offices =")[-1]
                .split(";\n        var pincode")[0]
            )
            all_locations = json.loads(data)
            for poi in all_locations:
                page_url = poi["url"]
                loc_response = session.get(page_url, headers=user_agent)
                if loc_response.status_code != 200:
                    continue
                loc_dom = etree.HTML(loc_response.text)
                location_type = ", ".join(
                    loc_dom.xpath(
                        '//*[@id="service"]//span[@class="el_txtIcon"]/text()'
                    )
                )
                if "新車取扱い" not in location_type:
                    continue
                raw_address = poi["pincode"]
                addr = parse_address_intl(raw_address)
                hoo = " ".join(poi["sales_hours"].split()).split("(")[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["name"],
                    street_address=poi["address"],
                    city=addr.city,
                    state="",
                    zip_postal=addr.postcode,
                    country_code="JP",
                    store_number="",
                    phone=poi["tel"],
                    location_type=location_type,
                    latitude=poi["lat"],
                    longitude=poi["lng"],
                    hours_of_operation=hoo,
                    raw_address=raw_address,
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
