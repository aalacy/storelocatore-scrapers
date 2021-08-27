# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tedscafe.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

data_raw = [
    ("action", "jet_engine_ajax"),
    ("handler", "get_listing"),
    ("page", "1"),
    ("listing_type", "elementor"),
    ("isEditMode", "false"),
    ("addedPostCSS[]", "5868"),
    ("addedPostCSS[]", "5868"),
    ("addedPostCSS[]", "5868"),
]


def get_latlng(lat_lng_href):
    if "z/data" in lat_lng_href:
        lat_lng = lat_lng_href.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in lat_lng_href:
        lat_lng = lat_lng_href.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://tedscafe.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    categories = search_sel.xpath(
        '//section[.//div[@data-lazy-load]]//div[@class="elementor-widget-wrap"]/div'
    )

    for category in categories:
        post_id = (
            category.xpath(".//div[@data-lazy-load]/@data-lazy-load")[0]
            .split('post_id":')[1]
            .split(",")[0]
            .strip()
        )
        queried_id = (
            category.xpath(".//div[@data-lazy-load]/@data-lazy-load")[0]
            .split('queried_id":"')[1]
            .split(",")[0]
            .split('"}"')[0]
            .strip()
        )
        element_id = category.xpath("./@data-id")[0].strip()

        data = data_raw + [
            ("post_id", post_id),
            ("queried_id", queried_id),
            ("element_id", element_id),
        ]

        api_res = session.post(
            "https://tedscafe.com/wp-admin/admin-ajax.php", headers=headers, data=data
        )
        json_res = json.loads(api_res.text)
        html = json_res["data"]["html"].strip('" ').strip()

        html_sel = lxml.html.fromstring(html)
        store_list = html_sel.xpath('//div[contains(@class,"jet-listing-grid__item ")]')

        for store in store_list:
            page_url = store.xpath('.//a[contains(@href,"teds-locations")]/@href')[0]
            log.info(page_url)
            locator_domain = website
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)
            location_name = "".join(store_sel.xpath("//title//text()")).strip()

            address_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@data-element_type="column" and ./div/div/div[@data-widget_type="button.default"]//a[contains(@href,"maps")]]//text()'
                        )
                    ],
                )
            )

            street_address = address_info[0].strip(",. ").strip()
            city = address_info[1].strip(",. ").strip()
            state = address_info[-2].strip(",. ").strip()
            zip = address_info[-1].strip(",. ").strip()
            country_code = "US"
            store_number = "<MISSING>"
            number = "".join(store_sel.xpath('//a[contains(@href,"Id=")]/@href'))
            if number:
                store_number = number.split("Id=")[1].strip()
            phone = "".join(
                store_sel.xpath('//a[contains(@href,"tel:")]//text()')
            ).strip()

            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in (
                            store_sel.xpath(
                                '//div[@data-widget_type="heading.default" and .//h6//text()="Hours"]/following-sibling::div[.//h4]//text()'
                            )
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours)

            lat_lng_href = "".join(store_sel.xpath('//a[contains(@href,"maps")]/@href'))

            latitude, longitude = get_latlng(lat_lng_href)

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
