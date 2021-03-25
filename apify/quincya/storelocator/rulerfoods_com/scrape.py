import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        "authority": "rulerfoods.com",
        "method": "GET",
        "path": "/wp-admin/admin-ajax.php",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "12125",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://rulerfoods.com",
        "referer": "https://rulerfoods.com/locations/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    base_link = "https://rulerfoods.com/wp-admin/admin-ajax.php"

    payload = "address=&formdata=addressInput%3D&lat=38.9269&lng=-85.90449199999999&name=&options%5Bbubblelayout%5D=%3Cdiv+id%3D%22slp_info_bubble_%5Bslp_location+id%5D%22+class%3D%22slp_info_bubble+%5Bslp_location+featured%5D%22%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_name%22%3E%3Cstrong%3E%5Bslp_location+name++suffix++br%5D%3C%2Fstrong%3E%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_address%22%3E%5Bslp_location+address+++++++suffix++br%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_address2%22%3E%5Bslp_location+address2++++++suffix++br%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_city%22%3E%5Bslp_location+city++++++++++suffix++comma%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_state%22%3E%5Bslp_location+state+suffix++++space%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_zip%22%3E%5Bslp_location+zip+suffix++br%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_country%22%3E%3Cspan+id%3D%22slp_bubble_country%22%3E%5Bslp_location+country+++++++suffix++br%5D%3C%2Fspan%3E%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_directions%22%3E%5Bhtml+br+ifset+directions%5D%0D%0A++++%5Bslp_option+label_directions+wrap+directions%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_website%22%3E%5Bhtml+br+ifset+url%5D%5Bslp_location+web_link%5D%5Bhtml+br+ifset+url%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_email%22%3E%5Bslp_location+email+++++++++wrap++++mailto+%5D%5Bslp_option+label_email+ifset+email%5D%5Bhtml+closing_anchor+ifset+email%5D%5Bhtml+br+ifset+email%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_phone%22%3E%5Bhtml+br+ifset+phone%5D%0D%0A++++%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_phone+++ifset+++phone%5D%3C%2Fspan%3E%5Bslp_location+phone+++++++++suffix++++br%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_fax%22%3E%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_fax+++++ifset+++fax++%5D%3C%2Fspan%3E%5Bslp_location+fax+++++++++++suffix++++br%5D%3Cspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_description%22%3E%3Cspan+id%3D%22slp_bubble_description%22%3E%5Bhtml+br+ifset+description%5D%0D%0A++++%5Bslp_location+description+raw%5D%3C%2Fspan%3E%5Bhtml+br+ifset+description%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_hours%22%3E%5Bhtml+br+ifset+hours%5D%0D%0A++++%3Cspan+class%3D%22location_detail_label%22%3E%5Bslp_option+++label_hours+++ifset+++hours%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+class%3D%22location_detail_hours%22%3E%5Bslp_location+hours+++++++++suffix++++br%5D%3C%2Fspan%3E%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_bubble_img%22%3E%5Bhtml+br+ifset+img%5D%0D%0A++++%5Bslp_location+image+++++++++wrap++++img%5D%3C%2Fspan%3E%0D%0A++++%3Cspan+id%3D%22slp_tags%22%3E%5Bslp_location+tags%5D%3C%2Fspan%3E%0D%0A++++%3C%2Fdiv%3E&options%5Bignore_radius%5D=0&options%5Bmap_domain%5D=maps.google.com&options%5Bno_autozoom%5D=0&options%5Bno_homeicon_at_start%5D=1&options%5Bradius_behavior%5D=always_use&options%5Bresults_layout%5D=%3Cdiv+id%3D%22slp_results_%5Bslp_location+id%5D%22+class%3D%22results_entry+location_primary+%5Bslp_location+featured%5D%22%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_left_column%22+++id%3D%22slp_left_cell_%5Bslp_location+id%5D%22+++%3E%0D%0A++++++++++++%0D%0A++++++++++++%3Cspan+class%3D%22location_name%22%3E%5Bslp_location+name%5D+%5Bslp_location+uml_buttons%5D+%5Bslp_location+gfi_buttons%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22location_distance%22%3E%5Bslp_location+distance+format%3D%22decimal1%22%5D+%5Bslp_option+distance_unit%5D%3C%2Fspan%3E%0D%0A++++++++++++%0D%0A++++++++%3C%2Fdiv%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_center_column+location_secondary%22+id%3D%22slp_center_cell_%5Bslp_location+id%5D%22+%3E%0D%0A++++++++++++%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_street%22%3E%5Bslp_location+address%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_street2%22%3E%5Bslp_location+address2%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_citystatezip%22%3E%5Bslp_location+city_state_zip%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_country%22%3E%5Bslp_location+country%5D%3C%2Fspan%3E%0D%0A%09%09%09%3Cdiv+class%3D%22time-phone%22%3E%0D%0A%09%09%09%3Cdiv+class%3D%22time%22%3E%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_hours%22%3E%3Cspan%3EHours%3C%2Fspan%3E%3A+%5Bslp_location+hours+format+text%5D%3C%2Fspan%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A%09%09%09%3Cdiv+class%3D%22phone-number%22%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_phone%22%3E%3Ca+href%3D%22tel%3A%5Bslp_location+phone%5D%22%3E%5Bslp_location+phone%5D%3C%2Fa%3E%3C%2Fspan%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_fax%22%3E%5Bslp_location+fax%5D%3C%2Fspan%3E%0D%0A++++++++++++++++++++++++%0D%0A++++++++%3C%2Fdiv%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_right_column+location_tertiary%22++id%3D%22slp_right_cell_%5Bslp_location+id%5D%22++%3E%0D%0A++++++++++++%0D%0A++++++++++++%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_contact+slp_result_email%22%3E%5Bslp_location+email_link%5D%3C%2Fspan%3E++++++++++++%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_directions%22%3E%3Ca+href%3D%22https%3A%2F%2F%5Bslp_option+map_domain%5D%2Fmaps%2Fplace%2F%5Bslp_location+location_address%5D%22+target%3D%22_blank%22+class%3D%22storelocatorlink%22%3E%5Bslp_option+label_directions%5D%3C%2Fa%3E%3C%2Fspan%3E%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_website%22%3E%5Bslp_location+web_link+raw%5D%3C%2Fspan%3E%0D%0A++++++++++++%0D%0A++++++++++++%5Bslp_location+pro_tags+raw%5D%0D%0A++++++++++++%5Bslp_location+iconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%5Bslp_location+eventiconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%5Bslp_location+socialiconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%0D%0A++++++++++++%3C%2Fdiv%3E%0D%0A++++%3C%2Fdiv%3E&options%5Bslplus_version%5D=4.7.2&options%5Buse_sensor%5D=0&options%5Bmessage_no_api_key%5D=This+site+most+likely+needs+a+Google+Maps+API+key.&options%5Bdistance_unit%5D=miles&options%5Bradii%5D=10%2C25%2C50%2C100%2C(2000)%2C500&options%5Bmap_center%5D=900+A+Ave.+East+Seymour%2C+IN%2C+4727&options%5Bmap_center_lat%5D=38.9269&options%5Bmap_center_lng%5D=-85.904492&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&options%5Bmap_type%5D=roadmap&options%5Bmap_home_icon%5D=https%3A%2F%2Frulerfoods.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbox_yellow_home.png&options%5Bmap_end_icon%5D=https%3A%2F%2Frulerfoods.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bimmediately_show_locations%5D=0&options%5Binitial_radius%5D=&options%5Binitial_results_returned%5D=50&options%5Bmessage_no_results%5D=No+locations+found.&options%5Blabel_website%5D=Facebook&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_phone%5D=Phone&options%5Blabel_fax%5D=Fax&options%5Bmap_width%5D=100&options%5Blayout%5D=%3Cdiv+class%3D%22formmap%22%3E%5Bslp_search%5D%3C%2Fdiv%3E%3Cdiv+class%3D%22neartexts%22%3E%0D%0A%09%09%09%09%09%3Ch2%3ELocations%3C%2Fh2%3E%0D%0A%09%09%09%09%09%3C%2Fdiv%3E%3Cdiv+id%3D%22sl_div%22%3E%5Bslp_map%5D%5Bslp_results%5D%3C%2Fdiv%3E&options%5Bmaplayout%5D=%5Bslp_mapcontent%5D%5Bslp_maptagline%5D&options%5Bresultslayout%5D=%3Cdiv+id%3D%22slp_results_%5Bslp_location+id%5D%22+class%3D%22results_entry+location_primary+%5Bslp_location+featured%5D%22%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_left_column%22+++id%3D%22slp_left_cell_%5Bslp_location+id%5D%22+++%3E%0D%0A++++++++++++%5Bslp_addon+section%3Dprimary+position%3Dfirst%5D%0D%0A++++++++++++%3Cspan+class%3D%22location_name%22%3E%5Bslp_location+name%5D+%5Bslp_location+uml_buttons%5D+%5Bslp_location+gfi_buttons%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22location_distance%22%3E%5Bslp_location+distance_1%5D+%5Bslp_location+distance_unit%5D%3C%2Fspan%3E%0D%0A++++++++++++%5Bslp_addon+section%3Dprimary+position%3Dlast%5D%0D%0A++++++++%3C%2Fdiv%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_center_column+location_secondary%22+id%3D%22slp_center_cell_%5Bslp_location+id%5D%22+%3E%0D%0A++++++++++++%5Bslp_addon+section%3Dsecondary+position%3Dfirst%5D%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_street%22%3E%5Bslp_location+address%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_street2%22%3E%5Bslp_location+address2%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_citystatezip%22%3E%5Bslp_location+city_state_zip%5D%3C%2Fspan%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_country%22%3E%5Bslp_location+country%5D%3C%2Fspan%3E%0D%0A%09%09%09%3Cdiv+class%3D%22time-phone%22%3E%0D%0A%09%09%09%3Cdiv+class%3D%22time%22%3E%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_hours%22%3E%3Cspan%3EHours%3C%2Fspan%3E%3A+%5Bslp_location+hours%5D%3C%2Fspan%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A%09%09%09%3Cdiv+class%3D%22phone-number%22%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_phone%22%3E%3Ca+href%3D%22tel%3A%5Bslp_location+phone%5D%22%3E%5Bslp_location+phone%5D%3C%2Fa%3E%3C%2Fspan%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A%09%09%09%3C%2Fdiv%3E%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_address+slp_result_fax%22%3E%5Bslp_location+fax%5D%3C%2Fspan%3E%0D%0A++++++++++++%5Bslp_addon+section%3Dsecondary+position%3Dlast%5D++++++++++++%0D%0A++++++++%3C%2Fdiv%3E%0D%0A++++++++%3Cdiv+class%3D%22results_row_right_column+location_tertiary%22++id%3D%22slp_right_cell_%5Bslp_location+id%5D%22++%3E%0D%0A++++++++++++%5Bslp_addon+section%3Dtertiary+position%3Dfirst%5D%0D%0A++++++++++++%0D%0A++++++++++++%3Cspan+class%3D%22slp_result_contact+slp_result_email%22%3E%5Bslp_location+email_link%5D%3C%2Fspan%3E++++++++++++%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_directions%22%3E%3Ca+href%3D%22https%3A%2F%2F%5Bslp_option+map_domain%5D%2Fmaps%2Fplace%2F%5Bslp_location+location_address%5D%22+target%3D%22_blank%22+class%3D%22storelocatorlink%22%3E%5Bslp_location+directions_text%5D%3C%2Fa%3E%3C%2Fspan%3E%0D%0A%09%09%09%3Cspan+class%3D%22slp_result_contact+slp_result_website%22%3E%5Bslp_location+web_link%5D%3C%2Fspan%3E%0D%0A++++++++++++%0D%0A++++++++++++%5Bslp_location+pro_tags%5D%0D%0A++++++++++++%5Bslp_location+iconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%5Bslp_location+eventiconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%5Bslp_location+socialiconarray+wrap%3D%22fullspan%22%5D%0D%0A++++++++++++%5Bslp_addon+section%3Dtertiary+position%3Dlast%5D%0D%0A++++++++++++%3C%2Fdiv%3E%0D%0A++++%3C%2Fdiv%3E&options%5Bsearchlayout%5D=%3Cdiv+id%3D%22address_search%22+class%3D%22slp+search_box%22%3E%0D%0A++++++++%5Bslp_search_element+add_on+location%3D%22very_top%22%5D%0D%0A++++++++%5Bslp_search_element+input_with_label%3D%22name%22%5D%0D%0A++++++++%5Bslp_search_element+input_with_label%3D%22address%22%5D%0D%0A++++++++%5Bslp_search_element+dropdown_with_label%3D%22city%22%5D%0D%0A++++++++%5Bslp_search_element+dropdown_with_label%3D%22state%22%5D%0D%0A++++++++%5Bslp_search_element+dropdown_with_label%3D%22country%22%5D%0D%0A++++++++%5Bslp_search_element+selector_with_label%3D%22tag%22%5D%0D%0A++++++++%5Bslp_search_element+dropdown_with_label%3D%22category%22%5D%0D%0A++++++++%5Bslp_search_element+dropdown_with_label%3D%22gfl_form_id%22%5D%0D%0A++++++++%5Bslp_search_element+add_on+location%3D%22before_radius_submit%22%5D%0D%0A++++++++%3Cdiv+class%3D%22search_item%22%3E%0D%0A++++++++++++%5Bslp_search_element+dropdown_with_label%3D%22radius%22%5D%0D%0A++++++++++++%5Bslp_search_element+button%3D%22submit%22%5D%0D%0A++++++++%3C%2Fdiv%3E%0D%0A%09%09%0D%0A++++++++%5Bslp_search_element+add_on+location%3D%22after_radius_submit%22%5D%0D%0A++++++++%5Bslp_search_element+add_on+location%3D%22very_bottom%22%5D%0D%0A++++%3C%2Fdiv%3E&options%5Btheme%5D=&options%5Bid%5D=&options%5Bhide_search_form%5D=&options%5Bforce_load_js%5D=0&options%5Bmap_region%5D=us&radius=&tags=&action=csl_ajax_onload"

    session = SgRequests()
    stores = session.post(base_link, headers=headers, data=payload).json()["response"]
    data = []
    locator_domain = "rulerfoods.com"

    for store in stores:
        store = store["data"]
        street_address = (store["sl_address"] + " " + store["sl_address2"]).strip()
        city = store["sl_city"]
        location_name = "Ruler Foods - " + city
        state = store["sl_state"]
        zip_code = store["sl_zip"].replace("46925", "46952")
        country_code = "US"
        store_number = store["sl_id"]
        location_type = "<MISSING>"
        phone = store["sl_phone"]
        hours_of_operation = store["sl_hours"].strip()
        latitude = store["sl_latitude"]
        longitude = store["sl_longitude"]
        link = "https://rulerfoods.com/locations/"

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
