import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stateandmain_ca")


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
    url = "https://spreadsheets.google.com/feeds/list/1MUyodpsytUuuYhHJTepJOHdD-uTgd0X5yzZJZqFtYSo/1/public/values?alt=json"
    r = session.get(url, headers=headers)
    website = "stateandmain.ca"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"content":{"type":"text","$t":"storename:' in line:
            items = line.split('"content":{"type":"text","$t":"storename:')
            for item in items:
                if (
                    '{"version":"1.0"' not in item
                    and "When no location selected" not in item
                ):
                    name = item.split(",")[0].strip()
                    lat = item.split("latitude:")[1].split(",")[0].strip()
                    lng = item.split("longitude:")[1].split(",")[0].strip()
                    try:
                        add = item.split("unit:")[1].split(",")[0].strip()
                    except:
                        add = ""
                    add = (
                        add + " " + item.split("streetnumber:")[1].split(",")[0].strip()
                    )
                    add = add.strip()
                    add = add + " " + item.split("street:")[1].split(",")[0].strip()
                    city = item.split("city:")[1].split(",")[0].strip()
                    state = item.split("province:")[1].split(",")[0].strip()
                    zc = item.split("postalcode:")[1].split(",")[0].strip()
                    phone = item.split("phonenumber:")[1].split(",")[0].strip()
                    hours = item.split('"gsx$hours":{"$t":"')[1].split('"},"')[0]
                    store = item.split('"gsx$storenumber":{"$t":"')[1].split('"')[0]
                    loc = "<MISSING>"
                    hours = (
                        hours.replace("\\u003cbr\\u003e\\n", "; ")
                        .replace("\\u0026", "&")
                        .replace(" ;", ";")
                        .replace("\\u003cbr\\u003e", "; ")
                    )
                    if "; \\u" in hours:
                        hours = hours.split("; \\u")[0].strip()
                    if "\\u003cb" in hours:
                        hours = hours.split("\\u003cb")[0].strip()
                    hours = hours.replace("\\n", "")
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
