from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "footlocker_ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
}

DOMAIN = "https://footlocker.ae/"
MISSING = SgRecord.MISSING

payload = "js=true&_drupal_ajax=1&ajax_page_state%5Btheme%5D=alshaya_footlocker&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=alshaya_acm_cart_notification%2Fcart_notification_js%2Calshaya_algolia_react%2Fautocomplete%2Calshaya_dynamic_yield%2Falshaya_dynamic_yield.product_modal%2Calshaya_footlocker%2Fglobal_styles%2Calshaya_footlocker%2Fltr_styles%2Calshaya_geolocation%2Fplaces-api.googleplacesapi%2Calshaya_i18n%2Flanguage_selection%2Calshaya_master%2Fcommon_fixes%2Calshaya_master%2Ffocus_form_error%2Calshaya_newsletter%2Fnewsletter_js%2Calshaya_search_api%2Fback_to_list%2Calshaya_seo_transac%2Fgtm_algolia%2Calshaya_spc%2Fcart_utilities%2Calshaya_spc%2Fcommerce_backend.cart.v1%2Calshaya_spc%2Fmini_cart%2Calshaya_stores_finder%2Fstore_finder%2Calshaya_white_label%2Falgolia_search%2Calshaya_white_label%2Fcolor_styles%2Calshaya_white_label%2Ffooter_js%2Calshaya_white_label%2Fglobal_styles%2Calshaya_white_label%2Fplp-add-to-cart%2Calshaya_white_label%2Fplp-swatch-hover%2Calshaya_white_label%2Fslick_css%2Calshaya_white_label%2Fstore_finder%2Calshaya_white_label%2Fucfix%2Cback_to_top%2Fback_to_top_icon%2Cback_to_top%2Fback_to_top_js%2Cclientside_validation_jquery%2Fcv.jquery.ckeditor%2Cclientside_validation_jquery%2Fcv.jquery.ife%2Cclientside_validation_jquery%2Fcv.jquery.validate%2Ccog%2Flib%2Ccore%2Fhtml5shiv%2Cdatadog_js%2Flogger%2Cdatalayer%2Fbehaviors%2Cdynamic_yield%2Fdynamic_yield.intelligent_tracking%2Cgeolocation%2Fgeolocation.commonmap%2Cgeolocation%2Fgeolocation.views.filter.geocoder%2Csystem%2Fbase%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module"


def fetch_data():
    loclist = []
    if True:
        url = "https://www.footlocker.ae/en/store-finder"
        with SgRequests(proxy_country="ae") as http:
            r = http.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            linklist = soup.findAll("div", {"class": "by--alphabet"})
            for link in linklist:
                temp_list = link.findAll("a")
                loclist += temp_list
            for loc in loclist:
                store_number = loc["data-glossary-view"]
                link = (
                    "https://www.footlocker.ae/en/store-detail/"
                    + store_number
                    + "/glossary?_wrapper_format=drupal_ajax"
                )
                data = http.get(link, headers=headers, data=payload).json()
                data = data[3]["data"]
                soup = BeautifulSoup(data, "html.parser")
                location_name = (
                    soup.find("a", {"class": "row-title"})
                    .get_text(separator="|", strip=True)
                    .replace("|", "")
                )
                log.info(location_name)
                phone = soup.find(
                    "div", {"class": "field--name-field-store-phone"}
                ).text
                raw_address = (
                    soup.find("div", {"class": "field-content"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                    .replace(phone, "")
                )
                if "+966" in raw_address:
                    raw_address = raw_address.split("+966")[0]
                if "/" in phone:
                    phone = phone.split("/")[0]
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING

                country_code = "AE"
                hours_of_operation = (
                    soup.find("div", {"class": "open--hours"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                coords = soup.find("div", {"class": "geolocation"})
                latitude = coords["data-lat"]
                longitude = "-" + coords["data-lng"]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
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
