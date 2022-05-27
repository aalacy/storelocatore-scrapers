import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "fiestainsurance.com"
    start_url = "https://www.fiestainsurance.com/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = re.findall(
            "locations = (.+?);",
            loc_response.text.replace(",;", ",")
            .replace("Lane;", "Lane")
            .replace("ve;", "ve")
            .replace("Dr;", "Dr")
            .replace("way;", "way")
            .replace("St;", "St")
            .replace("lvd;", "lvd")
            .replace("SE;", "SE")
            .replace("W;", "W")
            .replace(".;", ".")
            .replace("ue;", "ue")
            .replace("RD;", "RD")
            .replace("d;", "d")
            .replace("t;", "t"),
        )[0][2:-2].split(",")
        raw_data = [e.replace("'", "").replace('"', "").strip() for e in raw_data]
        if "Suite" in raw_data[4]:
            raw_data[3] += " " + raw_data[4]
            del raw_data[4]
        location_name = raw_data[1]
        city = raw_data[1].split("-")[-1]
        if "#" in location_name:
            street_address = raw_data[2]
            state = raw_data[4]
            zip_code = raw_data[5]
            latitude = raw_data[7]
            longitude = raw_data[8]
        else:
            street_address = raw_data[3]
            state = raw_data[5]
            zip_code = raw_data[6]
            latitude = raw_data[8]
            longitude = raw_data[9]
        hoo = loc_dom.xpath(
            '//div[@class="text-start pb-5 storeTiming"]//li/span/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if "#" in city:
            addr = parse_address_intl(city.split("#")[0])
            city = addr.city
        if not city:
            city = raw_data[1].split("-")[-1].split()[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=raw_data[0],
            phone=raw_data[-1],
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
