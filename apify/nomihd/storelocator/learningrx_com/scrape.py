# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "learningrx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.learningrx.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.learningrx.com"
    api_url = "https://www.learningrx.com/locations/?CallAjax=GetLocations"
    api_res = session.post(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:

        page_url = base + store["Path"]
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        store_number = store["FranchiseLocationID"]
        locator_domain = website

        location_name = store["BusinessName"].strip()
        street_address = store["Address1"].strip()
        if "Address2" in store and store["Address2"]:
            street_address = (
                (street_address + ", " + store["Address2"]).strip(", ").strip()
            )

        street_address = street_address.replace(
            ", Mary Savio Medical Plaza, Newtown Square", ""
        ).strip()

        city = store["City"].strip()
        state = store["State"].strip()

        zip = store["ZipCode"].strip()

        country_code = store["Country"]
        phone = store["Phone"]
        location_type = "<MISSING>"

        hours_list = []
        hours_of_operation = "<MISSING>"
        hours = store_sel.xpath('//ul[@class="hours-block"]/li')
        for hour in hours:
            day = "".join(hour.xpath('span[@class="interval"]/text()')).strip()
            time = "".join(hour.xpath("text()")).strip()
            if len(time) <= 0:
                time = "".join(hour.xpath('span[@class="cls"]/text()')).strip()
            hours_list.append(day + ":" + time)

        if len(hours_list) <= 0:
            if store["LocationHours"]:
                hours_info = store["LocationHours"].split("][")
                hours = []

                for hour in hours_info:
                    json_str = "{" + hour.strip("[] ") + "}"
                    json_obj = json.loads(json_str)
                    interval = json_obj["Interval"]

                    if json_obj["Closed"] == "1":
                        hours.append(f"{interval} : CLOSED")
                    else:
                        hours.append(
                            f"{interval} : {json_obj['OpenTime']} - {json_obj['CloseTime']}"
                        )

                    hours_of_operation = "; ".join(hours)

        else:
            hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["Latitude"]
        longitude = store["Longitude"]

        raw_address = "<MISSING>"
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
