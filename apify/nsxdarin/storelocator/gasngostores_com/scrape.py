import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.gasngostores.com/locations"
    r = session.get(url, headers=headers)
    website = "gasngostores.com"
    typ = "<MISSING>"
    country = "US"
    lat = "<MISSING>"
    lng = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<strong>" in line:
            items = line.split("<strong>")
            for item in items:
                if '</h3><p class=""' in item:
                    name = item.split("<")[0]
                    add = (
                        item.split('</h3><p class="" style="white-space:pre-wrap;">')[1]
                        .split(",")[0]
                        .rsplit(" ", 1)[0]
                    )
                    city = (
                        item.split('</h3><p class="" style="white-space:pre-wrap;">')[1]
                        .split(",")[0]
                        .rsplit(" ", 1)[1]
                    )
                    zc = (
                        item.split('</h3><p class="" style="white-space:pre-wrap;">')[1]
                        .split("<")[0]
                        .rsplit(" ", 1)[1]
                    )
                    state = (
                        item.split('</h3><p class="" style="white-space:pre-wrap;">')[1]
                        .split(",")[1]
                        .strip()
                        .split(" ")[0]
                    )
                    loc = "<MISSING>"
                    store = "<MISSING>"
                    typ = "<MISSING>"
                    hours = item.split(">Hours: ")[1].split("<")[0]
                    try:
                        phone = item.split('Phone: <a href="tel:+')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    if city == "Vista":
                        city = "Buena Vista"
                        add = add.replace(" Buena", "")
                    if city == "Byron":
                        city = "North Byron"
                        add = add.replace(" North", "")
                    if city == "Valley":
                        city = "Fort Valley"
                        add = add.replace(" Fort", "")
                    if city == "Montezuma":
                        zc = "31063"
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
                        url,
                    ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
