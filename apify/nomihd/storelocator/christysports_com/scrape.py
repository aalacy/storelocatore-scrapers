# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "christysports.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def split_fulladdress(address_info):
    street_address = ", ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()

    if not city or us.states.lookup(zip):
        city = city + " " + state
        state = zip
        zip = "<MISSING>"

    if city and state:
        if not us.states.lookup(state):
            city = city + " " + state
            state = "<MISSING>"

    country_code = "US"
    return street_address, city, state, zip, country_code


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
    search_url = "https://www.christysports.com/locations/find-a-store.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//a[contains(@href,"com/store-locations/")]')

        for store in stores:

            store_url = "".join(store.xpath("./@href")).strip()
            log.info(store_url)

            store_res = session.get(store_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locator_domain = website

            location_name = store_sel.xpath(
                '//div[contains(@class,"hero-title")]/h2//text()'
            )
            if len(location_name) > 0:
                location_name = location_name[0]

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//p[contains(strong/text(),"ADDRESS")]//text()'
                        )
                    ],
                )
            )

            full_address = store_info[1:]
            if len(full_address) == 3:
                full_address = store_info[2:]

            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )
            raw_address = "<MISSING>"

            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//p[contains(strong/text(),"PHONE")]//text()'
                        )
                    ],
                )
            )[1].strip()

            page_url = store_url

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//p[contains(strong/text(),"HOURS")]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours[1:])
                .replace(",;", ",")
                .split("Reop")[0]
                .strip()
                .strip(" ,;.")
                .strip()
                .replace("HOURS;", "")
                .strip()
                .split("; THANKSGIVING")[0]
                .strip()
                .split("; Thanksgiving")[0]
                .strip()
                .replace(".; During the season.", "")
                .strip()
                .split("; 12/24")[0]
                .strip()
            )

            if (
                "Closed for season".upper() in hours_of_operation.upper()
                or "Closed for seaon" in hours_of_operation
            ):
                location_type = "Temporarily Closed"
            store_number = (
                "".join(
                    store_sel.xpath(
                        '//div[@id="maincontent"]//div[@class="page-designer chromeless "]/@id'
                    )
                )
                .split("-")[-1]
                .strip()
            )

            map_link = "".join(
                store_sel.xpath('//p[contains(strong/text(),"ADDRESS")]//@href')
            ).strip()

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
