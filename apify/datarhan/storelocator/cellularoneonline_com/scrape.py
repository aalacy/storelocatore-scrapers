from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "cellularoneonline.com"
    start_url = "https://mycellularone.com/locations/"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//article[contains(@class, "locations")]')

    post_url = "https://mycellularone.com/wp-admin/admin-ajax.php"
    for poi_html in all_locations:
        store_number = poi_html.xpath("@data-post-id")[0]
        frm = {"action": "locations_location_detail", "location_id": str(store_number)}

        hdr = {
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://mycellularone.com",
            "referer": "https://mycellularone.com/locations/",
            "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        loc_response = session.post(post_url, data=frm, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        location_name = poi_html.xpath('.//div[@class="location-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[@class="nmld-detail-item for-address"]/text()'
        )
        raw_address = (
            " ".join(
                ", ".join([e.strip() for e in raw_address if e.strip()])
                .replace(",,", ",")
                .split()
            )
            .replace("Cellular One Store,", "")
            .strip()
        )

        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        latitude = poi_html.xpath("@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="nmld-detail-item for-hours"]//text()')
        hoo = [elem.strip() for elem in hoo]
        hours_of_operation = (
            " ".join(hoo).replace("Lunch Hours Vary", "") if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number=store_number,
            phone="",
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
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
