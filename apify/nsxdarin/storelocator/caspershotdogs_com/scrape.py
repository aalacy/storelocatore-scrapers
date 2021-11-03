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
    url = "https://caspershotdogs.com/pages/locations"
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    name = ""
    for line in lines:
        if "<h3>Caspers" in line and "Caspers Albany" not in line:
            store = "<MISSING>"
            website = "caspershotdogs.com"
            typ = "Restaurant"
            name = line.split("<h3>")[1].split("<")[0]
            g = next(lines)
            add = g.split('<p><a href="">')[1].split("<")[0].strip()
            country = "US"
            csz = g.split("br>")[1].split("<")[0].strip()
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.rsplit(" ", 1)[1]
            hours = "<MISSING>"
            loc = "<MISSING>"
        if "ll=" in line and '<button><svg class="' in line and name != "":
            lat = line.split("ll=")[1].split(",")[0]
            lng = line.split("ll=")[1].split(",")[1].split("&")[0]
            if "Dublin" in name:
                phone = "(925) 828-2224"
            if "21670 Foothill" in add:
                phone = "(510) 581-9064"
            if "951 C" in add:
                phone = "(510) 537-7300"
            if "Oakland" in name:
                phone = "(510) 652-1668"
            if "Pleasant Hill" in name:
                phone = "(925) 687-6030"
            if "Richmond" in name:
                phone = "(510) 235-6492"
            if "Walnut" in name:
                phone = "(925) 930-9154"
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
