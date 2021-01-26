import csv
from sgrequests import SgRequests

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
    url = "https://api.va.gov/v1/facilities/va?bbox[]=-179&bbox[]=10&bbox[]=-60&bbox[]=70&type=health&page=1&per_page=10000"
    r = session.get(url, headers=headers)
    website = "va.gov"
    typ = "VA Health"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',"type":"' in line:
            items = line.split(',"type":"')
            for item in items:
                if '},"id":"' in item:
                    store = item.split('},"id":"')[1].split('"')[0]
                    try:
                        zc = item.split('{"zip":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    loc = "https://www.va.gov/find-locations/facility/" + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    add = item.split('"address_1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split(',"city":"')[1].split('"')[0]
                    state = item.split(',"state":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"long":')[1].split(",")[0]
                    try:
                        phone = "<MISSING>"
                        phurl = "https://api.va.gov/v1/facilities/va/" + store
                        rp = session.get(phurl, headers=headers)
                        for lineph in rp.iter_lines():
                            lineph = str(lineph.decode("utf-8"))
                            if '"phone":{' in lineph:
                                phinfo = lineph.split('"phone":{')[1].split("}")[0]
                                phone = phinfo.split('"main":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                    hours = (
                        hours + "; Tue: " + item.split('"tuesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Wed: " + item.split('"wednesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Thu: " + item.split('"thursday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Fri: " + item.split('"friday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Sat: " + item.split('"saturday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Sun: " + item.split('"sunday":"')[1].split('"')[0]
                    )
                    if store not in locs:
                        locs.append(store)
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

    url = "https://api.va.gov/v1/facilities/va?bbox[]=-179&bbox[]=10&bbox[]=-60&bbox[]=70&type=benefits&page=1&per_page=10000"
    r = session.get(url, headers=headers)
    website = "va.gov"
    typ = "VA Benefits"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',"type":"' in line:
            items = line.split(',"type":"')
            for item in items:
                if '},"id":"' in item:
                    store = item.split('},"id":"')[1].split('"')[0]
                    try:
                        zc = item.split('{"zip":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    loc = "https://www.va.gov/find-locations/facility/" + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_1":"')[1].split('"')[0]
                    except:
                        add = "<MISSING>"
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    try:
                        state = item.split(',"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"long":')[1].split(",")[0]
                    try:
                        phone = "<MISSING>"
                        phurl = "https://api.va.gov/v1/facilities/va/" + store
                        rp = session.get(phurl, headers=headers)
                        for lineph in rp.iter_lines():
                            lineph = str(lineph.decode("utf-8"))
                            if '"phone":{' in lineph:
                                phinfo = lineph.split('"phone":{')[1].split("}")[0]
                                phone = phinfo.split('"main":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                    hours = (
                        hours + "; Tue: " + item.split('"tuesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Wed: " + item.split('"wednesday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Thu: " + item.split('"thursday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Fri: " + item.split('"friday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Sat: " + item.split('"saturday":"')[1].split('"')[0]
                    )
                    hours = (
                        hours + "; Sun: " + item.split('"sunday":"')[1].split('"')[0]
                    )
                    if store not in locs:
                        locs.append(store)
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

    url = "https://api.va.gov/v1/facilities/va?bbox[]=-179&bbox[]=10&bbox[]=-60&bbox[]=70&type=cemetery&page=1&per_page=10000"
    r = session.get(url, headers=headers)
    website = "va.gov"
    typ = "VA Cemetery"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',"type":"' in line:
            items = line.split(',"type":"')
            for item in items:
                if '},"id":"' in item:
                    store = item.split('},"id":"')[1].split('"')[0]
                    try:
                        zc = item.split('{"zip":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    loc = "https://www.va.gov/find-locations/facility/" + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_1":"')[1].split('"')[0]
                    except:
                        add = "<MISSING>"
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    try:
                        state = item.split(',"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"long":')[1].split(",")[0]
                    try:
                        phone = "<MISSING>"
                        phurl = "https://api.va.gov/v1/facilities/va/" + store
                        rp = session.get(phurl, headers=headers)
                        for lineph in rp.iter_lines():
                            lineph = str(lineph.decode("utf-8"))
                            if '"phone":{' in lineph:
                                phinfo = lineph.split('"phone":{')[1].split("}")[0]
                                phone = phinfo.split('"main":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item.split('"sunday":"')[1].split('"')[0]
                        )
                    except:
                        hours = "<MISSING>"
                    if store not in locs:
                        locs.append(store)
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

    url = "https://api.va.gov/v1/facilities/va?bbox[]=-179&bbox[]=10&bbox[]=-60&bbox[]=70&type=vet_center&page=1&per_page=10000"
    r = session.get(url, headers=headers)
    website = "va.gov"
    typ = "Vet Center"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ',"type":"' in line:
            items = line.split(',"type":"')
            for item in items:
                if '},"id":"' in item:
                    store = item.split('},"id":"')[1].split('"')[0]
                    try:
                        zc = item.split('{"zip":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    loc = "https://www.va.gov/find-locations/facility/" + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_1":"')[1].split('"')[0]
                    except:
                        add = "<MISSING>"
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    try:
                        state = item.split(',"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"long":')[1].split(",")[0]
                    try:
                        phone = "<MISSING>"
                        phurl = "https://api.va.gov/v1/facilities/va/" + store
                        rp = session.get(phurl, headers=headers)
                        for lineph in rp.iter_lines():
                            lineph = str(lineph.decode("utf-8"))
                            if '"phone":{' in lineph:
                                phinfo = lineph.split('"phone":{')[1].split("}")[0]
                                phone = phinfo.split('"main":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        hours = "Mon: " + item.split('"monday":"')[1].split('"')[0]
                        hours = (
                            hours
                            + "; Tue: "
                            + item.split('"tuesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + item.split('"wednesday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + item.split('"thursday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + item.split('"friday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sat: "
                            + item.split('"saturday":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Sun: "
                            + item.split('"sunday":"')[1].split('"')[0]
                        )
                    except:
                        hours = "<MISSING>"
                    if store not in locs:
                        locs.append(store)
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
