import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sharis_com')

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    base_url = "https://sharis.com/"
    conn = http.client.HTTPSConnection("guess.radius8.com")
    headers = {
        'authorization': "R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        'cache-control': "no-cache"
    }
    addresses = []
    
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
  
        
    result_coords = []
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        #logger.info(lat,lng)
    # logger.info("zip_code === " + str(coords))
    # logger.info("ramiang zip =====" + str(search.current_zip))
        data = "address=&formdata=nameSearch%3D%26addressInput%3D%26addressInputCity%3D%26addressInputState%3D%26addressInputCountry%3D%26ignore_radius%3D0&lat="+str(lat)+"&lng="+str(lng)+"&name=&options%5Baddress_autocomplete%5D=none&options%5Bappend_to_search%5D=&options%5Bcity%5D=&options%5Bcity_selector%5D=hidden&options%5Bcountry%5D=&options%5Bcountry_selector%5D=hidden&options%5Bcron_import_recurrence%5D=none&options%5Bcron_import_timestamp%5D=&options%5Bcsv_clear_messages_on_import%5D=1&options%5Bcsv_duplicates_handling%5D=update&options%5Bcsv_file_url%5D=&options%5Bcsv_skip_geocoding%5D=0&options%5Bdefault_comments%5D=0&options%5Bdefault_page_status%5D=publish&options%5Bdefault_trackbacks%5D=0&options%5Bdisable_initial_directory%5D=0&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bgoogle_map_style%5D=&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=1000&options%5Binstalled_version%5D=5.2.1&options%5Blabel_directions%5D=Get+Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=See+Specials&options%5Bload_data%5D=1&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=%2C++&options%5Bmap_center_lat%5D=45.4761412&options%5Bmap_center_lng%5D=-122.8264936&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=%2Fwp-content%2Fuploads%2F2018%2F11%2FSharis_Red_Logo_marker-1.png&options%5Bmap_home_icon%5D=%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fblank.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bmessage_bad_address%5D=Could+not+locate+this+address.+Please+try+a+different+location.&options%5Bmessage_no_results%5D=No+locations+found.&options%5Bno_autozoom%5D=0&options%5Bno_homeicon_at_start%5D=1&options%5Bpage_template%5D=%5Bvc_row%5D%0D%0A%5Bvc_column%5D%0D%0A%3Cimg+src%3D%22%2Fwp-content%2Fuploads%2F2016%2F04%2Fsharis_roseburg_oregon_pie.jpg%22%3E%0D%0A%5B%2Fvc_column%5D%0D%0A%5B%2Fvc_row%5D%0D%0A%0D%0A%5Bvc_row%5D%0D%0A%5Bvc_column+width%3D%221%2F2%22%5D%5Bvc_column_text%5D%0D%0A%3Ch4%3E%3Cstrong%3E%5Bstorepage+field%3Dstore%5D%3C%2Fstrong%3E%3C%2Fh4%3E%0D%0A%5B%2Fvc_column_text%5D%5Bvc_column_text%5D%0D%0A%0D%0A%5Bstorepage+field%3Daddress%5D%0D%0A%5Bstorepage+field%3Daddress2%5D%0D%0A%5Bstorepage+field%3Dcity%5D+%5Bstorepage+field%3Dstate%5D+%5Bstorepage+field%3Dzip%5D%0D%0A%0D%0A%5Bstorepage+field%3Ddescription%5D%0D%0A%3Cbr%2F%3E%0D%0A%3Cspan+class%3D%22hours%22%3ECafe+Hours%3A+%3Cbr%2F%3E%0D%0A%5Bstorepage+field%3Dhours%5D+%0D%0A%3C%2Fspan%3E%3Cbr%2F%3E%0D%0A%3Cspan+class%3D%22hours%22%3EThanksgiving+hours%3A+%5Bstorepage+field%3Dthanksgiving%5D%3C%2Fspan%3E%3Cbr%2F%3E%0D%0A%3Cspan+class%3D%22hours%22%3EChristmas+hours%3A+%5Bstorepage+field%3Dchristmas%5D%3C%2Fspan%3E%3Cbr%2F%3E%0D%0APhone%3A+%5Bstorepage+field%3Dphone%5D%0D%0A%0D%0A%5B%2Fvc_column_text%5D%0D%0A%0D%0A%5Bvc_empty_space%5D%0D%0A%0D%0A%5Bstorepage+field%3Dimage+type%3Dhyperlink+title%3D%22Order+Online%22+class%3D%22eltd-btn+eltd-btn-small+eltd-btn-solid+eltd-btn-custom-hover-bg+eltd-btn-custom-border-hover+eltd-btn-custom-hover-color+gf-btn+eltd-btn-hover-animation+eltd-btn-sweep-from-left%22%5D%0D%0A+%5Bslp_location%5D%0D%0A%5Bvc_empty_space%5D%0D%0A%5Blvca_portfolio+posts_query%3D%22size%3A2%7Corder_by%3Adate%7Cpost_type%3A%2Cpost%7Ccategories%3A78%7Ctags%3A79%22+image_size%3D%22full%22+per_line%3D%221%22+per_line_tablet%3D%221%22+per_line_mobile%3D%221%22+image_linkable%3D%22true%22+post_link_new_window%3D%22true%22+excerpt_length%3D%2225%22+display_excerpt_lightbox%3D%22true%22+read_more_text%3D%22See+Details%22+gutter%3D%2220%22+tablet_gutter%3D%2210%22+tablet_width%3D%22800%22+mobile_gutter%3D%2210%22+mobile_width%3D%22480%22%5D%0D%0A%0D%0A%5Bvc_empty_space%5D%0D%0A%0D%0A%5B%2Fvc_column%5D%0D%0A%0D%0A%5Bvc_column+width%3D%221%2F2%22%5D%0D%0A%0D%0A%0D%0A%5Bstorepage+map%3Dlocation%5D%0D%0A%5Bvc_empty_space%5D%0D%0A%0D%0A+%3Ca+href%3D%22https%3A%2F%2Fmaps.google.com%2Fmaps%3Fdaddr%3D%5Bstorepage+field%3Daddress%5D%2520%5Bstorepage+field%3Dcity%5D%2520%5Bstorepage+field%3Dstate%5D%2520%5Bstorepage+field%3Dzip%5D%22+target%3D%22_blank%22+class%3D%22storelocatorlink+eltd-btn+eltd-btn-small+eltd-btn-solid+eltd-btn-custom-hover-bg+eltd-btn-custom-border-hover+eltd-btn-custom-hover-color+gf-btn+eltd-btn-hover-animation+eltd-btn-sweep-from-left%22%3ETake+Me+There!%3C%2Fa%3E%0D%0A%0D%0A%5B%2Fvc_column%5D%0D%0A%0D%0A%5B%2Fvc_row%5D%0D%0A&options%5Bpages_read_more_text%5D=&options%5Bpages_replace_websites%5D=0&options%5Bpermalink_flush_needed%5D=0&options%5Bpermalink_starts_with%5D=cafe-locations&options%5Bprepend_permalink_blog%5D=1&options%5Bprevent_new_window%5D=0&options%5Bselector_behavior%5D=use_both&options%5Bstate%5D=&options%5Bstate_selector%5D=hidden&options%5Btag_autosubmit%5D=0&options%5Btag_dropdown_first_entry%5D=&options%5Btag_label%5D=&options%5Btag_label+%5D=&options%5Btag_output_processing%5D=hide&options%5Btag_selections%5D=&options%5Btag_selector%5D=none&options%5Btag_show_any%5D=0&options%5Bterritory%5D=&options%5Bterritory_selector%5D=&options%5Buse_nonces%5D=1&options%5Buse_same_window%5D=0&options%5Buse_sensor%5D=0&options%5Bzoom_level%5D=14&options%5Bzoom_tweak%5D=-1&radius=1000&tags=&action=csl_ajax_onload"


        try:

            r = session.post("https://sharis.com/wp-admin/admin-ajax.php", headers=header,data=data).json()
        except:
            continue
        if r['response'] != []:
            data = r['response']
            current_results_len = len(r['response'])
            for val in data:
                locator_domain = base_url
                location_name =  val['name']
                street_address = val['address']
                city = val['city']
                state =  val['state']
                zip =  val['zip']
                country_code = 'US'
                store_number = val['id']
                phone = val['phone']
                if 'phone' in val:
                    phone = val['phone']
                location_type = ''
                latitude = val['lat']
                longitude = val['lng']
                result_coords.append((latitude,longitude))
                hours_of_operation = val['hours'].replace('&lt;br/&gt;',' ')
                if street_address in addresses:
                    continue
                addresses.append(street_address)
                store = []
                result_coords.append((latitude, longitude))
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation.replace("&lt;/br&gt;","").replace(" \r\nThanksgiving &amp; Christmas:","") if hours_of_operation.replace("&lt;/br&gt;","").replace(" \r\nThanksgiving &amp; Christmas:","") else '<MISSING>')
                store.append('<MISSING>')
                #logger.info("===============", str(store))
                # return_main_object.append(store)
                yield store
      
        if current_results_len < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
