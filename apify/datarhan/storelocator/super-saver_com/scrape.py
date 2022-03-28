import re
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    scraped_items = []
    session = SgRequests()
    start_url = "https://www2.super-saver.com/StoreLocator/Search/?ZipCode={}&miles=500"
    domain = "super-saver.com"
    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@id="StoreLocator"]//td/a/@href')
        for store_url in list(set(all_locations)):
            store_url = store_url.replace("_Detail_S.las", "/")
            if store_url in scraped_items:
                continue
            scraped_items.append(store_url)
            loc_response = session.get(store_url, headers=hdr)
            if loc_response.status_code != 200:
                continue
            loc_dom = etree.HTML(loc_response.text)

            location_name = "<MISSING>"
            raw_address = loc_dom.xpath('//p[@class="Address"]/text()')
            raw_address = [
                " ".join([s.strip() for s in e.strip().split()])
                for e in raw_address
                if e.strip()
            ]
            street_address = raw_address[0].strip()
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = store_url.split("L=")[-1].split("&")[0]
            phone = loc_dom.xpath('//p[@class="PhoneNumber"]/a/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = re.findall(r"initializeMap\((.+?)\);", loc_response.text)[0][
                1:-1
            ].split(",")
            latitude = geo[0][:-1]
            latitude = latitude if latitude.strip() else "<MISSING>"
            longitude = geo[1][1:]
            longitude = longitude if longitude.strip() else "<MISSING>"
            hoo = loc_dom.xpath(
                '//dt[contains(text(), "Hours of Operation:")]/following-sibling::dd/text()'
            )
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
