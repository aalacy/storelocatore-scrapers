# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bathandbodyworks.com.sa"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    urls = [
        "https://www.bathandbodyworks.com.bh/en/store-finder",
        "https://www.bathandbodyworks.com.eg/en/store-finder",
        "https://www.bathandbodyworks.com.kw/en/store-finder",
        "https://www.bathandbodyworks.ae/en/store-finder",
        "https://www.bathandbodyworks.com.sa/en/store-finder",
        "https://www.bathandbodyworks.com.qa/en/store-finder",
    ]

    with SgRequests() as session:
        for search_url in urls:
            headers = {
                "authority": search_url.split("https://")[1]
                .strip()
                .split("/")[0]
                .strip(),
                "cache-control": "max-age=0",
                "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-user": "?1",
                "sec-fetch-dest": "document",
                "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
            }
            search_res = session.get(
                search_url,
                headers=headers,
            )
            log.info(search_res)
            search_sel = lxml.html.fromstring(search_res.text)

            ID_dict = {}
            title_gloss = search_sel.xpath('//a[contains(@id,"glossary-store-")]')
            for title in title_gloss:
                ID_dict["".join(title.xpath("text()")).strip()] = (
                    "".join(title.xpath("@id"))
                    .strip()
                    .replace("glossary-store-", "")
                    .strip()
                )

            stores = search_sel.xpath(
                '//div[@class="geolocation-common-map-locations"]/div'
            )

            for _, store in enumerate(stores, 1):

                page_url = search_url

                locator_domain = website

                location_name = "".join(
                    store.xpath('.//div[contains(@class,"title")]/span//text()')
                ).strip()

                ajax_params = (("_wrapper_format", "drupal_ajax"),)

                ajax_data = {
                    "js": "true",
                    "_drupal_ajax": "1",
                    "ajax_page_state[theme]": "alshaya_bathbodyworks",
                    "ajax_page_state[theme_token]": "",
                    "ajax_page_state[libraries]": "alshaya_acm_cart_notification/cart_notification_js,alshaya_algolia_react/autocomplete,alshaya_bathbodyworks/global_styles,alshaya_bathbodyworks/ltr_styles,alshaya_dynamic_yield/alshaya_dynamic_yield.product_modal,alshaya_geolocation/places-api.googleplacesapi,alshaya_i18n/language_selection,alshaya_master/common_fixes,alshaya_master/focus_form_error,alshaya_newsletter/newsletter_js,alshaya_search_api/back_to_list,alshaya_seo_transac/gtm_algolia,alshaya_spc/cart_utilities,alshaya_spc/commerce_backend.cart.v2,alshaya_spc/mini_cart,alshaya_stores_finder/store_finder,alshaya_white_label/algolia_search,alshaya_white_label/color_styles,alshaya_white_label/footer_js,alshaya_white_label/global_styles,alshaya_white_label/megamenu_inline_layout,alshaya_white_label/optionlist_menu,alshaya_white_label/plp-add-to-cart,alshaya_white_label/slick_css,alshaya_white_label/store_finder,alshaya_white_label/ucfix,back_to_top/back_to_top_icon,back_to_top/back_to_top_js,clientside_validation_jquery/cv.jquery.ckeditor,clientside_validation_jquery/cv.jquery.ife,clientside_validation_jquery/cv.jquery.validate,cog/lib,core/html5shiv,datadog_js/logger,datalayer/behaviors,dynamic_yield/dynamic_yield.intelligent_tracking,geolocation/geolocation.commonmap,geolocation/geolocation.views.filter.geocoder,system/base,views/views.ajax,views/views.module",
                }
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[contains(@class,"store-address")]//text()'
                            )
                        ],
                    )
                )

                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = (
                    search_url.split("bathandbodyworks.")[1]
                    .strip()
                    .split("/")[0]
                    .strip()
                    .replace("com.", "")
                    .strip()
                )

                store_number = "<MISSING>"
                phone = "<MISSING>"
                try:
                    if location_name in ID_dict:
                        ID = ID_dict[location_name]
                        log.info(ID)
                        ajax_URL = (
                            search_url.split("/en")[0].strip()
                            + "/en/store-detail/{}/glossary"
                        )
                        ajax_req = session.post(
                            ajax_URL.format(ID),
                            headers=headers,
                            params=ajax_params,
                            data=ajax_data,
                        )

                        phone = (
                            ajax_req.text.split(
                                "field field--name-field-store-phone field--type-string field--label-hidden field__item\\u0022\\u003E"
                            )[1]
                            .strip()
                            .split("\\u003C")[0]
                            .strip()
                            .replace("\\/", "/")
                            .strip()
                            .split("/")[0]
                            .strip()
                            .replace("\\u200b", "")
                            .strip()
                            .replace("\\u00a0", "")
                            .strip()
                        )

                except:
                    pass

                location_type = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/div[contains(@class,"open--hours")]//span//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = "; ".join(hours).strip().replace("day;", "day:")

                latitude, longitude = "".join(store.xpath("./@data-lat")), "".join(
                    store.xpath("./@data-lng")
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
