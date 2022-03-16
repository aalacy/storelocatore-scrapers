from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "schmizzapublichouse.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    scraped_urls = []
    start_url = "https://schmizzapublichouse.com/modules/multilocation/?near_location={}&threshold=4000&geocoder_region=&distance_unit=miles&limit=20&services__in=&language_code=en-us&published=1&within_business=true"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for code in all_codes:
        data = session.get(start_url.format(code), headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        for poi in data["objects"]:
            page_url = "https://" + poi["location_url"]
            if page_url in scraped_urls:
                continue
            scraped_urls.append(page_url)
            loc_response = session.get(page_url, headers=hdr)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath('//div[@class="hours-box"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name="",
                street_address=poi["street"],
                city=poi["city"],
                state=poi["state_name"],
                zip_postal=poi["postal_code"],
                country_code=poi["country"],
                store_number=poi["id"],
                phone=poi["phonemap"]["phone"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lon"],
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
