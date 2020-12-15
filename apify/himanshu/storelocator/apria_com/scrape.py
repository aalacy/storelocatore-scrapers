import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import unicodedata

logger = SgLogSetup().get_logger("apria_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=200,
    )
    addressesess = []

    url = "https://www.apria.com/wp-admin/admin-ajax.php"

    for cord in coords:
        payload = (
            "action=csl_ajax_search&address=&formdata=nameSearch%3D%26addressInput%3D%26addressInputCity%3D%26addressInputState%3D%26addressInputCountry%3D%26ignore_radius%3D500&lat="
            + str(cord[0])
            + "&lng="
            + str(cord[1])
            + "&options%5Bappend_to_search%5D=&options%5Bboundaries_influence_type%5D=none&options%5Bbubble_footnote%5D=&options%5Bcity%5D=&options%5Bcity_selector%5D=&options%5Bcluster_gridsize%5D=60&options%5Bcluster_minimum%5D=3&options%5Bclusters_enabled%5D=1&options%5Bcountry%5D=&options%5Bcountry_selector%5D=&options%5Bcron_import_recurrence%5D=none&options%5Bcron_import_timestamp%5D=&options%5Bcsv_clear_messages_on_import%5D=1&options%5Bcsv_duplicates_handling%5D=add&options%5Bcsv_file_url%5D=&options%5Bcsv_skip_geocoding%5D=0&options%5Bdefault_comments%5D=0&options%5Bdefault_page_status%5D=draft&options%5Bdefault_trackbacks%5D=0&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bgoogle_map_style%5D=&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=500&options%5Binstalled_version%5D=5.5.3&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bload_data%5D=0&options%5Bloading_indicator%5D=&options%5Bloading_indicator_color%5D=blue_light_grey&options%5Bloading_indicator_location%5D=map&options%5Bmap_appearance_cluster_header%5D=&options%5Bmap_center%5D=United+States&options%5Bmap_center_lat%5D=37.09024&options%5Bmap_center_lng%5D=-95.712891&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fwww.apria.com%2Fwp-content%2Fthemes%2Fapria%2Fassets%2Fimg%2Fmap_marker.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fwww.apria.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fblank.png&options%5Bmap_marker_tooltip%5D=1&options%5Bmap_option_fullscreenControl%5D=1&options%5Bmap_option_hide_streetview%5D=0&options%5Bmap_option_zoomControl%5D=1&options%5Bmap_options_clickableIcons%5D=1&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Bno_homeicon_at_start%5D=1&options%5Bpage_template%5D=&options%5Bpages_read_more_text%5D=&options%5Bpages_replace_websites%5D=1&options%5Bpagination_enabled%5D=0&options%5Bpermalink_flush_needed%5D=0&options%5Bpermalink_starts_with%5D=store-page&options%5Bprepend_permalink_blog%5D=1&options%5Bprevent_new_window%5D=1&options%5Bresults_click_animate_marker%5D=none&options%5Bresults_click_label_marker%5D=no_label&options%5Bresults_click_map_movement%5D=stationary&options%5Bresults_click_marker_icon%5D=&options%5Bresults_click_marker_icon_behavior%5D=as_is&options%5Bresults_no_wrapper%5D=0&options%5Bsearch_box_subtitle%5D=&options%5Bsearch_on_map_move%5D=0&options%5Bstate%5D=&options%5Bstate_selector%5D=&options%5Btag_autosubmit%5D=0&options%5Btag_dropdown_first_entry%5D=&options%5Btag_label%5D=&options%5Btag_output_processing%5D=hide&options%5Btag_selections%5D=&options%5Btag_selector%5D=none&options%5Btag_show_any%5D=1&options%5Bterritory%5D=&options%5Bterritory_selector%5D=&options%5Buse_nonces%5D=0&options%5Buse_same_window%5D=1&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=100&options%5Bzoom_tweak%5D=0&radius=500"
        )
        headers = {
            "accept": "*/*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.apria.com",
            "referer": "https://www.apria.com/find-a-branch/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        response = session.post(url, headers=headers, data=payload).json()
        for data in response["response"]:
            address2 = ""
            if data["address2"]:
                address2 = data["address2"]
            street_address = data["address"] + " " + address2
            location_name = data["name"]
            city = data["city"]
            zipp = data["zip"]
            state = data["state"]
            longitude = data["lng"]
            latitude = data["lat"]
            countryCode = "US"
            phone = data["phone"]
            hours = "<MISSING>"
            store_number = data["linked_postid"]
            store = []
            store.append("https://www.apria.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(countryCode)
            store.append(store_number)
            store.append(
                str(phone).replace(
                    "Main: (803) 786-6900;  Backline: (803) 794-3934", "(803) 786-6900"
                )
            )
            store.append(data["description"])
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = "".join(
                        (
                            c
                            for c in unicodedata.normalize("NFD", store[i])
                            if unicodedata.category(c) != "Mn"
                        )
                    )
            store = [x.replace("–", "-") if type(x) == str else x for x in store]
            if store[2] in addressesess:
                continue
            addressesess.append(store[2])

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
