# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wolseleyinc.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "app.mapply.net",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("api_key", "mapply.4f48f5aa0cf76c480f956d34d1292728"),)


def fetch_data():
    # Your scraper here
    search_url = "https://www.wolseleyinc.ca/locations.html"
    with SgRequests() as session:
        stores_req = session.post(
            "https://app.mapply.net/front-end/iframe.php",
            params=params,
            headers=headers,
        )
        stores = stores_req.text.split("markersCoords.push(")
        for index in range(1, len(stores)):
            store_data = stores[index].split(");")[0].strip()
            latitude = store_data.split("lat:")[1].strip().split(",")[0].strip()
            longitude = store_data.split("lng:")[1].strip().split(",")[0].strip()

            store_number = store_data.split("id:")[1].strip().split(",")[0].strip()
            if latitude == "data.you.lat":
                break

            API_url = (
                "https://app.mapply.net/front-end//get_store_info.php?api_key=mapply.4f48f5aa0cf76c480f956d34d1292728&data=detailed&store_id="
                + store_number
            )
            page_url = search_url
            locator_domain = website
            log.info(f"Pulling data for store ID: {store_number}")
            store_req = session.get(API_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.json()["data"])

            location_name = "".join(
                store_sel.xpath('//span[@class="name"]/text()')
            ).strip()

            street_address = "".join(
                store_sel.xpath('//span[@class="address"]/text()')
            ).strip()
            address_2 = "".join(
                store_sel.xpath('//span[@class="address2"]/text()')
            ).strip()
            if len(address_2) > 0:
                street_address = street_address + ", " + address_2

            city = "".join(store_sel.xpath('//span[@class="city"]/text()')).strip()
            state = "".join(
                store_sel.xpath('//span[@class="prov_state"]/text()')
            ).strip()
            zip = "".join(store_sel.xpath('//span[@class="postal_zip"]/text()')).strip()

            country_code = "".join(
                store_sel.xpath('//span[@class="country"]/text()')
            ).strip()

            phone = "".join(store_sel.xpath('//span[@class="phone"]//text()')).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath('//span[@class="hours"]/text()')
            hours_list = []
            for hour in hours:
                if (
                    len("".join(hour).strip()) > 0
                    and not (
                        "".join(hour)
                        .strip()
                        .replace("-", "")
                        .strip()
                        .replace(" ", "")
                        .strip()
                        .isdigit()
                    )
                    and "TEXTING NOW AVAILABLE" not in "".join(hour).strip()
                    and "Plumbing" not in "".join(hour).strip()
                    and "HVAC" not in "".join(hour).strip()
                ):
                    hours_list.append("".join(hour).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
                .split("; Covid-19 Update")[0]
                .strip()
                .split("Curbside")[0]
                .strip()
                .split("curbside")[0]
                .strip()
                .replace("Appointments recommended", "")
                .strip()
                .split("; Emergency Call")[0]
                .strip()
            )

            if (
                "Store hours vary subject to daily flight schedule. Please contact the store directly."
                in hours_of_operation
            ):
                hours_of_operation = "<MISSING>"

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
