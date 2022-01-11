# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "maxol.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
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
    elif "daddr=" in map_link:
        latitude = map_link.split("daddr=")[1].split(",")[0].strip()
        longitude = map_link.split("daddr=")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "https://stations.maxol.ie/"
    search_url = "https://stations.maxol.ie/index.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath('//li[@class="Directory-listItem"]/a')

        for _state in states:

            state_url = base + "".join(_state.xpath("./@href"))
            log.info(state_url)

            state_res = session.get(state_url, headers=headers)
            state_sel = lxml.html.fromstring(state_res.text)

            cities = state_sel.xpath('//li[@class="Directory-listItem"]/a')
            if not cities:
                cities = ["Temp"]

            for _city in cities:

                if _city == "Temp":
                    stores = state_sel.xpath('//li[@class="Directory-listTeaser"]')
                else:

                    city_url = base + "".join(_city.xpath("./@href"))
                    log.info(city_url)
                    city_res = session.get(city_url, headers=headers)
                    city_sel = lxml.html.fromstring(city_res.text)

                    stores = city_sel.xpath('//li[@class="Directory-listTeaser"]')

                for no, store in enumerate(stores, 1):

                    locator_domain = website

                    page_url = "".join(store.xpath(".//h2/a/@href"))

                    store_number = "<MISSING>"

                    location_name = " ".join(store.xpath(".//h2//text()"))
                    location_type = "<MISSING>"

                    raw_address = "<MISSING>"

                    street_address = " ".join(
                        store.xpath(
                            './/span[@class="Address-field Address-line1"]//text()'
                        )
                    )

                    if street_address is not None:
                        street_address = street_address.replace("Ste", "Suite")
                    city = " ".join(
                        store.xpath(
                            './/span[@class="Address-field Address-city"]//text()'
                        )
                    )

                    state = "<MISSING>"
                    zip = " ".join(
                        store.xpath(
                            './/span[@class="Address-field Address-postalCode"]//text()'
                        )
                    ).strip()

                    country_code = " ".join(
                        store.xpath(
                            './/span[contains(@class,"Address-field Address-country")]//text()'
                        )
                    ).strip()

                    phone = "".join(
                        store.xpath('.//a[contains(@href,"tel")]//text()')
                    ).strip()

                    hours_str = list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store.xpath(
                                    './/div[@class="Teaser-open"]/span/@data-days'
                                )
                            ],
                        )
                    )

                    if hours_str:
                        hours_obj = json.loads(hours_str[0])

                        hour_list = []

                        for hour in hours_obj:
                            day = hour["day"]
                            interval = hour["intervals"]
                            if interval:

                                start = interval[0]["start"]
                                end = interval[0]["end"]

                                hour_list.append(f"{day}: {start} - {end}")
                            else:
                                hour_list.append(f"{day}: CLOSED")

                        hours_of_operation = (
                            "; ".join(hour_list)
                            .replace("day;", "day:")
                            .replace("; -;", " - ")
                            .strip()
                        )
                    else:
                        hours_of_operation = "<MISSING>"

                    map_link = "".join(
                        store.xpath('.//a[@class="c-get-directions-button"]/@href')
                    )

                    log.info(map_link)
                    latitude, longitude = get_latlng(map_link)

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
