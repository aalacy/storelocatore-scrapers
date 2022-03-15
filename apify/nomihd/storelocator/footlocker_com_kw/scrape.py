# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.footlocker.com.kw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.footlocker.com.kw",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://www.footlocker.com.kw",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.footlocker.com.kw/en/store-finder",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "cookie": "cf_chl_2=1b0f85bf71110aa; cf_chl_prog=x12",
}

params = (
    (
        "__cf_chl_captcha_tk__",
        "pmd_dzDgjNvxmuc_yYma4G4Schh8FCgFRZDbW4PxnYy7SoQ-1634050663-0-gqNtZGzNAyWjcnBszQu9",
    ),
)

data = {
    "md": "53tANQfXvx47zDuzglZz_Ux2KBHqN8qzXzPDRgo0G.4-1634050663-0-Ae1isFR3rI8MfYuBGYerXpZh_XMHmDbCO1kjlfwYOp1o_CESJ6KJ0GJWK7ZPwNmFJxM-CvZ37O853tCB2d-ckYUeMxGYcOalqBHhk9Yrt2Z37qH1_EKn-GlkM1gy1x1R2Laq2zyoPoNHnE4rFEuxgHLp3wWKwJsMg0gFKUyDqYz-Vkq-mtgzYT5eILm50ra_Hgba5P22NY8ZlWit3jDX5quFMKYGZcdA1dCQRuVaNzX_QcmaXR1_ZaInnZPLnGXTWKrqUqHL4bwZjy9dMIR7bQRsqyKzZFhepx7QE8myf1m9QoP9-3k3tQaK7ya57EgVSzdHuxNwxIhf5nY1W-58rJ00pKoNLQ1FwLMHxBVxOvOqCSfD8AYorndpj-LyqQ-rhEjv95vdV3PuUJx5-4pe0NzAl3GwNlYkOjYr8Gt_WQHYfFJy4O567jjwYcMyBsepIWzNEZjibb5DjUbnjqSXcLUIMMO5NRy5ZJes_Q9156hsZ5TPRacqCBbjQhXaf7n6kzpqVyRYCBii4FxWqO7GL1JBu1sikTNC8C5H6o6Yd6l8ztLj-ruVWQ8MFAbmhBOwW9VDtQGC2UJxkbAo5TChd-ULdRvNsYKFrdt91KqlCHQVVJNHkoRxlWvFBUrvdH-65Q0KJ9HcHBpEUyrsQApfHrxBjy77T_g4SUs4FLklWX9n5wnRj_ndNZo8Jr2fQX1XHax9CmFlGu1Si1QpJ1op1c74vFs2Ghl1nIbZxltkxSc1",
    "r": "hYbjTZPI101EUagpdyIK4b9sKhK95V1J82iYgybl.oI-1634050663-0-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",
    "cf_captcha_kind": "h",
    "vc": "6e9f61d87169b699e5b7d60186a0d36f",
    "captcha_vc": "b45d5963f80b45f7762e85de86bb1282",
    "captcha_answer": "lqBLFzINUwYn-12-69d12ea8591c29bc",
    "cf_ch_verify": "plat",
    "h-captcha-response": "captchka",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.footlocker.com.kw/en/store-finder"

    with SgRequests() as session:
        search_res = session.post(
            "https://www.footlocker.com.kw/en/store-finder",
            headers=headers,
            params=params,
            data=data,
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
                "ajax_page_state[theme]": "alshaya_footlocker",
                "ajax_page_state[theme_token]": "",
                "ajax_page_state[libraries]": "alshaya_acm_cart_notification/cart_notification_js,alshaya_algolia_react/autocomplete,alshaya_dynamic_yield/alshaya_dynamic_yield.product_modal,alshaya_footlocker/global_styles,alshaya_footlocker/ltr_styles,alshaya_geolocation/places-api.googleplacesapi,alshaya_i18n/language_selection,alshaya_master/common_fixes,alshaya_master/focus_form_error,alshaya_newsletter/newsletter_js,alshaya_search_api/back_to_list,alshaya_seo_transac/gtm_algolia,alshaya_spc/cart_utilities,alshaya_spc/commerce_backend.cart.v1,alshaya_spc/mini_cart,alshaya_stores_finder/store_finder,alshaya_white_label/algolia_search,alshaya_white_label/color_styles,alshaya_white_label/footer_js,alshaya_white_label/global_styles,alshaya_white_label/plp-add-to-cart,alshaya_white_label/plp-swatch-hover,alshaya_white_label/slick_css,alshaya_white_label/store_finder,alshaya_white_label/ucfix,back_to_top/back_to_top_icon,back_to_top/back_to_top_js,clientside_validation_jquery/cv.jquery.ckeditor,clientside_validation_jquery/cv.jquery.ife,clientside_validation_jquery/cv.jquery.validate,cog/lib,core/html5shiv,datadog_js/logger,datalayer/behaviors,dynamic_yield/dynamic_yield.intelligent_tracking,geolocation/geolocation.commonmap,geolocation/geolocation.views.filter.geocoder,system/base,views/views.ajax,views/views.module",
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
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "KW"

            store_number = "<MISSING>"
            phone = "<MISSING>"
            try:
                if location_name in ID_dict:
                    ID = ID_dict[location_name]
                    log.info(ID)
                    ajax_req = session.post(
                        "https://www.footlocker.com.kw/en/store-detail/{}/glossary".format(
                            ID
                        ),
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
