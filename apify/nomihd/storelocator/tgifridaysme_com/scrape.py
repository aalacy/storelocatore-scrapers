# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tgifridaysme.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "tgifridaysme.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://tgifridaysme.com/store-locator/"
    with SgRequests() as session:
        countries_req = session.get(search_url, headers=headers)
        countries_sel = lxml.html.fromstring(countries_req.text)
        countries = countries_sel.xpath('//a[@class="active_country"]/@data-country')
        countries.append("AE")
        for country in countries:
            log.info(country)
            data = {"c": country, "action": "active_country"}

            session.post(
                "https://tgifridaysme.com/wp-content/themes/tgifridays-theme/ajaxRequest.php",
                data=data,
            )
            stores_req = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//li[@class="nearest_store"]')
            latlng_list = (
                stores_req.text.split("var locations = [[")[1]
                .strip()
                .split("]]")[0]
                .strip()
                .split('null,"')
            )
            for index in range(0, len(stores)):

                page_url = "<MISSING>"
                store_number = "".join(stores[index].xpath("@id")).strip()
                log.info(f"pulling info for ID: {store_number}")
                store_data = {"p": store_number, "action": "map_content"}
                store_req = session.post(
                    "https://tgifridaysme.com/wp-content/themes/tgifridays-theme/ajaxRequest.php",
                    data=store_data,
                )
                store_json = store_req.json()
                locator_domain = website

                location_name = "".join(stores[index].xpath(".//text()")).strip()

                add_sel = lxml.html.fromstring(store_json["address"])
                street_address = (
                    ", ".join(add_sel.xpath("//p/text()"))
                    .strip()
                    .replace(",,", ",")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                city = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = country

                phone = (
                    store_json["contact_number"]
                    .split("/")[0]
                    .strip()
                    .split("<br>")[0]
                    .strip()
                )
                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    latlng_list[index + 1]
                    .split(",")[0]
                    .strip()
                    .replace('"', "")
                    .strip(),
                    latlng_list[index + 1]
                    .split(",")[1]
                    .strip()
                    .replace('"', "")
                    .strip(),
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
