import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    domain = "freewayinsurance.com"
    start_url = "https://locations.freewayinsurance.com/?search={}&latitude=&longitude=&radio=200&time=open-any"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        dom = etree.HTML(response.text)
        all_urls = dom.xpath('//a[@class="c-office-teaser__control"]/@href')
        for url in all_urls:
            if "google" not in url:
                all_locations.append(url)

    for store_url in list(set(all_locations)):
        store_url = urljoin(start_url, store_url)
        store_response = session.get(store_url)
        loc_dom = etree.HTML(store_response.text)
        store_data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "address")]/text()'
        )[0]
        store_data = json.loads(store_data.replace("\n", ""))

        location_name = store_data["name"]
        street_address = store_data["address"]["streetAddress"]
        city = store_data["address"]["addressLocality"]
        city = city if city else SgRecord.MISSING
        state = store_data["address"]["addressRegion"]
        state = state if state else SgRecord.MISSING
        zip_code = store_data["address"]["postalCode"]
        zip_code = zip_code if zip_code else SgRecord.MISSING
        country_code = store_data["address"]["addressCountry"]
        country_code = country_code if country_code else SgRecord.MISSING
        phone = store_data["telephone"]
        phone = phone if phone else SgRecord.MISSING
        if phone == "none":
            phone = SgRecord.MISSING
        location_type = store_data["@type"]
        location_type = location_type if location_type else SgRecord.MISSING
        latitude = store_data["geo"]["latitude"]
        latitude = latitude if latitude else SgRecord.MISSING
        longitude = store_data["geo"]["longitude"]
        longitude = longitude if longitude else SgRecord.MISSING
        hours = []
        hoo = store_data["openingHoursSpecification"]
        for e in hoo:
            day = e["dayOfWeek"]
            if e["opens"] == "closed":
                hours.append(f"{day} closed")
            else:
                opens = e["opens"]
                closes = e["closes"]
                hours.append(f"{day} {opens} - {closes}")
        hours_of_operation = ", ".join(hours) if hours else SgRecord.MISSING

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
