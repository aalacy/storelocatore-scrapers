import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.maison-kayser.com/boulangeries"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall("BV.stores =(.+);", response.text)[0]

    all_locations = json.loads(data)
    for id, poi in all_locations.items():
        poi_html = etree.HTML(poi["info_box_html"])
        store_url = poi_html.xpath('//a[@class="button"]/@href')[0]
        location_name = poi["name"]
        location_name = location_name if location_name else SgRecord.MISSING
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        city = parse_address_intl(poi["city"]).city
        if not city:
            city = poi["city"]
        city = city.split(",")[0]
        if city == "Newyork":
            city = "New York"
        city = city.replace("NewYork", "New York")
        state = poi["state_name"]
        state = state if state else SgRecord.MISSING
        zip_code = poi["postcode"]
        zip_code = zip_code if zip_code else SgRecord.MISSING
        if zip_code == "00000":
            zip_code = SgRecord.MISSING
        store_number = poi["id_store"]
        phone = poi["phone"]
        phone = phone if phone else SgRecord.MISSING
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        hoo = []
        hours = poi["hours"]
        for i, day in enumerate(days):
            opens = hours[i].strip()
            opens = opens if opens else "Fermé"
            hoo.append(f"{day} {opens}")
        hours_of_operation = " ".join(hoo) if hoo else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
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
