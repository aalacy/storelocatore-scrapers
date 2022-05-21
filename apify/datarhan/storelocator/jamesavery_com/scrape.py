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
    start_url = "https://www.jamesavery.com/store_locations?utf8=%E2%9C%93&distance=50&address={}&store_type%5B%5D=retail&authenticity_token=yEwudnl2zo%2FdiLBCZIncYa3relP0t3%2FZPLiT4xG8SaJbVKaPckX7qzA1x6Ve%2F1uMa2N2xOUCG0%2FlPJcccmfIoA%3D%3D"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=40
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//li[@itemtype="http://schema.org/Place"]')

        for poi_html in all_locations:
            page_url = poi_html.xpath('.//h3[@itemprop="name"]/a/@href')
            page_url = urljoin(start_url, page_url[0]) if page_url else ""
            location_name = poi_html.xpath('.//h3[@itemprop="name"]/a/text()')
            location_name = location_name[0] if location_name else ""
            raw_address = poi_html.xpath(
                './/p[@class="store-locations__address"]/text()'
            )
            raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            state = addr.state
            city = addr.city
            zip_code = addr.postcode
            country_code = addr.country
            phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else ""
            geo = (
                poi_html.xpath('.//a[@itemprop="map"]/@href')[0]
                .split("=")[1]
                .split("&")[0]
                .split("%2C")
            )
            latitude = geo[0]
            longitude = geo[1]

            loc_response = session.get(page_url, headers=hdr)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath('//ul[@class="store-locations__hours"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()]) if hoo else ""

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
                hours_of_operation=hoo,
                raw_address=raw_address,
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
