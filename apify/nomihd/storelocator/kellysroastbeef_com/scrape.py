# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "kellysroastbeef.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.kellysroastbeef.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.kellysroastbeef.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.kellysroastbeef.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {
    "address": "",
    "formdata": "addressInput=",
    "lat": "70.09024",
    "lng": "-59.712891",
    "name": "",
    "options[bubblelayout]": '<div id="slp_info_bubble_[slp_location id]" class="slp_info_bubble [slp_location featured]">\n    <span id="slp_bubble_name"><strong>[slp_location name  suffix  br]</strong></span>\n    <span id="slp_bubble_address">[slp_location address       suffix  br]</span>\n    <span id="slp_bubble_address2">[slp_location address2      suffix  br]</span>\n    <span id="slp_bubble_city">[slp_location city          suffix  comma]</span>\n    <span id="slp_bubble_state">[slp_location state suffix    space]</span>\n    <span id="slp_bubble_zip">[slp_location zip suffix  br]</span>\n    <span id="slp_bubble_country"><span id="slp_bubble_country">[slp_location country       suffix  br]</span></span>\n    <span id="slp_bubble_directions">[html br ifset directions]\n    [slp_option label_directions wrap directions]</span>\n    <span id="slp_bubble_website">[html br ifset url][slp_location web_link][html br ifset url]</span>\n    <span id="slp_bubble_email">[slp_location email         wrap    mailto ][slp_option label_email ifset email][html closing_anchor ifset email][html br ifset email]</span>\n    <span id="slp_bubble_phone">[html br ifset phone]\n    <span class="location_detail_label">[slp_option   label_phone   ifset   phone]</span>[slp_location phone         suffix    br]</span>\n    <span id="slp_bubble_fax"><span class="location_detail_label">[slp_option   label_fax     ifset   fax  ]</span>[slp_location fax           suffix    br]<span>\n    <span id="slp_bubble_description"><span id="slp_bubble_description">[html br ifset description]\n    [slp_location description raw]</span>[html br ifset description]</span>\n    <span id="slp_bubble_hours">[html br ifset hours]\n    <span class="location_detail_label">[slp_option   label_hours   ifset   hours]</span>\n    <span class="location_detail_hours">[slp_location hours         suffix    br]</span></span>\n    <span id="slp_bubble_img">[html br ifset img]\n    [slp_location image         wrap    img]</span>\n    <span id="slp_tags">[slp_location tags]</span>\n    </div>',
    "options[distance_unit]": "miles",
    "options[ignore_radius]": "0",
    "options[immediately_show_locations]": "0",
    "options[initial_radius]": "10000",
    "options[initial_results_returned]": "25",
    "options[label_directions]": "Directions",
    "options[label_email]": "Email",
    "options[label_fax]": "Fax",
    "options[label_phone]": "Phone",
    "options[label_website]": "Website",
    "options[map_center]": "United States",
    "options[map_center_lat]": "70.09024",
    "options[map_center_lng]": "-59.712891",
    "options[map_domain]": "maps.google.com",
    "options[map_end_icon]": "http://000g2tw.myregisteredwp.com/wp-content/plugins/store-locator-le/images/icons/bulb_azure.png",
    "options[map_home_icon]": "http://000g2tw.myregisteredwp.com/wp-content/plugins/store-locator-le/images/icons/box_yellow_home.png",
    "options[map_type]": "roadmap",
    "options[message_no_results]": "No locations found.",
    "options[message_no_api_key]": "This site most likely needs a Google Maps API key.",
    "options[no_autozoom]": "0",
    "options[no_homeicon_at_start]": "1",
    "options[radii]": "10,25,50,100,(200),500",
    "options[radius_behavior]": "always_use",
    "options[results_layout]": '<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">\n        <div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >\n            \n            <span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>\n            <span class="location_distance">[slp_location distance format="decimal1"] [slp_option distance_unit]</span>\n            \n        </div>\n        <div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >\n            \n            <span class="slp_result_address slp_result_street">[slp_location address]</span>\n            <span class="slp_result_address slp_result_street2">[slp_location address2]</span>\n            <span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>\n            <span class="slp_result_address slp_result_country">[slp_location country]</span>\n            <span class="slp_result_address slp_result_phone">[slp_location phone]</span>\n            <span class="slp_result_address slp_result_fax">[slp_location fax]</span>\n                        \n        </div>\n        <div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >\n            \n            <span class="slp_result_contact slp_result_website">[slp_location web_link raw]</span>\n            <span class="slp_result_contact slp_result_email">[slp_location email_link]</span>\n            <span class="slp_result_contact slp_result_directions"><a href="http://[slp_option map_domain]/maps?saddr=[slp_location search_address]&amp;daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_option label_directions]</a></span>\n            <span class="slp_result_contact slp_result_hours">[slp_location hours format text]</span>\n            [slp_location pro_tags raw]\n            [slp_location iconarray wrap="fullspan"]\n            [slp_location eventiconarray wrap="fullspan"]\n            [slp_location socialiconarray wrap="fullspan"]\n            \n            </div>\n    </div>',
    "options[slplus_version]": "4.5.09",
    "options[use_sensor]": "0",
    "options[zoom_level]": "12",
    "options[zoom_tweak]": "1",
    "options[layout]": '<div id="sl_div">[slp_search][slp_map][slp_results]</div>',
    "options[maplayout]": "[slp_mapcontent][slp_maptagline]",
    "options[resultslayout]": '<div id="slp_results_[slp_location id]" class="results_entry location_primary [slp_location featured]">\n        <div class="results_row_left_column"   id="slp_left_cell_[slp_location id]"   >\n            [slp_addon section=primary position=first]\n            <span class="location_name">[slp_location name] [slp_location uml_buttons] [slp_location gfi_buttons]</span>\n            <span class="location_distance">[slp_location distance_1] [slp_location distance_unit]</span>\n            [slp_addon section=primary position=last]\n        </div>\n        <div class="results_row_center_column location_secondary" id="slp_center_cell_[slp_location id]" >\n            [slp_addon section=secondary position=first]\n            <span class="slp_result_address slp_result_street">[slp_location address]</span>\n            <span class="slp_result_address slp_result_street2">[slp_location address2]</span>\n            <span class="slp_result_address slp_result_citystatezip">[slp_location city_state_zip]</span>\n            <span class="slp_result_address slp_result_country">[slp_location country]</span>\n            <span class="slp_result_address slp_result_phone">[slp_location phone]</span>\n            <span class="slp_result_address slp_result_fax">[slp_location fax]</span>\n            [slp_addon section=secondary position=last]            \n        </div>\n        <div class="results_row_right_column location_tertiary"  id="slp_right_cell_[slp_location id]"  >\n            [slp_addon section=tertiary position=first]\n            <span class="slp_result_contact slp_result_website">[slp_location web_link]</span>\n            <span class="slp_result_contact slp_result_email">[slp_location email_link]</span>\n            <span class="slp_result_contact slp_result_directions"><a href="http://[slp_option map_domain]/maps?saddr=[slp_location search_address]&daddr=[slp_location location_address]" target="_blank" class="storelocatorlink">[slp_location directions_text]</a></span>\n            <span class="slp_result_contact slp_result_hours">[slp_location hours]</span>\n            [slp_location pro_tags]\n            [slp_location iconarray wrap="fullspan"]\n            [slp_location eventiconarray wrap="fullspan"]\n            [slp_location socialiconarray wrap="fullspan"]\n            [slp_addon section=tertiary position=last]\n            </div>\n    </div>',
    "options[searchlayout]": '<div id="address_search">\n        [slp_search_element add_on location="very_top"]\n        [slp_search_element input_with_label="name"]\n        [slp_search_element input_with_label="address"]\n        [slp_search_element dropdown_with_label="city"]\n        [slp_search_element dropdown_with_label="state"]\n        [slp_search_element dropdown_with_label="country"]\n        [slp_search_element selector_with_label="tag"]\n        [slp_search_element dropdown_with_label="category"]\n        [slp_search_element dropdown_with_label="gfl_form_id"]\n        [slp_search_element add_on location="before_radius_submit"]\n        <div class="search_item">\n            [slp_search_element dropdown_with_label="radius"]\n            [slp_search_element button="submit"]\n        </div>\n        [slp_search_element add_on location="after_radius_submit"]\n        [slp_search_element add_on location="very_bottom"]\n    </div>',
    "options[theme]": "",
    "options[id]": "",
    "options[hide_search_form]": "",
    "options[force_load_js]": "0",
    "options[map_region]": "us",
    "radius": "10000",
    "tags": "",
    "action": "csl_ajax_onload",
}


def fetch_data():
    # Your scraper here
    base = "https://www.kellysroastbeef.com/locations/"
    api_url = "https://www.kellysroastbeef.com/wp-admin/admin-ajax.php"
    api_res = session.post(api_url, headers=headers, data=data)

    json_res = json.loads(api_res.text)

    stores_list = json_res["response"]

    for store in stores_list:

        page_url = base + store["name"].lower().replace(" ", "-")

        store_number = store["id"]
        locator_domain = website

        location_name = store["name"].strip()
        street_address = store["address"].strip()
        if "address2" in store and store["address2"]:
            street_address = (
                (street_address + ", " + store["address2"]).strip(", ").strip()
            )

        city = store["city"].strip()
        state = store["state"].strip()

        zip = store["zip"].strip()

        country_code = "US"
        phone = store["phone"]
        location_type = "<MISSING>"

        hours_of_operation = store["hours"].split("Drive")[0].strip()

        latitude = store["lat"]
        longitude = store["lng"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
