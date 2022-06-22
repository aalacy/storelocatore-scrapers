import re
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
    start_url = "https://www.tboothwireless.ca/en/locations/"
    domain = "tboothwireless.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@id="city-list"]//a/@href')
    for url in all_cities:
        if "#" in url:
            continue
        city_url = urljoin(start_url, url)
        city_response = session.get(city_url)
        city_dom = etree.HTML(city_response.text)
        data = city_dom.xpath('//script[contains(text(), "page.locations =")]/text()')[
            0
        ]
        data = re.findall("page.locations =(.+);", data)[0]
        all_locations += json.loads(data)

    for poi in all_locations:
        location_name = poi["Name"]
        street_address = poi["Address"]
        if poi["Address2"]:
            street_address += " " + poi["Address2"]
        city = poi["City"]
        state = poi["ProvinceAbbrev"]
        zip_code = poi["PostalCode"]
        country_code = poi["CountryCode"]
        store_number = str(poi["LocationId"])
        url_part = location_name.lower().replace(" ", "-")
        page_url = (
            f"https://www.tboothwireless.ca/en/locations/{store_number}/{url_part}/"
        )
        phone = poi["Phone"]
        latitude = poi["Google_Latitude"]
        longitude = poi["Google_Longitude"]
        hoo = []
        for elem in poi["HoursOfOperation"]:
            day = elem["DayOfWeek"]
            opens = str(float(elem["Open"]) // 100.00).replace(".", ":") + "0"
            closes = str(float(elem["Close"]) // 100.00).replace(".", ":") + "0"
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
