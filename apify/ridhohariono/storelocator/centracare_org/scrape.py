from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa


DOMAIN = "centracare.org"
BASE_URL = "https://centracare.adventhealth.com"
LOCATION_URL = "https://www.adventhealth.com/find-a-location?facility=&name=centra+care"
API_URL = "https://www.adventhealth.com/views/ajax?facility=&name=centra+care&geolocation_geocoder_google_geocoding_api=&geolocation_geocoder_google_geocoding_api_state=1&latlng%5Bvalue%5D=&latlng%5Bcity%5D=&latlng%5Bstate%5D=&latlng%5Bprecision%5D=&service=&_wrapper_format=drupal_ajax"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    num = 0
    while True:
        payloads = {
            "view_name": "ahs_facility_search_list",
            "view_display_id": "map",
            "view_args": "",
            "view_path": "/node/1154",
            "view_base_path": "",
            "view_dom_id": "bbb39c7359d93358b557bec79aca8d85bcf7c84c460ac4456abf5fcc9cd85fd0",
            "pager_element": "0",
            "view_exposed_form_selector": '[id^="views-exposed-form-ahs-facility-search-list-map"]',
            "name": "centra care",
            "geolocation_geocoder_google_geocoding_api_state": "1",
            "latlng[distance][from]": "-",
            "page": num,
            "_drupal_ajax": "1",
            "ajax_page_state[theme]": "ahs_theme",
            "ajax_page_state[theme_token]": "",
            "ajax_page_state[libraries]": "ahs_admin/ahstabletools,ahs_banners/emergency,ahs_breadcrumbs/views,ahs_datalayer/datalayer,ahs_datalayer/visitor_geolocation,ahs_formstack/colorbox.popup,ahs_js/ahs_tooltip,ahs_js/anchor_links,ahs_js/autocomplete,ahs_js/form_validate.base,ahs_js/random_hero_picker,ahs_js/site_popups,ahs_media/blazy,ahs_media/blazy_slick,ahs_microsites/non_microsite_page,ahs_search/clear_all_facets_block,ahs_search/facet_facility_checkbox_widget,ahs_search/facets,ahs_search/facets_header_block,ahs_search/facets_module_checkbox_widget_extended,ahs_search/geolocation.links,ahs_search/geolocation.widget,ahs_search/physician_search.autocomplete,ahs_theme/core,ahs_views/bef_auto_submit,ahs_views/exposed_form_persistent_facets_non_ajax,ahs_views/views_ajax,amplitude/amplitude-events,better_exposed_filters/general,colorbox/example3,core/drupal.autocomplete,core/picturefill,datalayer/helper,eu_cookie_compliance/eu_cookie_compliance,eu_cookie_compliance/eu_cookie_compliance_bare,extlink/drupal.extlink,facets/drupal.facets.checkbox-widget,facets/drupal.facets.hierarchical,facets/drupal.facets.views-ajax,geolocation/geolocation.geocoder.googlegeocodingapi,geolocation/geolocation.views.filter.geocoder,paragraphs/drupal.paragraphs.unpublished,search_api_autocomplete/search_api_autocomplete,system/base,views/views.module",
        }
        log.info("Pull page => {}".format(str(num)))
        req = session.post(API_URL, headers=HEADERS, data=payloads).json()
        stores = bs(req[2]["data"], "lxml").select(
            "ul.facility-search-block__items div.location-block__caption"
        )
        if not stores:
            break
        for row in stores:
            try:
                location_name = (
                    row.find("span", {"class": "location-block__name-link-text"})
                    .text.replace("\n", " ")
                    .strip()
                )
            except:
                location_name = (
                    row.find("h3", {"class": "location-block__name"})
                    .text.replace("\n", " ")
                    .strip()
                )
            addr = row.find("span", {"class": "location-block__address-text"})
            try:
                addr.find("span", {"class": "visually-hidden"}).decompose()
            except:
                pass
            raw_address = addr.get_text(strip=True, separator=" ").strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "US"
            if city == MISSING:
                city = addr.find("span", {"class": "addressLocality"}).text.strip()
            if state == MISSING:
                state = addr.find("span", {"class": "addressRegion"}).text.strip()
            if zip_postal == MISSING:
                zip_postal = addr.find("span", {"class": "postalCode"}).text.strip()
            try:
                phone_content = row.find(
                    "span", {"class": "location-block__telephone-text"}
                )
                phone_content.find("span", {"class": "visually-hidden"}).decompose()
                phone = phone_content.text.strip()
            except:
                phone = MISSING
            hours_of_operation = MISSING
            page_url = LOCATION_URL
            try:
                page_url = row.find("h3", {"class": "location-block__name"}).find("a")[
                    "href"
                ]
                if (
                    "centracare.org" not in page_url
                    and "centracare-scheduling" not in page_url
                ):
                    if "adventhealth.com" not in page_url:
                        page_url = "https://www.adventhealth.com" + page_url
                    store_content = pull_content(page_url)
                    hoo_content = store_content.find("strong", text="Our Hours:")
                    if not hoo_content:
                        hoo_content = store_content.find("strong", text="Office Hours")
                        hours_of_operation = hoo_content.find_next("div").get_text(
                            strip=True, separator=","
                        )
                    else:
                        hours_of_operation = hoo_content.find_next("p").get_text(
                            strip=True, separator=","
                        )
            except:
                pass
            location_type = "CENTRA CARE"
            store_number = MISSING
            latlong = row.find("a", {"class": "address"})
            latitude = latlong["data-lat"]
            longitude = latlong["data-lng"]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        num += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
