# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "homewithmission.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.homewithmission.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "https://homewithmission.com"
    with SgRequests() as session:
        params = (
            ("page", "1"),
            ("perpage", "0"),
            ("withSchema", "true"),
        )

        for index in range(1, 21):
            stores_req = session.get(
                "https://www.homewithmission.com/wp-json/mapsvg/v1/objects/objects_{}/".format(
                    index
                ),
                headers=headers,
                params=params,
            )

            json_data = json.loads(stores_req.text)
            if "objects" in json_data:
                stores = json_data["objects"]
                if isinstance(stores, list):
                    for store in stores:
                        page_url = ""
                        if len(store["link"]) > 0:
                            if "/location" not in store["link"]:
                                page_url = base + "/" + store["link"]
                            else:
                                page_url = base + store["link"]

                        locator_domain = website

                        if len(store["description"]) <= 0:
                            continue

                        desc_sel = lxml.html.fromstring(store["description"])
                        temp_address = desc_sel.xpath(
                            '//div[@class="text-wrapper"]//text()'
                        )
                        add_list = []
                        for temp in temp_address:
                            if len("".join(temp).strip()) > 0:
                                add_list.append("".join(temp).strip())

                        street_address = ", ".join(add_list[:-1]).strip()
                        city = add_list[-1].strip().split(",")[0].strip()
                        state = (
                            add_list[-1]
                            .strip()
                            .split(",")[-1]
                            .strip()
                            .split(" ")[0]
                            .strip()
                        )
                        zip = (
                            add_list[-1]
                            .strip()
                            .split(",")[-1]
                            .strip()
                            .split(" ")[-1]
                            .strip()
                        )
                        country_code = "US"

                        location_name = store["title"]

                        if (
                            location_name
                            == "dvanced Healthcare Services Home Health- Newark"
                        ):
                            location_name = (
                                "Advanced Healthcare Services Home Health- Newark"
                            )

                        phone = "".join(
                            desc_sel.xpath('//div[@class="office-wrapper"]/text()')
                        ).strip()

                        store_number = store["id"]

                        location_type = "<MISSING>"

                        hours_of_operation = "<MISSING>"
                        latitude, longitude = "<MISSING>", "<MISSING>"

                        if len(page_url) > 0:
                            log.info(page_url)
                            loc_res = session.get(page_url, headers=headers)
                            loc_sel = lxml.html.fromstring(loc_res.text)

                            hours_list = []
                            days = loc_sel.xpath(
                                '//div[@class="text-wrapper"]/p[./strong[contains(text(),"Hours of Operation:")]]/following-sibling::p[1]/strong/text()'
                            )
                            time = loc_sel.xpath(
                                '//div[@class="text-wrapper"]/p[./strong[contains(text(),"Hours of Operation:")]]/following-sibling::p[1]/text()'
                            )

                            days_list = []
                            time_list = []
                            for day in days:
                                if len("".join(day).strip()) > 0:
                                    days_list.append("".join(day).strip())

                            for tim in time:
                                if len("".join(tim).strip()) > 0:
                                    time_list.append("".join(tim).strip())

                            for index in range(0, len(days)):
                                hours_list.append(days_list[index] + time_list[index])

                            hours_of_operation = "; ".join(hours_list).strip()
                            map_link = "".join(
                                loc_sel.xpath(
                                    '//iframe[contains(@src,"maps/embed?")]/@src'
                                )
                            )

                            latitude, longitude = get_latlng(map_link)

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
