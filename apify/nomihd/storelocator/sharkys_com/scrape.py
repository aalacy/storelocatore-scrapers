# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

website = "sharkys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "dashboard.storelocatorplus.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "accept": "*/*",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-dest": "script",
    "referer": "https://www.sharkys.com/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

param1 = (
    ("callback", "initMySLP"),
    ("action", "csl_ajax_search"),
    ("address", ""),
    ("formdata", "addressInputCity=&addressInput=&ignore_radius=0"),
)

param2 = (
    ("options[address_autocomplete]", "none"),
    ("options[append_to_search]", ""),
    ("options[city]", ""),
    ("options[city_selector]", "dropdown_addressinput"),
    ("options[country]", ""),
    ("options[country_selector]", "hidden"),
    ("options[cron_import_recurrence]", "none"),
    ("options[cron_import_timestamp]", ""),
    ("options[csv_clear_messages_on_import]", "0"),
    ("options[csv_duplicates_handling]", "update"),
    (
        "options[csv_file_url]",
        "https://docs.google.com/spreadsheets/d/1TXa3UXKqTA2vCRmOzoWl4dUJ236kUvTDEN1LDOxu5Y0/edit#gid=156241831",
    ),
    ("options[csv_skip_geocoding]", "1"),
    ("options[default_comments]", "0"),
    ("options[default_page_status]", "publish"),
    ("options[default_trackbacks]", "0"),
    ("options[disable_initial_directory]", "0"),
    ("options[distance_unit]", "miles"),
    ("options[dropdown_style]", "base"),
    ("options[google_map_style]", "[]"),
    ("options[ignore_radius]", "0"),
    ("options[immediately_show_locations]", "0"),
    ("options[initial_radius]", "30"),
    ("options[installed_version]", "5.5.5"),
    ("options[label_directions]", "Directions"),
    ("options[label_email]", "Email"),
    ("options[label_fax]", "Fax"),
    ("options[label_phone]", "Phone"),
    ("options[label_website]", "Website"),
    ("options[load_data]", "0"),
    ("options[loading_indicator]", ""),
    ("options[map_center]", "Los Angeles"),
    ("options[map_center_lat]", "34.07720800"),
    ("options[map_center_lng]", "-118.26529100"),
    ("options[map_domain]", "maps.google.com"),
    (
        "options[map_end_icon]",
        "https://www.sharkys.com/wp-content/uploads/2013/02/store_icon.png",
    ),
    (
        "options[map_home_icon]",
        "https://www.sharkys.com/wp-content/plugins/store-locator-le/images/icons/blank.png",
    ),
    ("options[map_region]", "us"),
    ("options[map_type]", "roadmap"),
    ("options[no_autozoom]", "0"),
    ("options[no_homeicon_at_start]", "0"),
    ("options[page_template]", ""),
    ("options[pages_read_more_text]", ""),
    ("options[pages_replace_websites]", "1"),
    ("options[permalink_flush_needed]", "0"),
    ("options[permalink_starts_with]", "store-page"),
    ("options[prepend_permalink_blog]", "1"),
    ("options[prevent_new_window]", "1"),
    ("options[selector_behavior]", "either_or"),
    ("options[state]", ""),
    ("options[state_selector]", "hidden"),
    ("options[territory]", ""),
    ("options[territory_selector]", ""),
    ("options[use_nonces]", "0"),
    ("options[use_same_window]", "1"),
    ("options[use_sensor]", "false"),
    ("options[zoom_level]", "8"),
    ("options[zoom_tweak]", "1"),
    ("radius", "100"),
    (
        "api_key",
        "myslp.8b96566446ee78867915df06d4c3162f1fd8257c5f28ab0a88c3108c20c60dc7",
    ),
    ("_jsonp", "initMySLP"),
    ("_", "1619546981480"),
)


def fetch_data():
    # Your scraper here
    search_url = "https://www.sharkys.com/locations/"

    api_url = "https://dashboard.storelocatorplus.com/jessica_at_imomedia_dot_com/wp-json/myslp/v2/locations-map/search"

    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    stores_dict = dict()
    for lat, lng in coords:
        params = param1 + (("lat", lat), ("lng", lng)) + param2
        api_res = session.get(api_url, headers=headers, params=params)
        json_str = api_res.text.split("/**/initMySLP")[1].strip(" ()")

        json_obj = json.loads(json_str)

        store_list = json_obj["data"]["response"]
        for store in store_list:

            if store["id"] in stores_dict.keys():
                continue
            data = dict()
            data["locator_domain"] = website
            data["page_url"] = search_url
            data["location_name"] = store["name"]
            address = store["address"]
            if (
                "address2" in store
                and store["address2"] is not None
                and store["address2"].strip()
            ):
                address = store["address2"]

            data["street_address"] = address
            data["city"] = store["city"]
            data["state"] = store["state"]
            data["zip_postal"] = store["zip"]
            data["country_code"] = "US"
            data["store_number"] = store["id"]
            data["phone"] = store["dial"]
            data["location_type"] = "<MISSING>"
            data["latitude"] = store["lat"]
            data["longitude"] = store["lng"]
            hours = store["hours"].split("&lt;")[0].replace("\r\n", "; ").strip("; ")
            data["hours_of_operation"] = hours
            data["raw_address"] = "<MISSING>"

            # Save into the dictionary
            stores_dict[store["id"]] = data

    for store in stores_dict.values():

        yield SgRecord(
            locator_domain=store["locator_domain"],
            page_url=store["page_url"],
            location_name=store["location_name"],
            street_address=store["street_address"],
            city=store["city"],
            state=store["state"],
            zip_postal=store["zip_postal"],
            country_code=store["country_code"],
            store_number=store["store_number"],
            phone=store["phone"],
            location_type=store["location_type"],
            latitude=store["latitude"],
            longitude=store["longitude"],
            hours_of_operation=store["hours_of_operation"],
            raw_address=store["raw_address"],
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
