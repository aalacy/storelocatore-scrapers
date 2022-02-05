from sgrequests import SgRequests
import re
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = SgLogSetup().get_logger("kentkwik_com")


def fetch_data():
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    }
    locator_domain = "https://kentkwik.com/"

    no = 1
    with SgRequests() as session:
        while True:
            data = (
                "&is_grouped=0&map_id=182317&data_id=182459&id="
                + str(no)
                + '&lt=31.8292887&ln=-102.3555451&per={"title":"Kent Kwik Locations","description":"","dist_sel":0,"dist_cb_status":false,"field_cb_status":true,"country_sel":"","locale":"us","map_type":"TERRAIN","view_sel":"0","groups":null,"groups_mode":1,"mb_style":"1","mb_over":0,"mb_detail":0,"markers_set":"14","max_lat":36.6984807,"max_lon":-96.1120791,"min_lat":30.8936988,"min_lon":-105.9638215,"color_col":null,"postal_col":11,"accuracy_col":12,"locator":"1","render_method":0,"groups_settings":[{"pos":0,"show":true},{"pos":1,"show":true},{"pos":2,"show":true},{"pos":3,"show":true},{"pos":4,"show":true},{"pos":5,"show":true},{"pos":6,"show":true},{"pos":7,"show":true},{"pos":8,"show":true}],"title_display":"1","enable_printing":"1","address_col":-1,"city_col":-1,"state_col":-1,"zip_col":-1,"title_col":-1,"desc_col":-1,"descURL_col":-1,"descIMG_col":-1,"email_col":-1,"country_column":-1,"search_col":-1,"group_header":"Company","clustering_lock":0,"open_menu":0,"mb_override_cluster":0,"show_info_directions":0,"web_target":0,"not_normal_group":0,"dont_bold_description_headers":0,"limit_search":0,"show_all_addresses":0,"map_password":0,"mb_markers_set":"14","lat_col":-1,"long_col":-1,"min_lng":-122.6778424,"max_lng":-73.4119925,"enable_filtering":0,"enable_proximity":0,"enable_directions":"1","map_style":[{"featureType":"road.arterial","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"road.local","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"road.highway","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"water","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"water","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"administrative","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"administrative","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"transit","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"transit","elementType":"labels","stylers":[{"visibility":"on"}]}],"title_description_bar":1,"enable_street_view":"1","enable_satellite_view":"1","remove_roads":0,"map_states":[["snap_view",{"zoom":9,"center_lat":"31.865013","center_lng":"-102.321310","bounds":"30.911938,-104.555655,32.808335,-100.086966","show_group":"[4]","filter_tree":{"type":"and","children":[{"type":"or","col_id":7,"children":[{"type":"literal","ref":[7,"gi","Kent Kwik",1]}]}]}}]],"aggregation":-1,"hide_popup_edit":0,"hide_popup_delete":0,"hide_popup_street_view":0,"hide_popup_directions":0,"hide_popup_proximity":0,"presentation_mode":"1","map_ver":1,"enable_show_location":"1","show_all_when_zoomed":"1","enable_distance_calc":"1","custom_individual_markers":{"0":{"style_type":"custom","style_id":9022,"label":""},"1":{"style_type":"custom","style_id":9022,"label":""},"2":{"style_type":"custom","style_id":9022,"label":""},"3":{"style_type":"custom","style_id":9022,"label":""},"4":{"style_type":"custom","style_id":9022,"label":""},"5":{"style_type":"custom","style_id":9022,"label":""},"6":{"style_type":"custom","style_id":9022,"label":""},"7":{"style_type":"custom","style_id":9023,"label":""},"8":{"style_type":"custom","style_id":9023,"label":""},"9":{"style_type":"custom","style_id":9023,"label":""},"10":{"style_type":"custom","style_id":9024,"label":""},"11":{"style_type":"custom","style_id":9024,"label":""},"12":{"style_type":"custom","style_id":9026,"label":""},"13":{"style_type":"custom","style_id":9026,"label":""},"14":{"style_type":"custom","style_id":9026,"label":""},"15":{"style_type":"custom","style_id":9026,"label":""},"16":{"style_type":"custom","style_id":9027,"label":""},"17":{"style_type":"custom","style_id":9027,"label":""},"18":{"style_type":"custom","style_id":9022,"label":""},"19":{"style_type":"custom","style_id":9022,"label":""},"20":{"style_type":"custom","style_id":9022,"label":""},"21":{"style_type":"custom","style_id":9022,"label":""},"22":{"style_type":"custom","style_id":9022,"label":""},"23":{"style_type":"custom","style_id":9022,"label":""},"24":{"style_type":"custom","style_id":9022,"label":""},"25":{"style_type":"custom","style_id":9022,"label":""},"26":{"style_type":"custom","style_id":9022,"label":""},"27":{"style_type":"custom","style_id":9022,"label":""},"28":{"style_type":"custom","style_id":9022,"label":""},"29":{"style_type":"custom","style_id":9022,"label":""},"30":{"style_type":"custom","style_id":9022,"label":""},"31":{"style_type":"custom","style_id":9022,"label":""},"32":{"style_type":"custom","style_id":9022,"label":""},"33":{"style_type":"custom","style_id":9022,"label":""},"34":{"style_type":"custom","style_id":9022,"label":""},"35":{"style_type":"custom","style_id":9022,"label":""},"36":{"style_type":"custom","style_id":9022,"label":""},"37":{"style_type":"custom","style_id":9022,"label":""},"38":{"style_type":"custom","style_id":9022,"label":""},"39":{"style_type":"custom","style_id":9022,"label":""},"40":{"style_type":"custom","style_id":9022,"label":""},"41":{"style_type":"custom","style_id":9022,"label":""},"42":{"style_type":"custom","style_id":9022,"label":""},"43":{"style_type":"custom","style_id":9022,"label":""},"44":{"style_type":"custom","style_id":9022,"label":""},"45":{"style_type":"custom","style_id":9022,"label":""},"46":{"style_type":"custom","style_id":9022,"label":""},"47":{"style_type":"custom","style_id":9022,"label":""},"48":{"style_type":"custom","style_id":9022,"label":""},"49":{"style_type":"custom","style_id":9022,"label":""},"50":{"style_type":"custom","style_id":9022,"label":""},"51":{"style_type":"custom","style_id":9024,"label":""},"52":{"style_type":"custom","style_id":9024,"label":""},"53":{"style_type":"custom","style_id":9024,"label":""},"54":{"style_type":"custom","style_id":9024,"label":""},"55":{"style_type":"custom","style_id":9024,"label":""},"56":{"style_type":"custom","style_id":9024,"label":""},"57":{"style_type":"custom","style_id":9024,"label":""},"58":{"style_type":"custom","style_id":9024,"label":""},"59":{"style_type":"custom","style_id":9024,"label":""},"60":{"style_type":"custom","style_id":9024,"label":""},"61":{"style_type":"custom","style_id":9024,"label":""},"62":{"style_type":"custom","style_id":9024,"label":""},"63":{"style_type":"custom","style_id":9079,"label":""},"64":{"style_type":"custom","style_id":9079,"label":""},"65":{"style_type":"custom","style_id":9079,"label":""},"66":{"style_type":"custom","style_id":9079,"label":""},"67":{"style_type":"custom","style_id":9079,"label":""},"68":{"style_type":"custom","style_id":9079,"label":""},"69":{"style_type":"custom","style_id":9079,"label":""},"70":{"style_type":"custom","style_id":9079,"label":""},"71":{"style_type":"custom","style_id":9079,"label":""},"72":{"style_type":"custom","style_id":9079,"label":""},"73":{"style_type":"custom","style_id":9079,"label":""},"74":{"style_type":"custom","style_id":9079,"label":""},"75":{"style_type":"custom","style_id":9079,"label":""},"76":{"style_type":"custom","style_id":9079,"label":""},"77":{"style_type":"custom","style_id":9356,"label":""},"78":{"style_type":"custom","style_id":9356,"label":""},"80":{"style_type":"custom","style_id":9358,"label":""},"81":{"style_type":"custom","style_id":9358,"label":""},"82":{"style_type":"custom","style_id":9358,"label":""},"83":{"style_type":"custom","style_id":9358,"label":""},"84":{"style_type":"custom","style_id":9358,"label":""},"85":{"style_type":"custom","style_id":9358,"label":""},"86":{"style_type":"custom","style_id":9358,"label":""},"87":{"style_type":"custom","style_id":9022,"label":""},"88":{"style_type":"custom","style_id":9022,"label":""},"89":{"style_type":"custom","style_id":9022,"label":""},"90":{"style_type":"custom","style_id":9022,"label":""},"91":{"style_type":"custom","style_id":9022,"label":""},"92":{"style_type":"custom","style_id":9022,"label":""},"94":{"style_type":"custom","style_id":9022,"label":""}},"custom_group_markers":{},"custom_group_text_markers":{},"custom_all_marker":{},"numeric_columns":{},"subgroup_cols":{},"boundary_group_settings":{},"advanced_reference_data":[["Avis Lube","Baskin-Robbins","Huddle House","Kent Car Wash","Kent Kwik","Kent Tire","Mr Payroll","Rustic Cafe","%?%"]],"advanced_reference_columns":[7],"additional_columns":[],"legend_not_grouping":0,"remove_highways":0,"remove_highway_labels":0,"remove_road_labels":0,"enable_map_zoom":"1","enable_restrict_bounds":0,"search_just_zoom":0,"split_grouped_markers":0,"add_directions_at_start":0,"zoom_to_user_on_load":0,"territories_on":"1","enable_territories":0,"boundaries_on":"1","enable_location_finder":0,"start_location_finder":0,"group_marker_pie_charts":1,"hide_all_markers":0,"unit_system":0,"heatmaps":{},"enable_heatmaps":0,"enable_boundaries":0,"boundary_to_group":{},"hide_boundary_labels":0,"combine_group_totals":0,"filters_unaffect_boundaries":0,"hide_no_fill_b":0,"hide_territory_labels":0,"marker_label_fs":10,"text_markers_on":0,"text_marker_col":-1,"text_marker_c":"e5e5ff","ss_type":3,"ss_zoom":0,"ss_exact_word":0,"remove_water":0,"remove_water_label":0,"remove_administrative":0,"remove_administrative_label":0,"remove_poi":0,"remove_poi_label":0,"remove_transit":0,"remove_transit_label":0,"map_font_bold":0,"view_sel_last":0,"zoom_to_on_load_admin":0,"search_always_on":0,"proximities_on":"1","hm_on":"1","only_display_legend":0,"address_key_open":0,"group_col":"7","unique_groups_7":["Avis Lube","Baskin-Robbins","Huddle House","Kent Car Wash","Kent Kwik","Kent Tire","Mr Payroll","Rustic Cafe","%?%"],"is_temporary":0,"mb_settings":{"resize_mode":"0","width":"325","content_height":"210","min_auto_width":"318","header_fs":"22","header_fc":"#428BCA","body_c":"#FFF","footer_c":"#5e99d5","footer_fc":"#FFF"},"use_image_markers":0,"gt_whole_names":0,"enable_lasso":0,"legend_not_boundary":0,"deleted_on":null,"clustering_cb_status":"1","mb_piechart":0,"enable_grouping_tool":"1","custom_individual_text_markers":{},"remove_ls":0,"remove_ls_label":0,"label_above_no_num":0,"pub_map_hidden_filter_cols":{}}'
            )
            r = session.post(
                "https://fortress.maptive.com/ver4/data.php?operation=get_bubble_info",
                data=data,
                headers=headers,
            )
            try:
                json_data = r.json()["description"]["json"]
            except:
                continue

            if json_data["address"]:
                latitude = json_data["lat"]
                longitude = json_data["lng"]
                if "Address" in json_data["columnsData"][0]["name"]:
                    street_address = json_data["columnsData"][0]["value"]

                if "City" in json_data["columnsData"][1]["name"]:
                    city = json_data["columnsData"][1]["value"]
                if "State/Province" in json_data["columnsData"][2]["name"]:
                    state = json_data["columnsData"][2]["value"]
                if "Postal Code" in json_data["columnsData"][3]["name"]:
                    zip = json_data["columnsData"][3]["value"]
                country_code = "US"
                if "Location Name" in json_data["columnsData"][5]["name"]:
                    location_name = json_data["columnsData"][5]["value"].strip()

                phone = "<MISSING>"
                try:
                    if "Phone" in json_data["columnsData"][6]["name"]:
                        phone_tag = json_data["columnsData"][6]["value"]
                        phone_list = re.findall(
                            re.compile(".?(\\(?\\d{3}\\D{0,3}\\d{3}D{0,3}\\d{4}).?"),
                            str(phone_tag),
                        )
                        if phone_list:
                            phone = phone_list[0]
                        else:
                            phone = "<MISSING>"
                except:
                    pass

                try:
                    if "Company" in json_data["columnsData"][7]["name"]:
                        location_type = json_data["columnsData"][7]["value"]
                except:
                    if "Huddle House" in location_name:
                        location_type = "Huddle House"
                    else:
                        location_type = "Car Wash"
                try:
                    if "Store Hours" in json_data["columnsData"][8]["name"]:
                        hours_of_operation = json_data["columnsData"][8]["value"]
                except:
                    hours_of_operation = "<MISSING>"
                store_number = " ".join(re.findall(r"\d+", str(location_name)))
                page_url = "https://kentkwik.com/locations-2/"
                if "Mr Payroll" != location_type:
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
                    )

            else:
                break

            no += 1


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
