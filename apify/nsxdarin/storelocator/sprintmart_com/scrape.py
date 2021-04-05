import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("sprintmart_com")


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
    url = "https://www.sprintmart.com/wp-admin/admin-ajax.php?action=csl_ajax_onload&address=&formdata=addressInput%3D&lat=32.3546679&lng=-89.3985283&options%5Bdistance_unit%5D=miles&options%5Bdropdown_style%5D=none&options%5Bignore_radius%5D=0&options%5Bimmediately_show_locations%5D=1&options%5Binitial_radius%5D=500&options%5Blabel_directions%5D=Directions&options%5Blabel_email%5D=Email&options%5Blabel_fax%5D=Fax&options%5Blabel_phone%5D=&options%5Blabel_website%5D=Website&options%5Bloading_indicator%5D=&options%5Bmap_center%5D=Mississippi%2C+USA&options%5Bmap_center_lat%5D=32.3546679&options%5Bmap_center_lng%5D=-89.3985283&options%5Bmap_domain%5D=maps.google.com&options%5Bmap_end_icon%5D=https%3A%2F%2Fsprintmart.com%2Fwp-content%2Fuploads%2F2018%2F01%2FLocationMarker-1-e1516806074512.png&options%5Bmap_home_icon%5D=https%3A%2F%2Fsprintmart.com%2Fwp-content%2Fplugins%2Fstore-locator-le%2Fimages%2Ficons%2Fbulb_lightblue.png&options%5Bmap_region%5D=us&options%5Bmap_type%5D=roadmap&options%5Bno_autozoom%5D=0&options%Buse_sensor%5D=false&options%5Bzoom_level%5D=6&options%5Bzoom_tweak%5D=0&radius=5000"
    r = session.get(url, headers=headers)
    website = "sprintmart.com"
    typ = "<MISSING>"
    country = "US"
    loc = "https://www.sprintmart.com/locations"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"sl_id":"' in line:
            items = line.split('"sl_id":"')
            for item in items:
                if '"sl_store":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"sl_store":"')[1].split('"')[0]
                    add = item.split('"sl_address":"')[1].split('"')[0]
                    city = item.split('"sl_city":"')[1].split('"')[0]
                    state = item.split('"sl_state":"')[1].split('"')[0]
                    zc = item.split('"sl_zip":"')[1].split('"')[0]
                    lat = item.split('"sl_latitude":"')[1].split('"')[0]
                    lng = item.split('"sl_longitude":"')[1].split('"')[0]
                    phone = item.split('"sl_phone":"')[1].split('"')[0]
                    if phone == "":
                        phone = "<MISSING>"
                    yield [
                        website,
                        loc,
                        name,
                        add,
                        city,
                        state,
                        zc,
                        country,
                        store,
                        phone,
                        typ,
                        lat,
                        lng,
                        hours,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
