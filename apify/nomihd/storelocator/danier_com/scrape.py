# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "danier.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "danier.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://danier.com/apps/store-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("markersCoords.push(")[1:-2]
    for store in stores:
        raw_data = store.split(");")[0].strip()
        store_number = raw_data.split("id:")[1].strip().split(",")[0].strip()

        page_url = search_url
        log.info(f"Pulling data for store ID: {store_number}")
        store_req = session.get(
            "https://stores.boldapps.net/front-end/get_store_info.php?shop=danier-canada.myshopify.com&data=detailed&store_id={}".format(
                store_number
            ),
            headers=headers,
        )
        store_sel = lxml.html.fromstring(store_req.json()["data"])

        locator_domain = website

        location_name = "".join(store_sel.xpath("//span[@class='name']/text()")).strip()

        street_address = "".join(
            store_sel.xpath('//span[@class="address"]/text()')
        ).strip()

        add_2 = "".join(store_sel.xpath('//span[@class="address2"]/text()')).strip()
        if len(add_2) > 0:
            street_address = street_address + ", " + add_2

        city = "".join(store_sel.xpath('//span[@class="city"]/text()')).strip()
        state = "".join(store_sel.xpath('//span[@class="prov_state"]/text()')).strip()
        zip = "".join(store_sel.xpath('//span[@class="postal_zip"]/text()')).strip()

        country_code = "".join(
            store_sel.xpath('//span[@class="country"]/text()')
        ).strip()

        phone = "".join(store_sel.xpath('//span[@class="phone"]/text()')).strip()

        location_type = "".join(
            store_sel.xpath('//span[@class="hours"]/span/text()')
        ).strip()
        hours = store_sel.xpath("//span[@class='hours']/text()")
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = raw_data.split("lat:")[1].strip().split(",")[0].strip()
        longitude = raw_data.split("lng:")[1].strip().split(",")[0].strip()

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
