from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.xpresspa.com/Articles.asp?ID=262"
    domain = "xpresspa.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    closed_locations = dom.xpath("//h4/following-sibling::div[@id][1]/div/ul/li")
    for poi_html in closed_locations:
        location_name = poi_html.xpath(".//a/b/text()")[0]
        loc_id = poi_html.xpath(".//a/@href")[0]
        location_type = "Temporarily Closed"
        street_address = location_name + ", " + poi_html.xpath("text()")[0].strip()
        raw_address = (
            dom.xpath(
                '//div[descendant::a[contains(@href, "{}")]]/preceding-sibling::h4[1]//text()'.format(
                    loc_id
                )
            )[0]
            .replace("Europe", "")
            .replace("-", ",")
            .strip()
        )
        raw_address = street_address + ", " + raw_address
        addr = parse_address_intl(raw_address)
        raw_data = [e.strip() for e in poi_html.xpath(".//text()") if e.strip()]
        phone = [e.replace("Tel:", "").strip() for e in raw_data if "Tel:" in e]
        phone = phone[0] if phone else ""
        hoo = [e.replace("Hours:", "").strip() for e in raw_data if "Hours:" in e]
        hoo = hoo[0] if hoo else ""
        city = addr.city
        if city == "Europe":
            city = ""
        if city and len(city) == 3:
            city = ""
        country_code = addr.country
        if country_code and "Raleigh" in country_code:
            country_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal="",
            country_code="",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

        yield item

    all_locations = dom.xpath('//div[h4[@class="location_state-city"]]')
    for l_html in all_locations:
        all_subs = l_html.xpath('.//div[@class="panel panel-default"]')
        for poi_html in all_subs:
            location_name = poi_html.xpath(".//h5/a/text()")
            location_name = location_name[0].strip()
            state = l_html.xpath(".//h4/text()")[0].split(" - ")[0]
            city = l_html.xpath(".//h4/text()")[0].split(" - ")[-1]
            street_address = l_html.xpath('.//p[@class="location_airport"]/text()')[
                0
            ].strip()
            street_address += ", " + location_name
            phone = poi_html.xpath(
                './/dt[contains(text(), "Telephone")]/following-sibling::dd/text()'
            )
            phone = phone[0].strip() if phone else ""
            if not phone:
                phone = (
                    poi_html.xpath('.//div[@class="card card-body"]/text()')[1]
                    .split(":")[-1]
                    .strip()
                )
            hoo = poi_html.xpath(
                './/dt[contains(text(), "Hours")]/following-sibling::dd/text()'
            )
            if not hoo:
                hoo = [
                    e.replace("Hours: ", "").strip()
                    for e in poi_html.xpath('.//div[@class="card card-body"]/text()')
                    if "Hours" in e
                ]
            hoo = hoo[0] if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal="",
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
