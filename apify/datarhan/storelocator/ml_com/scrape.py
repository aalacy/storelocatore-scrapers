import json
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ml.com"
    scraped_urls = []
    start_url = "https://fa.ml.com/find-an-advisor/locator/api/InternalSearch"
    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    usr_agent = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    body = '{"Locator":"MER-WM-Offices","PostalCode":"%s","Company":null,"ProfileTypes":"Branch","DoFuzzyNameSearch":0,"SearchRadius":"50"}'

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=50,
    )

    for code in all_codes:
        response = session.post(start_url, data=body % code, headers=hdr)
        if not response.text:
            continue
        data = json.loads(response.text)
        if not data.get("Results"):
            continue
        for poi in data["Results"]:
            store_url = "https:" + poi["XmlData"]["parameters"]["Url"]
            if store_url in scraped_urls:
                continue
            scraped_urls.append(store_url)
            location_name = poi["Company"]
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            city = poi["City"]
            state = poi["Region"]
            zip_code = poi["PostalCode"]
            country_code = poi["Country"]
            store_number = poi["ProfileId"]
            phone = poi["XmlData"]["parameters"].get("LocalNumber")
            latitude = poi["GeoLat"]
            longitude = poi["GeoLon"]
            location_type = poi["ProfileType"]

            store_response = session.get(store_url, headers=usr_agent)
            if store_response.status_code != 200:
                continue
            store_dom = etree.HTML(store_response.text)
            hours_of_operation = ""
            if store_dom:
                hours_of_operation = store_dom.xpath(
                    '//div[@id="more-hours"]//ul/li/text()'
                )
                hours_of_operation = (
                    " ".join(hours_of_operation) if hours_of_operation else ""
                )

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
