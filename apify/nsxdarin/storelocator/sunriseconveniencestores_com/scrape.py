import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    url = "https://sunriseconveniencestores.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"
    website = "sunriseconveniencestores.com"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '"map_id":"' in line:
            items = line.split('"map_id":"')
            for item in items:
                if '"address":"' in item:
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    addinfo = (
                        addinfo.replace(" MI", ", MI")
                        .replace(" Michigan", ", Michigan")
                        .replace(",,", ",")
                    )
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip()
                    zc = "<MISSING>"
                    if '"tel:+1' in item:
                        phone = item.split('"tel:+1')[1].split('"')[0]
                    else:
                        phone = "<MISSING>"
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    loc = "<MISSING>"
                    title = item.split('"title":"')[1].split('"')[0]
                    country = "US"
                    typ = "<MISSING>"
                    if title == "":
                        name = "Marathon"
                    else:
                        if "<a href" in item.split('"title":"')[1]:
                            loc = "https://sunriseconveniencestores.com/" + item.split(
                                '"title":"<a href=\\"'
                            )[1].split('\\"')[0].replace("\\", "")
                            name = (
                                item.split('"title":"')[1].split('">')[1].split("<")[0]
                            )
                        else:
                            loc = "<MISSING>"
                            name = item.split('"title":"')[1].split('"')[0]
                    loc = loc.replace(
                        "http://www.sunriseconveniencestores.com/", ""
                    ).replace(".com//", ".com/")
                    phone = phone.replace("\\", "").replace("n", "")
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
