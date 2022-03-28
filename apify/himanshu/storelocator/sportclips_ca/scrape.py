from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = SgLogSetup().get_logger("sportclips_ca")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
}


def fetch_data():

    locator_domain = "sportclips.ca"
    country_code = "US"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    with SgRequests() as session:
        stores_req = session.get("https://sportclips.ca/store-locator")
        stores_str = stores_req.text.split("var data = ")[1].split(";")[0].strip()
        json_data = json.loads(stores_str)
        for loc in json_data:
            store_number = loc["id"]
            location_name = loc["SiteName"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            street_address = loc["Address"]
            city = loc["City"]
            state = loc["State"]
            zip = loc["Postal"]
            country_code = "CA"
            page_url = loc["Web"]
            phone = loc["Phone"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            log.info(page_url)
            r_loc = session.get(page_url)
            store_sel = lxml.html.fromstring(r_loc.text)
            hours = store_sel.xpath(
                '//div[@class="wtp-article"][./h2[contains(.//text(),"STORE HOURS")]]/div'
            )
            if len(hours) <= 0:
                hours = store_sel.xpath(
                    '//div[@class="wtp-article"][./h2[contains(.//text(),"STORE HOU")]]/div'
                )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("div[1]//text()")).strip()
                time = "".join(hour.xpath("div[2]//text()")).strip()
                if len(day) > 0 and len(time) > 0:
                    hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
