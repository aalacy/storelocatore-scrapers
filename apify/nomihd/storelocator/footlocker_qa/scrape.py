# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.footlocker.qa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.footlocker.qa",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://www.footlocker.qa",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.footlocker.qa/en/store-finder",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
    "cookie": "cf_chl_rc_i=1; cf_chl_2=03171e232e91c02; cf_chl_prog=x19",
}

params = (
    (
        "__cf_chl_captcha_tk__",
        "pmd_xMbF5K1lRaCUSNAW.vlQyOYM6jSeoQD9HdYbuxU.x8M-1634052270-0-gqNtZGzNAyWjcnBszQc9",
    ),
)

data = {
    "md": "jev.ROTVB_pzGubew8WED9vpefa4Gw2sebTK8XplDvs-1634052270-0-ARIsnOXoQowN8mcbLxcCkwlqqLhM2jTfbt9vtSUNqaLkWDlMyebvxYAdrkK08RLi7SwsCUowVV3Tq2NmhFSTcJS3KTjN9jhstbedjc2pElFGLqeVbrAuhnZFE8WUqxEdhzNZABOGJRoT3XhpRBpMwaWZrk-mPu2kIC-X1dLGcp_4ddx7Sk7KZfgpytVctSSGaq0HKCxiTuI7umZll7SUBwazTH5Kwif8d28o4xABQtU6pby7lZ18yNxD4FxOBFdXSgI7neuAjuN_u_pcSDbkhXW7EkLE7aZSeojRZLvJ6qFggZoDSCYBzMJx9GsV1uhQjS4ezRQP3k3vXms-thBcoGSDCAjdSdSROZmRf4nbQb47Nwcyggi5pbyr7NRqUfokC4ZOzyq_nmsDIyEki0uGLGFen_-NSfvlcuwFp6NlrSgd8qzR0Ith6ghMxM4d8FYfXu-_NvRBj5em2nv_ye9zE3ShGv9bGzN-5O-A7zLRKmOyxIUhhj5FOQZLYjaisWdLMd8xm9wreeepDayxOqyLxIVeh_N7U3vKQYR19pZa1DXHYY9pfy8P_nUqSWyjvLlWlL86-n62nXvYgjffGBVwiSD7-4s2UuX1FR-xFByPAsp3Z1W1ZKK2HgbCMOyXD6oA4V2UYGdTrnKodkzerCEq2R9EfdPNn8uQ6l17NFEm-hUO26e3wNOqlDp77DQonOyW9Xte1fhlDzdZNBaMCJ587ucLygZYGGh5nZ4jxXNTMFzk",
    "r": "W_eCcl0h._7Vw3LbbyCDsUMXekKmjrw900sFf0xI5vw-1634052270-0-ARPwBY7VdNvL5ntvbDOnr6NZSt24Xu+lJxhQp+kd7Wwe5V09dUKTWaFG39df8peh2mp8eOHl1prYXHWF1E/+6jEj4Bev/0UBSJII2CswtdN2+0gETZPPeKTkt/rAzvHtaBh3jd6IorDM5MiiahQqFty8kHhK0ANCqxVIeRHOGEE4Upx0OB4k1iT3XbVsWdjn67xiwZchdPJe+9NB/BaiswEog6v0RdWyT7Jl/1z4qA/8NCpu1gnJExSiTKfvZDSyuRlGuPt+E4Cdg2AT6iTR5LLB6U8eiU5RjdCvWrDK3JnZiLwq6iEUvyOeyyR0DB2CN2ZZSbrkutWs2U2wibPcq1ppfY426ZLVkIeqWJgGM/7To30GUqJf1J8MsNNvYQ8gpg4d8SqTInEbsuGK/uu67KFEy0AIb0qimnB5+BOIjKcvP6ZPikW1lAxPqvDBJhbaFRoE25zQE9ZsBDJhcPULI31gMk7mQjkjXt1/m74++FzP2SLGGR7CPbjTCU79lvwW7DcZipJKnP7ZvsOGSShAxryzPfZvf3O0LHEd5Z6bxpO5+ZOoSeJttyN2H2EcbgMiRTY2EFXsqdx4DTQpgeHNiSEzx5NLvMd9kxz0GiOdclZePTiV0hS7AQeu3mmXME9mEZqF51mB1Pjm0yrufY9L0Ha1XD6c5W4+qdxzCSo6YcQE6eWcl0gXPRVL7GfcdnDa7g8MHkVOHc+D8rU2JNVS7soew7GEMvgEQxbitNVDsInmrrOveFV6B371Cl/3X3ohXKNIBlKhS57q/PQ9+Wy6bvUrJnXxcCly+PkCGVRDajhJt7RoUErUHH+VxnbnhMWst8Hd2J+4c4OU36pwzjlUXyO3kG85EhBw5/0nD77mTUZZ9oEBNorj2aO0tM71htJ+duM4CM8gkrn7s6K+doGMoSwwhjkY7kecH5fPSuuSdP/P9GwvmyJW5aoLiGSYGhHeFZQSsLhrQfDDX72uAbJ71d6kkPFxQMsTaQnKE2EpwHY9AnNi5ZdnzxSHDQT866P18G8sqAur/EJnUGjP3nrjYL2zeedC/DxmoCaGa/anvR+ro1fv4rrSGrHyMbNbX+gsZm2U8QSfV1LJ/x7eohU4XJ3rIBgQmJUPjv2GRj6hiT0DRLNOn7N0J7vaQn1ljLXmrCbr9bOwU7k4OVLLwu6dMXfv/+dxSgTYFq5929WCMnNw4WIcGjneXCu7LF8WZPjeG7tQJm6dCbmo3xpAPGnYfYvj3aJlJzGtnlegYOfGEVSoZpO5gBkoLSlj2SBulllQooXzgybrHN9FG1168grvnOfNK2YHo1IsBVaNDUc6/9IVxHcPCDJX864FOaAWxj49FwGO+lemIWtSCJbz18LsMQ1HjLKfpdr+BUTB/0q1oq0vOtS5lg9B9zdJRAz83MBEWKfcfD+m+zYn46VAqJeH5aSdNrjReIMyc5mje7w2mRHjZLJDlhdxvWYyCyz1juKaeoUlbotjCcrFmIKIyFwZRV6vtCttBWl/5qgsIW9DEZDdkoTbAg9mw95omvvx0yNGTmTgsJ8mm+xJ5Tot4KyjtFw+u/hXG+KBTtC3b8DZvxUtvqBJXmX8BGd8WlAjv3FdyrZFx8o0GW4feiulRLvcjiWH6dhnaE3UptxZYE/puQQ4tYKAM+I5+JnLIlT15iDn7i16WyVbv+Kv7bPt5EU6gvYbvDfp7Xe4JZibZrIJ4Rek171uN51nOdpxmjLpvGKXCRKfJRh54EUq9CMnZru1rGLcHgGOsR3NH9emCzyE5ksO7Sm47Sg9a+421zGgekw7Rg==",
    "cf_captcha_kind": "h",
    "vc": "12c27dc9113bc589e36e9df823132522",
    "captcha_vc": "c03e0e03607361dffca56d247e759a60",
    "captcha_answer": "xqFuqZVvkana-19-69d155dfcfd76b2d",
    "cf_ch_verify": "plat",
    "h-captcha-response": "captchka",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.footlocker.qa/en/store-finder"

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
                        "https://www.footlocker.qa/en/store-detail/{}/glossary".format(
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
