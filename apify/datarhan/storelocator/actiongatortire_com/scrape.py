import re
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.actiongatortire.com/locations/?address%5B0%5D=10001&post%5B0%5D=location&distance=100&units=imperial&per_page=99&lat=40.748421&lng=-73.994152&form=1&action=fs"
    domain = "actiongatortire.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Location")]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/text()')
        if location_name:
            location_name = location_name[0]
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[
                0
            ].strip()
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
            state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
            phone = loc_dom.xpath("//a/@data-tel-number")[0]
            longitude = re.findall(r",Lng:(.+?),", loc_response.text)[0]
            latitude = re.findall(r",Lat:(.+?),", loc_response.text)[0]
            hoo = loc_dom.xpath('//div[@class="store-hours"]/div[1]//text()')
            hoo = " ".join(hoo)

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
                hours_of_operation=hoo,
            )

            yield item
        else:
            more_locations = loc_dom.xpath(
                '//div[contains(@class, "location-content-container__col-group-2")]/div/table//a/@href'
            )
            all_locations += [
                urljoin("https://www.mavistire.com/locations/", url)
                for url in more_locations
            ]
            continue


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
