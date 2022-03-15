from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://quikefoods.com/locations/"
    domain = "quikefoods.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="entry-content"]/p[@style="text-align: center;"]'
    )
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")[0]
        if "/locations/" in store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/strong/text()")
            location_name = location_name[0] if location_name else ""
            raw_address = loc_dom.xpath('//div[@class="entry-content"]/p[1]/text()')
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = ""
            store_number = ""
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            if phone and "#" in phone:
                store_number = phone.split("#")[-1]
                phone = phone.split("Store")[0]
            else:
                store_number = poi_html.xpath("text()")[-1].split("#")[-1]
            location_type = ""
            latitude = ""
            longitude = ""
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!3m")[0]
                .split("!3d")
            )
            latitude = geo[1].split("!")[0]
            longitude = geo[0]
            hours_of_operation = ""
        else:
            location_name = poi_html.xpath(".//a/strong/text()")
            location_name = location_name[0] if location_name else ""
            raw_address = poi_html.xpath("text()")[0].split("(")[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else ""
            state = addr.state
            state = state if state else ""
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else ""
            country_code = addr.country
            country_code = country_code if country_code else ""
            store_number = poi_html.xpath("text()")[0].split()[-1][1:-1]
            phone = "(" + poi_html.xpath("text()")[0].split("(")[1]
            store_number = ""
            if phone and "#" in phone:
                store_number = phone.split("#")[-1]
                phone = phone.split("Store")[0]
            else:
                store_number = poi_html.xpath("text()")[-1].split("#")[-1]
            location_type = ""
            latitude = ""
            longitude = ""
            hours_of_operation = ""
            if "quikefoods" in store_url:
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)
                geo = (
                    loc_dom.xpath("//iframe/@src")[0]
                    .split("!2d")[-1]
                    .split("!3m")[0]
                    .split("!3d")
                )
                latitude = geo[1].split("!")[0]
                longitude = geo[0]
        store_number = store_number.replace(")", "")

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
