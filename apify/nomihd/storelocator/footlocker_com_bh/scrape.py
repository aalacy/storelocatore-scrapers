# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.footlocker.com.bh"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.footlocker.com.bh",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://www.footlocker.com.bh",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.footlocker.com.bh/en/store-finder",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "cookie": "cf_chl_rc_i=1; cf_chl_2=c282fceffcc8507; cf_chl_prog=x13",
}

params = (
    (
        "__cf_chl_captcha_tk__",
        "pmd_2QmxFrWzIkPEAAxUWaEU.D0satr8ksd7o7rmfWl3amI-1634051489-0-gqNtZGzNAyWjcnBszQdR",
    ),
)

data = {
    "md": "3DBTNFKB2LrkX7Ob0xSDi6bEi_v7NtL2YO9hepQ1EgA-1634051489-0-AWa0gGOXy1Uyxlt8yF-8zJ3RECIDGIeWCcmlfVlpPpA36GkS2_hddJ8UB-ktzF2nWu3gYOubF5Hd4FF_90pcy88nWGtF_Orxk-Bn58n-MBFG7u0YKK-PF41drNPI6TKQmM2MFbLGxIuB-XuaJJxE3b4URDA8ZKCU3Q8Bcg9Yx4B5vvYUhPLz2BdH9jTxeugNJ9v1mQfAT9-fzwpXUrwth4-CgyCxm-b30Pv8DFwj3rVu4we4QmVWhNSk2Glgv48jU8GRtQKo0zD9L1D7s7Vxew9B6Qhk_3HNIxDPJaPGbJOQHtzKkNFhkAkQ7JnWCn7Wvc9KVQcnGWTV30ALvHsq0Iwqppmw0pBxec9ia-A3eaf1a8-NG3pzU-w55Xv4McLmEZqvVuN8y5MzMrZXGSoBiuoHg1rLXFmgyxMa2CxpRO1l8WCorgO6vXKwQNe4n4Fvx3N4sVAgDdFYsIhdgevWeCHrvrRMyHekzjcIzFDMpRMT6lKF0gI78YHKcc_Q-4I8o_NZ3ILvnvPDgoTsKH4S5bBme9fnpQ80c2tphXKNOQjGgMORVGXT0wRUmz3w9CCSzR2Yxl0SDbpN_K6eogzIQzAm43GbHz8NN1Sw7G-KRGSMi2zZMpBC14Ae3KosV3_JjS5aRflJg-dFGkE8SgFFzyF6Lz9h4m7UuW3Q-eYTY0EaLpvDddNTelBzk_Cy2p_fX0QzKr9FAjqCqpsRuIDBq57WKXBDEi8_pWyFHupT_E8t",
    "r": "wJq_ORl353aIh0YAw.JvADH4SGY6OTDeWIBwq93.Hu0-1634051489-0-AWzgt3xdi364SBtrzmMguxTgltKSNv3go7RWtvD4+WQTtpUqFhzDSoAB+9CxIFOpNxfrZ/ARXhwaA410Ln+TsxOe+P6Xvm9g5NHIxITMFxklb6YEV4TLPu5F8wBgzOJDaK85bjYsigT6P6FnE9nbd4PzPVunWfi6rFmfQARAhnfhOXbPgalf/Ya8v4iC0Z3lOzv4kzfVxbiR8r6iRcWW5B5ODM4jRQQoI2Ak76+FrQaNM4TIo2ZZGeE+2uxyjREFQzyUVBZho8DhkEl+FVMIHmqgwxkXiGQDmRQ5lCWKLn8+ehb3AhMO8Aih08yHP0eb/pun3ABMIB6Z7b21fZRzMuzdNGCr4JNR2UHQBLEHMhBLKsmzfd30WV0sVEdl9kGIvtnn3TEnesZXvcQ5k0OD8eV7eKd3bcanNe96LGbLdjZePPHVZUxOjX0o7bb+7+EqhOFiQtoRjZrHvcRnspHkufbVdz2l1ja44XbuHASBRqNV3rUy1le977c73+CAp/muoFfyuJr5v6KEms0gB+TsdDrvWVznLBYV9fwZbGIuo983TlIuOFSoKd6URXDiXLw7Oa+a+bzsY7T7BZZF8mTtC5xQ+Qt3AmlVDMAb4//AbKIaV6oVAFWQlDvo6bkQ3DddRatiIQvAM1a/BDh71FUffhHPKowAFzLcPFijYOFQ2+dQ3DqdWziRUSXPKADFTQojtjhK+0DMCCnhIyia9Qs9RXuGBjYeMSiQXe+ZuqHG2wlz11C30MQEriHERlzj+l8JcBaO6ZjmLvHtQHNJWuAQ/x7qK4d7YPaeTI6vcGJZJONmyvrRsOdmvesbTy9b5940iFJ83e74+ZN8NX8N/B5ufAtdMnXQxE5DlWKzAs+Wjo5C1AvqDihdPA5WtaE+NFw5ZnanKwqeioW8okzr2a0VWBkGA07Ceti4/kfT7v0La9BCRXwhK0XGjMs9lZIb/MCHYeBC6d7ck3tHMX5WDXsUdxsd0srAnDo2ObBc7Fkf57TDFvuQ74/ORHgwtC0DJKduKy/QUBnbYj59OjUmQ7nkh5oRwlsEDFlHQKeUHofo0kWmxXGkFB3DvgGq2gtqmzW6sfWsxAVAABVIbJ3Qs65fw6lA4UOm+qfbNJJbAKVTFwcdSpmQJ2B8jL2WnXYprQ7x0/9Rjx9IJql/kPgxbMv8IIs6wfbaGF/3JN17C57ZyLzF+bxO5mDL0VgD3x1yfJ5L/MqaE5jcrcyemvz3b9n5z7z7b42RIRomfvvVp7tm1k1t9SYFSpqgigb9aoZyy7EBWvQABAINXeY2kqnwiXlW9QEx5a0FkahKEF+3+l/WCf5Y6GWdtC3NVaeE7bICq7ZXr6YUm0afc6BXJLkI+yj+VFuIUc9Ll9nSTWZp9yXGZt4CPIY47q1g6QCK9GUDIHNLMqcXM+LcaEebBqmf21HkSa0Qr4kzsSvpNu6eTTlxG2lurOY4QpVYRFIE1TFMZdxnRZ9Bsf+/kkkxqqjCNgAfn2IZhc2wzwwZu2fihYSCLTrbvBSbkpo6hnPfuG/1iwSjCxzQS16B8K1yxzKUlevXuORwoeT75cyVk5XOiuanMUnUhv9mTV1u3RIymKAkxN1EetoPgQlaqNME+z4kSuMJvelmIjW57yfr7WwXVW8q8NuWfXtNGa698bTSQ7cxgxhdEuLTs7AsyDJq0NTvYZDG2ScpgXydBy02QKkaW7rS9aYrrC0cAqRXD0wrTmQ1ktIz4RSD3GdbdzgMpQpFzHj/hXbWNlPuIR7MjsBOp5PabR85rfeKJEk4BsKc9mje5KXTckItrCri536DxDM49ToYKm8=",
    "cf_captcha_kind": "h",
    "vc": "939b09024cb58d9d01cb3aac4a934529",
    "captcha_vc": "9b330f0ecb74616d1c75566b193d37fa",
    "captcha_answer": "ghakGbIxRcVg-13-69d142cf6c274667",
    "cf_ch_verify": "plat",
    "h-captcha-response": "captchka",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.footlocker.com.bh/en/store-finder"

    with SgRequests() as session:
        search_res = session.post(
            search_url,
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

            country_code = "QA"

            store_number = "<MISSING>"
            phone = "<MISSING>"
            try:
                if location_name in ID_dict:
                    ID = ID_dict[location_name]
                    log.info(ID)
                    ajax_req = session.post(
                        "https://www.footlocker.com.bh/en/store-detail/{}/glossary".format(
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
                        .replace("\\/", "/")
                        .strip()
                        .split("/")[0]
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
