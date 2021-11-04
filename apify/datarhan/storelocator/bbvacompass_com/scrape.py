from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    scraped_urls = []
    domain = "bbvausa.com"
    start_url = "https://apps.pnc.com/locator-api/locator/api/v2/location/?t=1634895538357&latitude={}&longitude={}&radius=100&radiusUnits=mi&branchesOpenNow=false"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.get(start_url.format(lat, lng), headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        for poi in data["locations"]:
            page_url = ""
            location_type = poi["locationType"]["locationTypeDesc"]
            city = poi["address"]["city"]
            if location_type == "BRANCH":
                page_url = f'https://apps.pnc.com/locator/result-details/{poi["externalId"]}/{city.lower().replace(" ", "-")}'
            street_address = poi["address"]["address1"]
            if poi["address"]["address2"]:
                street_address += ", " + poi["address"]["address2"]
            phone = [
                e["contactInfo"]
                for e in poi["contactInfo"]
                if e["contactType"] == "Internal Phone"
            ]
            phone = phone[0] if phone else ""
            hoo = ""
            if page_url:
                if page_url in scraped_urls:
                    continue
                scraped_urls.append(page_url)
                with SgFirefox() as driver:
                    driver.get(page_url)
                    driver.get(page_url)
                    loc_dom = etree.HTML(driver.page_source)
                    hoo = loc_dom.xpath(
                        '//div[@class="hourlyServiceBlock"]/div[1]//div[@id="resultDetailHoursDiv"]//text()'
                    )
                    hoo = [e.strip() for e in hoo if e.strip()]
                    hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["locationName"],
                street_address=street_address,
                city=city,
                state=poi["address"]["state"],
                zip_postal=poi["address"]["zip"],
                country_code="",
                store_number=poi["id"],
                phone=phone,
                location_type=location_type,
                latitude=poi["address"]["latitude"],
                longitude=poi["address"]["longitude"],
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
