from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "pmi-parking.com"
    for i in range(1, 300):
        store_number = str(i)
        page_url = (
            f"https://pmi-parking.com/r/parking/view.aspx?record_id={store_number}"
        )
        loc_response = session.get(page_url)
        if "PageNotFoundError" in str(loc_response.url.raw[-1]):
            continue
        loc_dom = etree.HTML(loc_response.text)
        street_address = loc_dom.xpath('//input[contains(@name, "Address")]/@value')[0]
        if street_address == "Not Assigned":
            street_address = ""
        city = loc_dom.xpath('//input[contains(@name, "City")]/@value')[0]
        if city == "City Not Assign":
            if street_address:
                city = ""
            else:
                continue
        state = loc_dom.xpath('//input[contains(@name, "State")]/@value')[0]
        if state in ["Not Assign", "Not Assigned"]:
            continue
        zip_code = loc_dom.xpath('//input[contains(@name, "Zip")]/@value')[0]
        if zip_code in ["ZipCode N", "Not Assig"]:
            continue
        phone = loc_dom.xpath('//input[contains(@name, "Phone")]/@value')[0]
        if phone.lower().strip() == "none":
            phone = ""
        latitude = loc_dom.xpath('//input[contains(@name, "Latitude")]/@value')[0]
        if latitude == "0.000000":
            latitude = ""
        longitude = loc_dom.xpath('//input[contains(@name, "Longitude")]/@value')[0]
        if longitude == "0.000000":
            longitude = ""
        hoo = loc_dom.xpath('//td[h2[contains(text(), "HOURS")]]/p/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name="",
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
