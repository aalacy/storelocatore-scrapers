import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("deli-delicious_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    locs = []
    coords = []
    url = "https://app.mapply.net/front-end/iframe.php?api_key=mapply.1912a876a35b8b709f3f1be5fa28f2b2&id=6eae593f-03dd-4dd6-bd8d-12e94a173fdf&ga=0&msid=00000000-0000-0000-0000-000000000000&spmid=51fbe951-f66f-43e9-99cc-0e98d060d71c&pgid=6eae593f-03dd-4dd6-bd8d-12e94a173fdf&siteid=7316a0f9-bfb1-420e-bf72-c4cd78ecedec&locale=en&pid=3426a993-ea79-433c-a715-d4493d114760"
    r = session.get(url, headers=headers)
    website = "deli-delicious.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "{lat: " in line and "id:2503388, marker_colour" in line:
            items = line.split("{lat: ")
            for item in items:
                if ", lng:" in item:
                    lid = item.split(", id:")[1].split(",")[0]
                    lidlat = item.split(",")[0]
                    lidlng = item.split(", lng: ")[1].split(",")[0]
                    coords.append(lid + "|" + lidlat + "|" + lidlng)
        if "onmouseover='hoverStart(" in line:
            items = line.split("onmouseover='hoverStart(")
            for item in items:
                if "onmouseout='hoverStop(" in item:
                    locs.append(item.split(")")[0])
    for loc in locs:
        logger.info(loc)
        for coord in coords:
            if coord.split("|")[0] == loc:
                lat = coord.split("|")[1]
                lng = coord.split("|")[2]
        lurl = (
            "https://app.mapply.net/front-end//get_store_info.php?api_key=mapply.1912a876a35b8b709f3f1be5fa28f2b2&data=detailed&store_id="
            + loc
        )
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<span class='name'>" in line2:
                name = line2.split("<span class='name'>")[1].split("<")[0].strip()
                store = loc
                loc = "<MISSING>"
                add = line2.split("<span class='address'>")[1].split("<")[0].strip()
                city = line2.split("<span class='city'>")[1].split("<")[0].strip()
                state = (
                    line2.split("<span class='prov_state'>")[1].split("<")[0].strip()
                )
                zc = line2.split("<span class='postal_zip'>")[1].split("<")[0].strip()
                try:
                    phone = (
                        line2.split("><span class='phone'>")[1].split("<")[0].strip()
                    )
                except:
                    phone = "<MISSING>"
                try:
                    hours = (
                        line2.split("<span class='hours'>")[1]
                        .split("<\\/span>")[0]
                        .strip()
                        .replace("day<br \\/>", "day: ")
                        .replace("<br \\/>", "; ")
                    )
                except:
                    hours = "<MISSING>"
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
