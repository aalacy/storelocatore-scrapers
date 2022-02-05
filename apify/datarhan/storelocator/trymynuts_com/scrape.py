from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.trymynuts.com/retail-locations"
    domain = "trymynuts.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[span[@style="font-weight: bold;"]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//span/text()")[0].strip()
        street_address = (
            poi_html.xpath(".//following-sibling::div[1]/span/text()")[0]
            .split("Monday")[0]
            .strip()
            .split("Sunday")[0]
        )
        raw_address = poi_html.xpath(".//following-sibling::div[2]/span/text()")
        if not raw_address:
            raw_address = poi_html.xpath(".//following-sibling::div[3]/span/text()")
        raw_address = raw_address[0].strip()
        city = raw_address.split(", ")[0]
        state = raw_address.split(", ")[-1].split()[0]
        zip_code = raw_address.split(", ")[-1].split()[1]
        phone = (
            poi_html.xpath(
                './/following-sibling::div[span[contains(text(), "Phone")]]/span/text()'
            )[0]
            .replace("\xa0", "")
            .split("Sunday")[0]
            .split(":")[1]
            .split("Thursday")[0]
            .split(" Sunday")[0]
            .split("Saturday")[0]
            .split("Friday")[0]
            .strip()
        )
        hoo_data = [
            e.strip()
            for e in poi_html.xpath(".//following::*//text()")[:5]
            if e.strip()
        ]
        raw_hoo = []
        for e in hoo_data:
            if ":00 -" in e or "- closed" in e:
                raw_hoo.append(e)
        clean_hoo = []
        for e in raw_hoo:
            e = (
                e.replace(street_address, "")
                .replace(city, "")
                .replace(state, "")
                .replace(zip_code, "")
                .replace(phone, "")
            )
            clean_hoo.append(e)
        hoo = (
            " ".join([e.strip() for e in clean_hoo if e.strip()])
            .replace("Phone: ", "")
            .replace("Mile Marker 8.5", "")
        )
        hoo = " ".join(hoo.split()).replace(" , ", " ")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
