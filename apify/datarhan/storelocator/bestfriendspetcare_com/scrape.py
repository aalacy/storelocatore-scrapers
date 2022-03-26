import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bestfriendspetcare.com"
    start_url = (
        "https://cms.bestfriendspetcare.com/wp-json/cache/v1/locations-by-state/all"
    )

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr)
    data = json.loads(data.text.split("><br />\n")[-1])
    for state in data.keys():
        locations = data[state]["locations"]

        for poi in locations:
            store_url = f'https://www.bestfriendspetcare.com/location/{poi["value"]}'
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi["label"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["line1"]
            if poi["address"]["line2"]:
                street_address += ", " + poi["address"]["line2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["address"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hoo = etree.HTML(poi["hours"])
            hoo = [
                elem.strip() for elem in hoo.xpath("//text()") if "am" in elem.lower()
            ]
            if not hoo:
                hoo = loc_dom.xpath('//p[contains(text(), "am – ")]/text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
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
