from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "jamesavery.com"
    start_url = "https://www.jamesavery.com/store_locations?utf8=%E2%9C%93&distance=any&address={}&store_type%5B%5D=retail&authenticity_token=yEwudnl2zo%2FdiLBCZIncYa3relP0t3%2FZPLiT4xG8SaJbVKaPckX7qzA1x6Ve%2F1uMa2N2xOUCG0%2FlPJcccmfIoA%3D%3D"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=200
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//li[@itemtype="http://schema.org/Place"]')

        for poi_html in all_locations:
            page_url = poi_html.xpath('.//h3[@itemprop="name"]/a/@href')
            page_url = urljoin(start_url, page_url[0]) if page_url else ""
            location_name = poi_html.xpath('.//h3[@itemprop="name"]/a/text()')
            location_name = location_name[0] if location_name else ""
            address_raw = poi_html.xpath('.//span[@itemprop="address"]/text()')[0]
            addr = parse_address_intl(address_raw)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            city = addr.city
            zip_code = addr.postcode
            country_code = addr.country
            phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            geo = (
                poi_html.xpath('.//a[@itemprop="map"]/@href')[0]
                .split("=")[1]
                .split("&")[0]
                .split("%2C")
            )
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = poi_html.xpath('.//div[@class="store"]//text()')
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if "p.m." in elem
            ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else ""
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
