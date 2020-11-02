import csv
from sgrequests import SgRequests
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cellularsales_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    countries = []

    key_set = set([])
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 500.0
    # i=1
    coord = search.next_coord()

    while coord:
        lati = coord[0]
        longi = coord[1]
        url = "https://www.cellularsales.com/wp-admin/admin-ajax.php?action=store_search&lat=" + str(
            lati) + "&lng=" + str(longi) + "&max_results=25&search_radius=500"
        #logger.info(url)
        r = session.get(url)
        allocs = r.json()
        result_coords = []
        for al in allocs:
            s = al['address']+" "+al['address2'].strip()
            c = al["city"]
            st = al["state"]
            z = al["zip"].split("-")[0].strip()
            if len(z) == 4:
                z="0"+z

            key = s + c + st + z
            if key in key_set:
                continue
            else:
                key_set.add(key)
            page_url.append(url)
            street.append(s)
            locs.append(al["store"])
            ids.append(al["id"])
            cities.append(c)
            states.append(st)
            zips.append(z)
            lat.append(al["lat"])
            long.append(al["lng"])
            phones.append(al["phone"])
            try:
                tim = al["hours"].split('class="wpsl-opening-hours">')[1].replace("</time></td></tr>", " ").replace(
                    "</td><td><time>", " ").replace("</table>", "").replace("<tr><td>", " ").replace("</td></tr>", " ").replace(
                    "</td><td>", " ").strip()
            except:
                tim="<MISSING>"
            timing.append(tim)
            result_coords.append((al["lat"], al["lng"]))
        if len(allocs) < MAX_RESULTS:
            logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(allocs) == MAX_RESULTS:
            logger.info("max count update")
            search.max_count_update(result_coords)
        coord = search.next_coord()
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.cellularsales.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append('US')
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
