# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "berluti.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    search_url = "https://store.berluti.com/"
    with SgRequests() as session:
        cities_req = session.get(search_url, headers=headers)
        cities_sel = lxml.html.fromstring(cities_req.text)
        cities = cities_sel.xpath(
            '//div[@class="lf-footer-seo__container__grid__group lf-home__bottom-content__seo-footer__container__grid__group"]/ul/li//a'
        )
        for cit in cities:
            stores_req = session.get(
                "https://store.berluti.com" + "".join(cit.xpath("@href")).strip(),
                headers=headers,
            )
            city = "".join(cit.xpath("span/text()")).strip()
            log.info(city)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('.//a[contains(text(),"Go to store")]/@href')
            for store_url in stores:
                page_url = "https://store.berluti.com" + store_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                json_list = store_sel.xpath(
                    '//script[@type="application/ld+json"]/text()'
                )
                for js in json_list:
                    if json.loads(js, strict=False)["@type"] == "LocalBusiness":
                        store_json = json.loads(js, strict=False)
                        locator_domain = website

                        store_number = "<MISSING>"

                        location_type = "<MISSING>"
                        location_name = store_json["name"]

                        street_address = store_json["address"]["streetAddress"]
                        city = store_json["address"]["addressLocality"]
                        state = "<MISSING>"
                        zip = store_json["address"]["postalCode"]

                        country_code = store_json["address"]["addressCountry"]

                        phone = store_json["telephone"].replace("+1", "").strip()

                        hours = store_sel.xpath(
                            '//div[@id="lf-parts-opening-hours-content"]/div'
                        )
                        hours_list = []
                        for hour in hours:
                            day = "".join(hour.xpath("span/text()")).strip()
                            raw_time = (
                                "".join(hour.xpath("div//text()"))
                                .strip()
                                .replace("\n", "")
                                .strip()
                            )
                            if "-" in raw_time:
                                time = (
                                    raw_time.split("-")[0].strip()
                                    + "-"
                                    + raw_time.split("-")[1].strip()
                                )
                            else:
                                time = raw_time
                            hours_list.append(day + ":" + time)

                        hours_of_operation = (
                            "; ".join(hours_list)
                            .strip()
                            .replace("\n", "")
                            .strip()
                            .replace("Today opening hours", "")
                            .strip()
                        )

                        latitude, longitude = (
                            store_json["geo"]["latitude"],
                            store_json["geo"]["longitude"],
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
                        )
                        break


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
