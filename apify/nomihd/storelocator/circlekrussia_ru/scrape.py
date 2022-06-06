# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "circlekrussia.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers1 = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "If-None-Match": 'W/"1640091251"',
}


headers2 = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.circlekrussia.ru",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.circlekrussia.ru/station-search",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("ajax_form", "1"),
    ("_wrapper_format", "drupal_ajax"),
)

data = {
    "phrase": "",
    "form_build_id": "",
    "form_id": "sim_search_form",
    "_triggering_element_name": "op",
    "_triggering_element_value": "\u041F\u043E\u0438\u0441\u043A",
    "_drupal_ajax": "1",
    "ajax_page_state[theme]": "circlek",
    "ajax_page_state[theme_token]": "",
    "ajax_page_state[libraries]": "circlek/ajax-modal-uikit,circlek/global-css,circlek/global-scripts,circlek/main-menu,ck_cookie_complience/cookie_banner,ck_sim_search/ck_sim_search_map,core/drupal.autocomplete,core/drupal.collapse,core/jquery.form,system/base",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.circlekrussia.ru/station-search"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers1)

        search_sel = lxml.html.fromstring(search_res.text)

        form_build_id = "".join(
            search_sel.xpath('//input[@name="form_build_id"]/@value')
        )

        data["form_build_id"] = form_build_id

        # Get countires
        countires = search_sel.xpath('//fieldset[@id="edit-countries"]/div/div')

        for _country in countires:
            country_name = "".join(_country.xpath("./input/@name"))
            log.info(country_name)
            data[country_name] = "1"

            search_res = session.post(
                "https://www.circlekrussia.ru/station-search",
                headers=headers2,
                params=params,
                data=data,
            )
            data.pop(country_name)

            json_res = json.loads(search_res.text)
            stores = []
            for obj in json_res:
                if obj["command"] == "invoke":
                    log.info("found intt")
                    stores = obj["args"][0]["station_results"]
                    break

            for no, store in stores.items():

                locator_domain = website

                location_name = store["/sites/{siteId}"]["name"]

                location_type = store["/sites/{siteId}"]["brand"]

                page_url = "<MISSING>"

                raw_address = "<MISSING>"

                address_info = store["/sites/{siteId}/addresses"]["PHYSICAL"]
                street_address = address_info["street"]

                city = address_info["city"]

                state = address_info["county"]

                zip = address_info["postalCode"]

                country_code = address_info["country"]

                phone = store["/sites/{siteId}/contact-details"]["phones"]
                if phone:
                    phone = phone["WOR"]
                else:
                    phone = "<MISSING>"

                hours = store["/sites/{siteId}/opening-info"]["openingTimes"]

                hours_of_operation = (
                    "; ".join(hours)
                    .replace("day;", "day:")
                    .replace("Fri;", "Fri:")
                    .replace("Sat;", "Sat:")
                    .replace("Sun;", "Sun:")
                    .replace("Thurs;", "Thurs:")
                    .replace(":;", ":")
                )
                if store["/sites/{siteId}/opening-info"]["alwaysOpen"] is True:
                    hours_of_operation = "24 Hours"

                store_number = no

                latitude, longitude = (
                    store["/sites/{siteId}/location"]["lat"],
                    store["/sites/{siteId}/location"]["lng"],
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
                    raw_address=raw_address,
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
