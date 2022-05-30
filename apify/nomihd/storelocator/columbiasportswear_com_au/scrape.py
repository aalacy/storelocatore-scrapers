# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "columbiasportswear.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.columbiasportswear.com.au",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.columbiasportswear.com.au/stores.asp",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("type", "getNearest"),
    ("lat", "-33.8688197"),
    ("lng", "151.2092955"),
    ("rad", "10000"),
    ("term", ""),
)


def fetch_data():
    # Your scraper here

    search_url = "https://www.columbiasportswear.com.au/stores.asp"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(
            "https://www.columbiasportswear.com.au/cc-google-maps.asp",
            headers=headers,
            params=params,
        )
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//markers/marker")
        brand_data = search_res.text.split('isColumbia="')[1:]
        index = 0
        for store in stores:

            page_url = search_url

            locator_domain = website

            location_name = "".join(store.xpath("@name")).strip()

            store_info = (
                "".join(store.xpath("@address"))
                .strip()
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .split("<br>")
            )

            street_address = (
                ", ".join(store_info[:-3])
                .strip()
                .replace("&amp;", "&")
                .strip()
                .replace("&,", "&")
                .strip()
            )

            city = store_info[-3].strip().split(",")[0].strip()
            state = store_info[-3].strip().split(",")[1].strip()
            zip = store_info[-3].strip().split(",")[2].strip()

            country_code = "AU"

            store_number = "".join(store.xpath("@id")).strip()

            phone = store_info[-1].strip().replace("Phone:", "").strip()

            location_type = brand_data[index].split('"')[0].strip()
            if location_type == "1":
                location_type = "Columbia Store"
            else:
                location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude, longitude = (
                "".join(store.xpath("@lat")).strip(),
                "".join(store.xpath("@lng")).strip(),
            )
            index = index + 1
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
