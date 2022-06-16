# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser
import lxml.html

website = "greenp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "parking.greenp.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "application/json",
    "x-requested-with": "XMLHttpRequest",
    "x-request": "JSON",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://parking.greenp.com/find-parking/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("api_key", "eedeab41c581e6883cd4eb349fdea8329dc450479b7f686dff292b5bf2de6f5b"),
)


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404]), verify_ssl=False) as session:
        stores_req = session.get(
            "https://parking.greenp.com/api/carparks/", headers=headers, params=params
        )
        stores = json.loads(stores_req.text)["carparks"]

        for store in stores:
            page_url = store["slug"]
            locator_domain = website
            location_name = "Carpark"

            phone = "<MISSING>"
            raw_address = store["address"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            country_code = "CA"
            store_number = store["id"]
            location_name = location_name + " " + str(store_number)
            location_type = store["carpark_type_str"]
            hours_of_operation = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]

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
                raw_address=raw_address,
            )

        search_url = (
            "https://parking.greenp.com/parking-information/off-street-parking/"
        )
        store_res = session.get(search_url, headers=headers)

        store_sel = lxml.html.fromstring(store_res.text)
        page = 2
        while True:
            stores = store_sel.xpath("//article/a")
            if not stores:
                break  # get out of while

            for store in stores:
                page_url = "".join(store.xpath(".//@href"))
                log.info(page_url)
                store_res = session.get(
                    page_url, headers=headers
                )  # update the variable
                store_sel = lxml.html.fromstring(store_res.text)
                location_type = "".join(
                    store_sel.xpath('//p[span/text()="Facility type:"]/text()')
                ).strip()
                location_name = "".join(store_sel.xpath("//title//text()"))
                temp_store_number = (
                    location_name.replace("Carpark", "").strip().split(" ")[0].strip()
                )
                store_number = ""
                for index in range(0, len(temp_store_number)):
                    if temp_store_number[index] != "0":
                        store_number = "".join(temp_store_number[index:]).strip()
                        break

                raw_address = " ".join(
                    store_sel.xpath('//p[span/text()="Address:"]//text()')[1:]
                ).strip()

                if "closing" in raw_address.lower():
                    raw_address = raw_address.split("closing")[0].strip("- ").strip()
                    location_type = "Temporarily Closed"

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode
                country_code = "CA"
                phone = "<MISSING>"

                hours_of_operation = "<MISSING>"
                if "lat:" in store_res.text and "lng:" in store_res.text:
                    latitude, longitude = (
                        store_res.text.split("lat:")[1].split(",")[0].strip(),
                        store_res.text.split("lng:")[1].split("};")[0].strip(),
                    )
                else:
                    latitude, longitude = "<MISSING>", "<MISSING>"

                yield SgRecord(
                    locator_domain=website,
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
                    raw_address=raw_address,
                )
            store_res = session.get(search_url + f"/page/{page}/", headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)
            page += 1


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
