import csv
from sgrequests import SgRequests
import json
import sgzip

search = sgzip.ClosestNSearch()
search.initialize(country_codes=["us", "ca"])

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}


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
    ids = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        x = coord[0]
        y = coord[1]
        url = "https://www.claires.com/on/demandware.store/Sites-clairesNA-Site/en_US/Stores-GetNearestStores"
        payload = {
            "time": "00:00",
            "page": "storelocator",
            "lat": str(x),
            "lng": str(y),
        }
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        website = "claires.com"
        r = session.post(url, headers=headers, data=payload)
        if '"id":"' in r.content.decode("utf-8"):
            for item in json.loads(r.content)["stores"]:
                hours = ""
                store = item["id"]
                name = item["name"]
                add = item["address1"]
                try:
                    add = add + " " + item["address2"]
                except:
                    pass
                add = add.strip()
                city = item["city"]
                zc = item["postalCode"]
                country = item["country"]
                phone = item["phone"]
                state = "<MISSING>"
                lat = item["coordinates"]["lat"]
                lng = item["coordinates"]["lng"]
                result_coords.append((lat, lng))
                typ = item["business"]
                loc = "https://www.claires.com/us/store-details/?StoreID=" + store
                r2 = session.get(loc, headers=headers)
                lines = r2.iter_lines()
                for line2 in lines:
                    line2 = str(line2.decode("utf-8"))
                    if "<p><strong>" in line2:
                        next(lines)
                        next(lines)
                        next(lines)
                        g = next(lines)
                        g = str(g.decode("utf-8"))
                        state = g.strip().split(" ")[0]
                for day in item["storeHours"]:
                    hrs = (
                        day["day"]
                        + ": "
                        + day["from"].strip()
                        + "-"
                        + day["to"].strip()
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                if store not in ids:
                    ids.append(store)
                    poi = [
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
                    yield poi

        search.max_count_update(result_coords)
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
