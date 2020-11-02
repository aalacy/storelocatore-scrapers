import csv
import json
from sgrequests import SgRequests
import sgzip
from tenacity import retry, stop_after_attempt
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('comfortkeepers_ca')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

@retry(stop = stop_after_attempt(7))
def query_zip(postcode):
    headers={'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-length': '1107',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.comfortkeepers.ca',
            'referer': 'https://www.comfortkeepers.ca/local-office-finder/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'}
    data = "action=csl_ajax_onload&address=&formdata=addressInput%3D&lat="+str(postcode[0])+"&lng="+str(postcode[1])+"&options%5Bdistance_unit%5D=km&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=500&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax%3A+&options%5Blabel_phone%5D=Phone%3A+&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=245+Fairview+Mall+Drive++Toronto%2C+Ontario+Canada&options%5Bmap_center_lat%5D="+str(postcode[0])+"&options%5Bmap_center_lng%5D="+str(postcode[1])+"&options%5Bmap_domain%5D=maps.google.ca&options%5Bmap_end_icon%5D=https%3A%2F%2Fwww.comfortkeepers.ca%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_azure.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fwww.comfortkeepers.ca%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_yellow.png&options%5Bmap_region%5D=ca&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%5Buse_sensor%5D=false&options%5Bzoom_level%5D=12&options%5Bzoom_tweak%5D=0&radius=500"
    return session.post("https://www.comfortkeepers.ca/wp-admin/admin-ajax.php", data=data, headers=headers).json()['response']

def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = [ 'ca'])
    MAX_COUNT = 25
    MAX_DISTANCE = 500
    all=[]

    postcode = search.next_coord()
    key_set=set([])
    count=0
    while postcode:
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        results = query_zip(postcode)
        result_coords=[]
        for r in results:
            coords=(r['lat'],r['lng'])
            result_coords.append(coords)
            key=r['city']+r['address']+r['lat']+r['lng']+r['zip']
            if key in key_set:
                continue
            else:
                key_set.add(key)
                count += 1
                loc=r['name']
                street=r['address']+" "+r['address2']
                city=r['city']
                state=r['state']
                zip=r['zip']
                lat=r['lat']
                long=r['lng']
                phone=r['phone']
                id=r['id']
                if  "," in phone:
                    phone=phone.split(",")[-1].strip()
                elif "and" in phone:
                    phone = phone.split("and")[-1].strip()

                all.append([
                    "https://comfortkeepers.ca/",
                    loc,
                    street,
                    city,
                    state,
                    zip,
                    "CA",
                    id,  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    "<MISSING>",  # timing
                    "https://www.comfortkeepers.ca/wp-admin/admin-ajax.php"])
        if len(results) < MAX_COUNT:
            logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(results) == MAX_COUNT:
            logger.info("max count update")
            search.max_count_update(result_coords)

        postcode = search.next_coord()
    logger.info("count = ",count)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
