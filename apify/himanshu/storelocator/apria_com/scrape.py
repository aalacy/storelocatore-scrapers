from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "apria.com"
LOCATION_URL = "https://www.apria.com/locations"
API_URL = "https://dashboard.storelocatorplus.com/lakshmi_dot_nerella_at_skavatar_dot_com/wp-admin/admin-ajax.php"
HEADERS = {
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.apria.com",
    "referer": LOCATION_URL,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()
MISSING = "<MISSING>"


def search_data(lat, lng):
    payload = (
        "action=csl_ajax_search&address=&formdata=nameSearch%3D%26addressInput%3D%26addressInputCity%3D%26addressInputState%3D%26addressInputCountry%3D%26ignore_radius%3D500&lat="
        + str(lat)
        + "&lng="
        + str(lng)
        + "&options%5Bappend_to_search%5D=&options%5Bboundaries_influence_type%5D=none&options%5Bbubble_footnote%5D=&options%5Bcity%5D=&options%5Bcity_selector%5D=&options%5Bcluster_gridsize%5D=60&options%5Bcluster_minimum%5D=3&options%5Bclusters_enabled%5D=1&options%5Bcountry%5D=&options%5Bcountry_selector%5D=&options%5Bcron_import_recurrence%5D=none&options%5Bcron_import_timestamp%5D=&options%5Bcsv_clear_messages_on_import%5D=1&options%5Bcsv_duplicates_handling%5D=add&options%5Bcsv_file_url%5D=&options%5Bcsv_skip_geocoding%5D=0&options%5Bdefault_comments%5D=0&options%5Bdefault_page_status%5D=draft&options%5Bdefault_trackbacks%5D=0&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bgoogle_map_style%5D=&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=500&options%5Binstalled_version%5D=5.5.3&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bload_data%5D=0&options%5Bloading_indicator%5D=&options%5Bloading_indicator_color%5D=blue_light_grey&options%5Bloading_indicator_location%5D=map&options%5Bmap_appearance_cluster_header%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fwww.apria.com%2Fwp-content%2Fthemes%2Fapria%2Fassets%2Fimg%2Fmap_marker.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fwww.apria.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fblank.png&options%5Bmap_marker_tooltip%5D=1&options%5Bmap_option_fullscreenControl%5D=1&options%5Bmap_option_hide_streetview%5D=0&options%5Bmap_option_zoomControl%5D=1&options%5Bmap_options_clickableIcons%5D=1&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Bno_homeicon_at_start%5D=1&options%5Bpage_template%5D=&options%5Bpages_read_more_text%5D=&options%5Bpages_replace_websites%5D=1&options%5Bpagination_enabled%5D=0&options%5Bpermalink_flush_needed%5D=0&options%5Bpermalink_starts_with%5D=store-page&options%5Bprepend_permalink_blog%5D=1&options%5Bprevent_new_window%5D=1&options%5Bresults_click_animate_marker%5D=none&options%5Bresults_click_label_marker%5D=no_label&options%5Bresults_click_map_movement%5D=stationary&options%5Bresults_click_marker_icon%5D=&options%5Bresults_click_marker_icon_behavior%5D=as_is&options%5Bresults_no_wrapper%5D=0&options%5Bsearch_box_subtitle%5D=&options%5Bsearch_on_map_move%5D=0&options%5Bstate%5D=&options%5Bstate_selector%5D=&options%5Btag_autosubmit%5D=0&options%5Btag_dropdown_first_entry%5D=&options%5Btag_label%5D=&options%5Btag_output_processing%5D=hide&options%5Btag_selections%5D=&options%5Btag_selector%5D=none&options%5Btag_show_any%5D=1&options%5Bterritory%5D=&options%5Bterritory_selector%5D=&options%5Buse_nonces%5D=0&options%5Buse_same_window%5D=1&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=100&options%5Bzoom_tweak%5D=0&radius=500"
    )
    response = session.post(API_URL, headers=HEADERS, data=payload).json()
    return response


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=15,
    )
    for lat, lng in search:
        data = search_data(lat, lng)
        for row in data["response"]:
            search.found_location_at(lat, lng)
            address2 = ""
            if row["address2"]:
                address2 = row["address2"]
            street_address = row["address"] + " " + address2
            location_name = row["name"]
            city = row["city"]
            zip_postal = row["zip"]
            state = row["state"]
            longitude = row["lng"]
            latitude = row["lat"]
            country_code = "US"
            phone = (
                row["phone"]
                .replace(
                    "Main: (803) 786-6900;  Backline: (803) 794-3934", "(803) 786-6900"
                )
                .strip()
            )
            hours_of_operation = MISSING
            location_type = MISSING
            store_number = row["linked_postid"]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=LOCATION_URL,
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
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
