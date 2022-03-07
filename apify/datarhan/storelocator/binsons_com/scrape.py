import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "binsons.com"
    start_url = "https://www.binsons.com/modules/locations/library/gmap.php"

    formdata = {"types": "", "services": "", "search": "", "states": ""}
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.binsons.com/locations/{}"
        store_url = store_url.format(
            poi["Name"]
            .replace(" ", "-")
            .replace(",", "")
            .replace(".", "")
            .replace("(", "")
            .replace(")", "")
            .replace("&", "and")
        )
        if "St-Mary-Mercy-Hospital-Livonia" in store_url:
            store_url = store_url.replace("St-Mary-Mercy-Hospital-Livonia", "St-Mary")
        if store_url == "https://www.binsons.com/locations/St-Joseph-Mercy-Oakland":
            store_url = "https://www.binsons.com/locations/st-joseph-mercy"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["Name"]
        raw_adr = loc_dom.xpath('//p[@class="location-address my-1"]/text()')
        street_address = raw_adr[0]
        city = raw_adr[-1].split(", ")[0]
        state = raw_adr[-1].split(", ")[-1].split()[0]
        zip_code = raw_adr[-1].split(", ")[-1].split()[-1]
        store_number = poi["id"]
        phone = loc_dom.xpath('//p[@class="location-phone-main my-1"]/text()')
        phone = phone[-1].strip() if phone else "<MISSING>"
        latitude = poi["Lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location-hours-list"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
