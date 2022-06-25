import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jollyes.co.uk"

    data = session.get("https://www.jollyes.co.uk/api/ext/story-blok/get-stores").json()
    for poi in data["result"]["StoreItems"]["items"]:
        page_url = f"https://www.jollyes.co.uk/store/{poi['slug']}"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        poi_data = loc_dom.xpath('//script[contains(text(), "latitude")]/text()')
        if not poi_data:
            continue
        poi_data = json.loads(poi_data[0])

        hoo = []
        for key, value in poi["content"]["storeTime"][0].items():
            if "Opening" in key:
                day = key.replace("Opening", "")
                if value:
                    opens = value[:2] + ":" + value[2:]
                    closes = poi["content"]["storeTime"][0]["{}Closing".format(day)]
                    closes = closes[:2] + ":" + closes[2:]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
        hoo = " ".join(hoo) if hoo else ""
        location_name = poi["content"]["name"]
        street_address = poi_data["address"]["streetAddress"]
        city = poi_data["address"]["addressLocality"]
        if city and city == "Westwood Centre Kennedy Way":
            city = location_name
            street_address += ", " + poi["content"]["location"][0]["city"]
        if not city:
            city = location_name

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=poi["content"]["location"][0]["county"],
            zip_postal=poi_data["address"]["postalCode"],
            country_code=poi_data["address"]["addressCountry"],
            store_number=poi["content"]["warehouseId"],
            phone=poi["content"]["phoneNumber"],
            location_type="",
            latitude=poi_data["geo"]["latitude"],
            longitude=poi_data["geo"]["longitude"],
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
