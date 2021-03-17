# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import us
from sgselenium import SgChrome

website = "brandsmartusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.brandsmartusa.com/arc/static/storelocator?format=json&isMember=false"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(
        json.loads(stores_req.text)["payload"]["page"]["segmentsMap"]["middle"][0][
            "columnContentItemMap"
        ]["1"]["htmlContent"]["content"]
    )
    stores = stores_sel.xpath('//a[contains(@href,"/store")]/@href')
    for store_slug in stores:
        page_url = "https://www.brandsmartusa.com" + store_slug
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(
            "https://www.brandsmartusa.com/arc/static"
            + store_slug
            + "?format=json&isMember=false",
            headers=headers,
        )

        sections = json.loads(store_req.text)["payload"]["page"]["segmentsMap"][
            "middle"
        ]

        store_sel = ""
        map_sel = ""
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zip = ""
        phone = ""
        hours_of_operation = ""
        latitude = ""
        longitude = ""
        for section in sections:
            current_section = section["columnContentItemMap"]["1"]
            store_sel = lxml.html.fromstring(current_section["htmlContent"]["content"])

            if len(latitude) <= 0:
                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
                ).strip()

                if len(map_link) > 0:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

            if len(location_name) <= 0:
                location_name = "".join(
                    store_sel.xpath('//h1[@itemprop="name"]/span/text()')
                ).strip()
                if len(location_name) <= 0:
                    location_name = (
                        "".join(
                            store_sel.xpath(
                                '//div[@id="info"]/div[1]/center/h2/strong[1]/text()'
                            )
                        )
                        .strip()
                        .replace("Info", "")
                        .strip()
                    )
                    if len(location_name) <= 0:
                        location_name = (
                            "".join(
                                store_sel.xpath(
                                    '//div[@id="info"]/div[1]/h2/strong[1]/text()'
                                )
                            )
                            .strip()
                            .replace("Info", "")
                            .strip()
                        )
            if len(street_address) <= 0:
                street_address = "".join(
                    store_sel.xpath(
                        '//span[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
                    )
                ).strip()
                if len(street_address) <= 0:
                    address = store_sel.xpath('//div[@id="info"]/div[1]/span[1]/text()')
                    if len(address) > 0:
                        add_list = []
                        for add in address:
                            if len("".join(add).strip()) > 0:
                                add_list.append("".join(add).strip())

                        street_address = add_list[1].strip()
                        city_state_zip = add_list[-2].strip()
                        city = city_state_zip.split(",")[0].strip()
                        state = (
                            city_state_zip.split(",")[1].strip().split(" ")[0].strip()
                        )
                        zip = (
                            city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
                        )
                        phone = add_list[-1].strip().replace("Call or Text", "").strip()
                else:
                    city = "".join(
                        store_sel.xpath(
                            '//span[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
                        )
                    ).strip()
                    state = "".join(
                        store_sel.xpath(
                            '//span[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
                        )
                    ).strip()
                    zip = "".join(
                        store_sel.xpath(
                            '//span[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
                        )
                    ).strip()

            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath('//span[@itemprop="telephone"]/text()')
                ).strip()

            if len(hours_of_operation) <= 0:
                hours = store_sel.xpath("//table[1]//tr")
                if len(hours) > 1:
                    hours_list = []
                    for hour in hours:
                        day = (
                            "".join(hour.xpath("td[1]/span/text()"))
                            .strip()
                            .replace("-", ":")
                            .strip()
                        )
                        time = "".join(hour.xpath("td[2]/span/text()")).strip()
                        if len(day) > 0:
                            if (
                                "Monday" in day
                                or "Tuesday" in day
                                or "Wednesday" in day
                                or "Thursday" in day
                                or "Friday" in day
                                or "Saturday" in day
                                or "Sunday" in day
                            ):
                                hours_list.append(day + time)

                    hours_of_operation = (
                        "; ".join(hours_list)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                    )
                else:
                    if "Store Hours" in store_sel.xpath(
                        '//div[@id="info"]/div[@class="col-sm-4"]/center/h2/strong/text()'
                    ):
                        hours = store_sel.xpath(
                            '//div[@id="info"]/div[@class="col-sm-4"]/div'
                        )
                        hours_list = []
                        for hour in hours:
                            day = (
                                "".join(hour.xpath("span[1]/text()"))
                                .strip()
                                .replace("-", ":")
                                .strip()
                            )
                            time = "".join(hour.xpath("span[2]/text()")).strip()
                            if len(day) > 0:
                                if (
                                    "Monday" in day
                                    or "Tuesday" in day
                                    or "Wednesday" in day
                                    or "Thursday" in day
                                    or "Friday" in day
                                    or "Saturday" in day
                                    or "Sunday" in day
                                ):
                                    hours_list.append(day + time)

                        hours_of_operation = (
                            "; ".join(hours_list)
                            .strip()
                            .encode("ascii", "replace")
                            .decode("utf-8")
                            .replace("?", "-")
                            .strip()
                        )
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = "<MISSING>"

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
