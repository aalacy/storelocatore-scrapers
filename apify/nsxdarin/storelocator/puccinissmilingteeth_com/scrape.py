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
    url = "https://www.puccinispizzapasta.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "puccinissmilingteeth.com"
    lat = "<MISSING>"
    country = "US"
    lng = "<MISSING>"
    hours = "<MISSING>"
    store = "<MISSING>"
    typ = "<MISSING>"
    lurl = "https://www.puccinispizzapasta.com/locations"
    zc = "<MISSING>"
    name = "West Lafayette"
    add = "300 Brown St"
    city = "West Lafayette"
    state = "IN"
    zc = "47906"
    phone = "7657465000"
    yield [
        website,
        lurl,
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
    for line in r.iter_lines(decode_unicode=True):
        if "INDIANAPOLIS, IN<br /></strong>" in line:
            line = line.replace("</a>Oaklandon", "</a><strong>Oaklandon")
            items = line.split("<strong>")
            state = "IN"
            city = "Indianapolis"
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = "puccinissmilingteeth.com"
                    name = item.split("<")[0]
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    typ = "<MISSING>"
                    lurl = "https://www.puccinispizzapasta.com/locations"
                    rawadd = (
                        item.split('target="_blank">')[1]
                        .split("tel:")[1]
                        .split(">")[3]
                        .split("<")[0]
                    )
                    add = rawadd.split(",")[0]
                    zc = rawadd.rsplit(" ", 1)[1]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = "US"
                    name = name.replace(" at ", "")
                    if "86th St" in add:
                        name = "Greenbriar"
                    yield [
                        website,
                        lurl,
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
        if "LEXINGTON, KY<br /></strong>" in line:
            items = line.split("<strong>")
            state = "KY"
            city = "Lexington"
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = "puccinissmilingteeth.com"
                    name = item.split("<")[0]
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    typ = "<MISSING>"
                    lurl = "https://www.puccinispizzapasta.com/locations"
                    rawadd = (
                        item.split('target="_blank">')[1]
                        .split("tel:")[1]
                        .split(">")[3]
                        .split("<")[0]
                    )
                    add = rawadd.split(",")[0]
                    zc = rawadd.rsplit(" ", 1)[1]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = "US"
                    add = add.replace("&rsquo;", "'")
                    if "86th St" in add:
                        name = "Greenbriar"
                    yield [
                        website,
                        lurl,
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
        if "WEST LAFAYETTE, IN<br /></strong>" in line:
            items = line.split("<strong>")
            state = "IN"
            city = "West Lafayette"
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = "puccinissmilingteeth.com"
                    name = item.split("<")[0]
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    typ = "<MISSING>"
                    lurl = "https://www.puccinispizzapasta.com/locations"
                    rawadd = (
                        item.split('target="_blank">')[1]
                        .split("tel:")[1]
                        .split(">")[3]
                        .split("<")[0]
                    )
                    add = rawadd.split(",")[0]
                    zc = rawadd.rsplit(" ", 1)[1]
                    add = item.split('target="_blank">')[1].split("<")[0]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = "US"
                    if "86th St" in add:
                        name = "Greenbriar"
                    yield [
                        website,
                        lurl,
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
