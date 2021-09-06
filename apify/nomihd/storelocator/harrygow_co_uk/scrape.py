# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "harrygow.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.harrygow.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.harrygow.co.uk/contact/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    api_headers = {
        "authority": "www.harrygow.co.uk",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "*/*",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }

    API_URL = "https://www.harrygow.co.uk/Umbraco/Api/ShopApi/GetAllShops"
    api_req = session.get(API_URL, headers=api_headers)
    stores = api_req.json()

    for store in stores:
        if store["IsCoopStore"] is True:
            continue

        page_url = search_url
        location_name = "Harry Gow " + store["Name"]
        location_type = "<MISSING>"
        locator_domain = website

        street_address = store["AddressLine1"]
        if (
            "AddressLine2" in store
            and store["AddressLine2"] is not None
            and len(store["AddressLine2"]) > 0
        ):
            street_address = street_address + ", " + store["AddressLine2"]

        street_address = street_address.replace(
            "(within Co-op supermarket),", ""
        ).strip()
        city = store["City"]
        state = store["Region"]
        zip = store["PostalCode"]

        country_code = "GB"
        store_number = store["Id"]

        phone = "".join(
            stores_sel.xpath(
                f'//div[@id="js-shopDetail-{store_number}"]//div[@class="contact-map-selected__right-content"]/p[2]/text()'
            )
        ).strip()
        hours = stores_sel.xpath(
            f'//div[@id="js-shopDetail-{store_number}"]//table[@class="contact-map-selected__table"]//tr'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latlng = store["Coordinates"]
        latitude = latlng.split(",")[0].strip()
        longitude = latlng.split(",")[-1].strip()

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
