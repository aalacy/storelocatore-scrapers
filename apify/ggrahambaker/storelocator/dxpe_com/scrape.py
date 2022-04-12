import re
import json
from lxml import etree
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    scraped_items = []

    start_url = "https://www.dxpe.com/program/www/index.php/main/submitForm"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=1000,
    )

    for code in all_codes:
        all_locations = []
        frm = {"category": "", "address": code}
        hdr = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        try:
            response = session.post(start_url, data=frm, headers=hdr)
            all_locations = json.loads(response.text)["locations"]
        except:
            continue
        for poi in all_locations:
            store_url = "https://www.dxpe.com/locations/"
            location_name = poi["locationName"]
            location_name = (
                etree.HTML(location_name).xpath("//text()")[0].strip()
                if location_name
                else "<MISSING>"
            )
            street_address = poi["address"]
            street_address = (
                street_address.strip().replace("\n", "")
                if street_address
                else "<MISSING>"
            )
            if len(street_address.strip()) <= 1:
                continue
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state.split(",")[0] if state else "<MISSING>"
            zip_code = poi["zip"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["locationId"]
            phone = poi["phone"]
            phone = phone if phone and len(phone) > 2 else "<MISSING>"
            location_type = poi["locationType"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = "<MISSING>"
            if store_number in scraped_items:
                continue
            scraped_items.append(store_number)

            yield SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
