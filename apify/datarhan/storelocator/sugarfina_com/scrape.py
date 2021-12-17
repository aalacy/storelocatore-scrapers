from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    scraped_urls = []
    session = SgRequests(proxy_country="us")
    start_url = "https://www.sugarfina.com/rest/V1/storelocator/search/"
    domain = "sugarfina.com"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-NewRelic-ID": "VgMGWVJSARADXVJaDwUOUlM=",
        "Listrak-Listening": "1",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for code in all_codes:
        params = {
            "searchCriteria[filter_groups][0][filters][0][field]": "lat",
            "searchCriteria[filter_groups][0][filters][0][value]": "",
            "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][1][field]": "lng",
            "searchCriteria[filter_groups][0][filters][1][value]": "",
            "searchCriteria[filter_groups][0][filters][1][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][2][field]": "country_id",
            "searchCriteria[filter_groups][0][filters][2][value]": "US",
            "searchCriteria[filter_groups][0][filters][2][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][3][field]": "store_id",
            "searchCriteria[filter_groups][0][filters][3][value]": "1",
            "searchCriteria[filter_groups][0][filters][3][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][4][field]": "region_id",
            "searchCriteria[filter_groups][0][filters][4][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][5][field]": "region",
            "searchCriteria[filter_groups][0][filters][5][value]": code,
            "searchCriteria[filter_groups][0][filters][5][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][6][field]": "distance",
            "searchCriteria[filter_groups][0][filters][6][value]": "50",
            "searchCriteria[filter_groups][0][filters][6][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][7][field]": "onlyLocation",
            "searchCriteria[filter_groups][0][filters][7][value]": "0",
            "searchCriteria[filter_groups][0][filters][7][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][8][field]": "store_type",
            "searchCriteria[filter_groups][0][filters][8][value]": "",
            "searchCriteria[filter_groups][0][filters][8][condition_type]": "eq",
            "searchCriteria[current_page]": "1",
            "searchCriteria[page_size]": "9",
        }

        data = session.get(start_url, headers=hdr, params=params)
        status = data.status_code
        counter = 0
        while status != 200:
            session = SgRequests(proxy_country="us")
            data = session.get(start_url, headers=hdr, params=params)
            status = data.status_code
            counter += 1
            if counter == 10:
                continue
        data = data.json()
        all_locations = data["items"]
        total_pages = data["total_count"] // 9 + 1
        if total_pages > 1:
            for p in range(2, total_pages):
                params["searchCriteria[current_page]"] = str(p)
                data = session.get(start_url, headers=hdr, params=params).json()
                all_locations += data["items"]
        for poi in all_locations:
            store_url = poi.get("store_details_link")
            if store_url:
                if store_url in scraped_urls:
                    continue
                scraped_urls.append(store_url)
                hdr = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0"
                }
                loc_response = session.get(store_url, headers=hdr)
                loc_dom = etree.HTML(loc_response.text)
            else:
                loc_dom = "<MISSING>"

            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["name"]
            location_name = location_name.strip() if location_name else "<MISSING>"
            street_address = poi["street"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"].strip()
            city = city if city else "<MISSING>"
            state = poi.get("region")
            state = state if state else "<MISSING>"
            zip_code = poi["postal_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country_id"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi.get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = poi["store_type"]
            latitude = poi["lat"]
            longitude = poi["lng"]
            hoo = []

            if store_url != "<MISSING>":
                hoo = loc_dom.xpath('//div[@class="store-timing"]/p//text()')
                hoo = [e.strip() for e in hoo if e.strip()]
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
