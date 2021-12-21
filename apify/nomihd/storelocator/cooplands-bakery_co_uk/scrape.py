# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cooplands-bakery.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "cooplands-bakery.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "origin": "https://cooplands-bakery.co.uk",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://cooplands-bakery.co.uk/locations",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {
    "searchzip": "United Kingdom, country, United Kingdom",
    "task": "search",
    "radius": "-1",
    "option": "com_mymaplocations",
    "limit": "0",
    "component": "com_mymaplocations",
    "Itemid": "227",
    "zoom": "9",
    "geo": "",
    "limitstart": "0",
    "latitude": "54.7023545",
    "longitude": "-3.2765753",
}


def fetch_data():
    # Your scraper here
    base = "https://cooplands-bakery.co.uk"
    search_url = "https://cooplands-bakery.co.uk/locations"

    with SgRequests() as session:

        search_res = session.post(search_url, headers=headers, data=data)

        json_str = search_res.text.split("var promise=")[1].split("};")[0] + "}"

        json_res = json.loads(json_str)

        stores = json_res["features"]

        for no, store in enumerate(stores[1:], 1):  # Skip the very first

            locator_domain = website

            location_name = store["properties"]["name"]
            location_type = "<MISSING>"

            page_url = base + store["properties"]["url"]
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            address_html = store["properties"]["fulladdress"]
            address_sel = lxml.html.fromstring(address_html)

            raw_address = (
                " ".join(address_sel.xpath('//*[@class="locationaddress"]/text()'))
                .strip()
                .split(",")
            )

            street_address = ", ".join(raw_address[:-2]).strip()
            if street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = raw_address[-2]

            state = "<MISSING>"

            zip = raw_address[-1]

            country_code = "GB"

            phone = "".join(address_sel.xpath('.//*[contains(@href,"tel:")]/text()'))

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//*[@class="mml-calendar"]/..//text()'
                        )
                    ],
                )
            )

            hours_of_operation = (
                "; ".join(hours)
                .replace("day;", "day:")
                .replace("Fri;", "Fri:")
                .replace("Sat;", "Sat:")
                .replace("Sun;", "Sun:")
                .replace("Thurs;", "Thurs:")
                .replace(":;", ":")
                .replace("\n", "; ")
            )

            store_number = store["id"]

            latitude, longitude = (
                store["geometry"]["coordinates"][0],
                store["geometry"]["coordinates"][1],
            )

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
                raw_address=", ".join(raw_address).strip(),
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
