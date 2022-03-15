from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "grouchos.com"
    start_url = "https://www.grouchos.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="btn btn-xs btn-white website"]/@href')
    next_page = dom.xpath('//a[@rel="next"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[@class="btn btn-xs btn-white website"]/@href')
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        name = loc_dom.xpath("//title/text()")
        loc_id = loc_dom.xpath('//div[contains(@id, "contact-form-widget")]/@id')
        if loc_id:
            loc_id = loc_id[0].replace("contact-form-widget-", "")
            loc_response = session.get(
                f"https://impact.locable.com/widgets/contact_form_widgets/{loc_id}"
            )
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath('//h3[@itemprop="name"]/text()')
            if not location_name:
                location_name = name
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//a[@itemprop="address"]/span/text()')
            raw_address = [elem.strip() for elem in raw_address]
            street_address = raw_address[0]
            state = raw_address[-1].split(", ")[-1].split()[0]
            city = raw_address[-1].split(", ")[0]
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            phone = loc_dom.xpath('//a[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            geo = (
                loc_dom.xpath('//a[@itemprop="address"]/@href')[0]
                .split("=")[-1]
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = loc_dom.xpath(
                '//div[@itemprop="openingHours"]//text()'
            )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )
        else:
            location_name = loc_dom.xpath('//div[@class="title"]/text()')[0].strip()
            street_address = loc_dom.xpath('//span[@class="street-address"]/text()')[0]
            raw_data = loc_dom.xpath('//span[@class="locality"]/text()')[0].split(", ")
            state = raw_data[1].split()[0]
            city = raw_data[0]
            zip_code = raw_data[1].split()[1].split()[-1]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
            latitude = ""
            longitude = ""
            hours_of_operation = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
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
