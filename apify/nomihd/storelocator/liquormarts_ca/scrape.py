# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
import datetime

website = "liquormarts.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.liquormarts.ca",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.kellysroastbeef.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.kellysroastbeef.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.liquormarts.ca/liquormarts"
    search_res = session.get(search_url, headers=headers)
    json_str = search_res.text.split('"markers":')[1].split("],")[0] + "]"

    json_res = json.loads(json_str)

    stores_list = json_res

    for store in stores_list:

        store_sel = lxml.html.fromstring(store["text"])
        page_url = (
            "https://www.liquormarts.ca" + "".join(store_sel.xpath("//a/@href")).strip()
        )

        store_info = list(
            filter(
                str,
                [x.strip() for x in store_sel.xpath("//text()")],
            )
        )

        store_number = page_url.split("/")[-1].strip()
        locator_domain = website

        location_name = store_info[0].strip()
        full_address = store_info[1:-2]

        street_address = " ".join(full_address[:-1])
        city = full_address[-1].split(",")[0].strip()
        state = full_address[-1].split(",")[1].strip()

        zip = full_address[-1].split(",")[2].strip()

        country_code = "CA"
        phone = store_info[-2]
        location_type = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_html_sel = lxml.html.fromstring(store_req.text)
        nid = (
            "".join(store_html_sel.xpath('//link[@rel="shortlink"]/@href'))
            .strip()
            .split("/")[-1]
            .strip()
        )
        today = datetime.date.today()
        next_sunday = str(today + datetime.timedelta(days=today.weekday()))
        last_monday = str(today + datetime.timedelta(days=-today.weekday()))

        hours_req = session.get(
            "https://www.liquormarts.ca/opening_hours/instances?from_date={}&to_date={}&nid={}".format(
                last_monday, next_sunday, nid
            ),
            headers=headers,
        )

        hours = json.loads(hours_req.text)
        hours_list = []
        for hour in hours:
            day = datetime.datetime.strptime(hour["date"], "%Y-%m-%d").strftime("%A")
            time = hour["start_time"] + "-" + hour["end_time"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["latitude"]
        longitude = store["longitude"]

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
