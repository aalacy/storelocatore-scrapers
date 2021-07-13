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
    url = "https://cdn.shopify.com/s/files/1/0397/6842/4614/t/8/assets/stores-map.js"
    r = session.get(url, headers=headers)
    website = "mothersnutritionalcenter.com"
    typ = "<MISSING>"
    country = "US"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<p><strong>" in line:
            name = line.split("<p><strong>")[1].split("<")[0].replace("\\", "")
            store = name.rsplit(" ", 1)[1]
            hours = line.split("Store Hours: ")[1].split("<")[0].replace(" |", ";")
            add = line.split("</p><p>")[2].split(",")[0].strip().replace('"', "")
            city = line.split("</p><p>")[2].split(",")[1].strip().rsplit(" ", 1)[0]
            state = line.split("</p><p>")[2].split(",")[1].strip().rsplit(" ", 1)[1]
            zc = line.split("?api=1&destination")[1].split("'")[0].rsplit("+", 1)[1]
            lat = line.split("</p>',")[1].split(",")[0].strip()
            lng = line.split("</p>',")[1].split(",")[1].strip()
            phone = "<MISSING>"
            loc = "https://mothersnc.com/pages/stores"
            zc = zc.replace("\\", "").replace("/", "").strip()
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
