import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests(proxy_country="us", verify_ssl=False)
    domain = "countryfinancial.com"
    start_url = "https://www.countryfinancial.com/services/forms?configNodePath=%2Fcontent%2Fcfin%2Fen%2Fjcr%3Acontent%2FrepLocator&cfLang=en&repSearchType=queryByLocation&latitude=&longitude=&repSearchValue={}"
    scraped_urls = []

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for code in all_codes:
        try:
            response = session.get(
                start_url.format(code),
            )
        except Exception:
            continue
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[@itemtype="//schema.org/Organization"]')
        for poi_html in all_poi_html:
            store_url = poi_html.xpath('.//a[@itemprop="url"]/@href')[0]
            print(store_url)
            if store_url in scraped_urls:
                continue
            loc_response = session.get(store_url)
            scraped_urls.append(store_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
            if not poi:
                continue
            poi = demjson.decode(poi[0].replace("\n", ""))

            data = loc_dom.xpath('//script[contains(text(), "JSContext")]/text()')[0]
            data = re.findall("JSContext =(.+);", data)[0]
            data = demjson.decode(data)

            location_name = poi[0]["name"].replace("&#39;", "'")
            street_address = data["profile"]["address"]["street"]
            suit = data["profile"]["address"].get("suite")
            if suit:
                street_address += " " + suit
            city = poi[0]["address"]["addressLocality"]
            city = city.replace("&#39;", "'") if city else ""
            state = poi[0]["address"]["addressRegion"]
            zip_code = poi[0]["address"]["postalCode"]
            phone = poi[0]["contactPoint"][0]["telephone"]
            location_type = poi[0]["@type"]
            latitude = data["profile"]["latlng"]
            latitude = latitude[0] if latitude else ""
            longitude = data["profile"]["latlng"]
            longitude = longitude[1] if longitude else ""

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="",
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
