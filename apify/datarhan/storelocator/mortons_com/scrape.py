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
    domain = "mortons.com"
    start_url = "https://www.mortons.com/locations/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath("//script[contains(text(), locations)]/text()")
    all_locations = re.findall("locations: (.+) apiKey:", data[7].replace("\n", ""))[
        0
    ].strip()[:-1]
    all_locations = json.loads(all_locations)

    for poi in all_locations:
        store_url = urljoin(start_url, poi["url"])
        loc_reponse = session.get(store_url)
        loc_dom = etree.HTML(loc_reponse.text)

        location_name = poi["name"]
        street_address = poi["street"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal_code"]
        store_number = poi["id"]
        phone = poi["phone_number"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//div[h2[@class="h1"]]/p[2]//text()')
        hoo = [e.strip() for e in hoo if e.strip() and "We " not in e]
        hours_of_operation = (
            " ".join(hoo)
            .split("Parties")[0]
            .split("Inside")[0]
            .split("General")[0]
            .split("Proper")[0]
            .replace("Dining Room", "")
            .split("Located")[0]
            .strip()
            if hoo
            else ""
        )
        country_code = "US"
        if len(state) > 2:
            country_code = state
            state = ""
        if len(zip_code.split()) == 2:
            country_code = "CA"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
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
