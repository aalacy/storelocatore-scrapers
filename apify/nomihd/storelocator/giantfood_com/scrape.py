from sgrequests import SgRequests, SgRequestError
import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "giantfood.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(proxy_country="us", dont_retry_status_codes=([404]))
headers = {
    "authority": "giantfood.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://giantfood.com/store-locator",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    store_types = ["GROCERY", "GAS_STATION"]

    for s in store_types:
        locations_resp = session.get(
            "https://giantfood.com/apis/store-locator/locator/v1/stores/GNTL?storeType="
            + s.strip()
            + "&maxDistance=10000&details=true",
            headers=headers,
        )

        locations = json.loads(locations_resp.text)["stores"]

        for loc in locations:
            location_name = loc["name"]
            street_address = loc["address1"]
            if len(loc["address2"]) > 0:
                street_address = street_address + ", " + loc["address2"]

            city = loc["city"]
            state = loc["state"]
            zip = loc["zip"]
            store_number = loc["storeNo"]
            location_type = loc["storeType"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]

            store_url = "https://stores.giantfood.com/" + store_number
            store_resp = session.get(store_url, headers=headers)
            if isinstance(store_resp, SgRequestError):
                continue
            store_sel = lxml.html.fromstring(store_resp.text)
            country_code = "".join(
                store_sel.xpath(
                    '//span[@itemprop="address"]'
                    '//abbr[@itemprop="addressCountry"]/text()'
                )
            ).strip()

            phone = "".join(
                store_sel.xpath(
                    '//div[@class="NAP-info l-container"]'
                    '//span[@itemprop="telephone"]/text()'
                )
            ).strip()
            page_url = store_url
            hours_of_operation = " ".join(
                store_sel.xpath(
                    '//div[@class="StoreDetails-hours--desktop u-hidden-xs"]'
                    "//table/tbody/tr/@content"
                )
            ).strip()
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
