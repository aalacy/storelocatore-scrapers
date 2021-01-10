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
    url = "https://www.simon.com/search"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '{"PropertyType":' in line:
            items = line.split('{"PropertyType":')
            for item in items:
                if '"City":"' in item:
                    typ = "Simon Mall"
                    website = "simon.com"
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    loc = (
                        "https://www.simon.com/mall/"
                        + item.split('"MallShortName":"')[1].split('"')[0]
                    )
                    hours = ""
                    r2 = session.get(loc, headers=headers)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if '"HoursOutlook":{"' in line2:
                            hours = (
                                line2.split('"HoursOutlook":{"')[1]
                                .split('"},"Hours":')[0]
                                .replace('","', "; ")
                                .replace('":"Open', ":")
                                .replace('":"Abierto', ":")
                            )
                    store = item.split('"Id":')[1].split(",")[0]
                    country = item.split('"CountryName":"')[1].split('"')[0]
                    if country == "CANADA":
                        country = "CA"
                    if country == "UNITED STATES":
                        country = "US"
                    add = (
                        item.split('{"Address1":"')[1].split('"')[0]
                        + " "
                        + item.split('"Address2":"')[1].split('"')[0]
                    )
                    add = add.strip()
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"StateCode":"')[1].split('"')[0]
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    name = item.split('"DisplayName":"')[1].split('"')[0]
                    try:
                        phone = item.split('"PhoneNumber":{"Origin":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    if hours == "":
                        hours = "<MISSING>"
                    if country == "CA" or country == "US":
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
