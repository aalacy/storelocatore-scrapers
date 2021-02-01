import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("stuartweitzman_com")


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
    Found = False
    states = []
    r = session.get(
        "https://www.stuartweitzman.com/service/store_locator/", headers=headers
    )
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ">State</option>" in line:
            Found = True
        if Found and "</select>" in line:
            Found = False
        if Found and '<option value="' in line and ">State<" not in line:
            states.append(line.split('<option value="')[1].split('"')[0])
    url = "https://www.stuartweitzman.com/ajax.aspx"
    for state in states:
        logger.info(state)
        payload = {
            "F": "StoreLookup",
            "SiteId": "1",
            "Country": "US",
            "State": state,
            "Zip": "Zip Code",
            "UseProximity": "1",
        }
        r2 = session.post(url, headers=headers, data=payload)
        website = "stuartweitzman.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Address":"' in line2:
                items = line2.split('"Address":"')
                for item in items:
                    if '{"Success":true' not in item:
                        add = item.split('"Address1":"')[1].split('"')[0]
                        try:
                            add = (
                                add + " " + item.split('"Address2":"')[1].split('"')[0]
                            )
                        except:
                            pass
                        add = add.strip()
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('"State":"')[1].split('"')[0]
                        zc = item.split('"Zip":"')[1].split('"')[0]
                        phone = item.split('"Phone":"')[1].split('"')[0]
                        hours = item.split('"StoreHours":"')[1].split('"')[0]
                        name = item.split('"Name":"')[1].split('"')[0]
                        name = name + " " + item.split('"Name2":"')[1].split('"')[0]
                        name = name.strip()
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                        loc = "<MISSING>"
                        store = "<MISSING>"
                        hours = (
                            hours.replace("<br />", "")
                            .replace("\\n\\n", "; ")
                            .replace("<div>", "")
                            .replace("</div>", "")
                            .strip()
                            .replace("  ", " ")
                        )
                        hours = (
                            hours.replace("<p>", "")
                            .replace("\\n", "")
                            .replace("</p", "")
                        )
                        if phone == "":
                            phone = "<MISSING>"
                        if hours == "":
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
    payload = {
        "F": "StoreLookup",
        "SiteId": "1",
        "Country": "CA",
        "State": "",
        "Zip": "Zip Code",
        "UseProximity": "1",
    }
    r2 = session.post(url, headers=headers, data=payload)
    website = "stuartweitzman.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line2 in r2.iter_lines():
        line2 = str(line2.decode("utf-8"))
        if '"Address":"' in line2:
            items = line2.split('"Address":"')
            for item in items:
                if '{"Success":true' not in item:
                    add = item.split('"Address1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"Address2":"')[1].split('"')[0]
                    except:
                        pass
                    add = add.strip()
                    city = item.split('"City":"')[1].split('"')[0]
                    state = "<MISSING>"
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    hours = item.split('"StoreHours":"')[1].split('"')[0]
                    name = item.split('"Name":"')[1].split('"')[0]
                    name = name + " " + item.split('"Name2":"')[1].split('"')[0]
                    name = name.strip()
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    loc = "<MISSING>"
                    store = "<MISSING>"
                    hours = (
                        hours.replace("<br />", "")
                        .replace("\\n\\n", "; ")
                        .replace("<div>", "")
                        .replace("</div>", "")
                        .strip()
                        .replace("  ", " ")
                    )
                    hours = (
                        hours.replace("<p>", "").replace("\\n", "").replace("</p", "")
                    )
                    if phone == "":
                        phone = "<MISSING>"
                    if hours == "":
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
    payload = {
        "F": "StoreLookup",
        "SiteId": "1",
        "Country": "GB",
        "State": "",
        "Zip": "Zip Code",
        "UseProximity": "1",
    }
    r2 = session.post(url, headers=headers, data=payload)
    website = "stuartweitzman.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line2 in r2.iter_lines():
        line2 = str(line2.decode("utf-8"))
        if '"Address":"' in line2:
            items = line2.split('"Address":"')
            for item in items:
                if '{"Success":true' not in item:
                    add = item.split('"Address1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"Address2":"')[1].split('"')[0]
                    except:
                        pass
                    add = add.strip()
                    city = item.split('"City":"')[1].split('"')[0]
                    state = "<MISSING>"
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    hours = item.split('"StoreHours":"')[1].split('"')[0]
                    name = item.split('"Name":"')[1].split('"')[0]
                    name = name + " " + item.split('"Name2":"')[1].split('"')[0]
                    name = name.strip()
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    loc = "<MISSING>"
                    store = "<MISSING>"
                    hours = (
                        hours.replace("<br />", "")
                        .replace("\\n\\n", "; ")
                        .replace("<div>", "")
                        .replace("</div>", "")
                        .strip()
                        .replace("  ", " ")
                    )
                    hours = (
                        hours.replace("<p>", "").replace("\\n", "").replace("</p", "")
                    )
                    if phone == "":
                        phone = "<MISSING>"
                    if hours == "":
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
