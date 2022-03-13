# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.fridays.nl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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
    base = "https://www.fridays.nl/"
    search_url = "https://www.fridays.nl/contact/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="wpb_wrapper" and h2 and p]')

        for _, store in enumerate(stores, 1):

            locator_domain = website
            location_name = "".join(store.xpath("./h2//text()")).strip()
            page_url = base + location_name.lower().split(" ")[-1] + "/"

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath("./p[1]//text()")],
                )
            )
            raw_address = "<MISSING>"
            street_address = store_info[0].strip()

            city = store_info[1].split(" ")[-1].strip()
            state = store_info[1].split(" ")[-2].strip()
            zip = store_info[1].split(" ")[0].strip()

            country_code = "NL"

            store_number = "<MISSING>"

            phone = store_info[-2].strip()
            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in search_sel.xpath(
                            f'//div[text()="Openingstijden {city}"]/..//div[@class="tweecolumns"]//text()'
                        )
                    ],
                )
            )
            hour_list = []
            for i in range(0, 7):
                hour_list.append(f"{hours[i]}: {hours[i+7]}")

            hours_of_operation = "; ".join(hour_list)
            map_link = "".join(store.xpath('.//iframe[contains(@src,"maps")]/@src'))
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
