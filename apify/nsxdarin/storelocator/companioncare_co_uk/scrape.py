import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "origin": "https://www.companioncare.co.uk",
    "referer": "https://www.companioncare.co.uk/find-a-practice/",
    "authority": "api.woosmap.com",
}

logger = SgLogSetup().get_logger("companioncare_co_uk")


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
    for x in range(1, 1000):
        url = (
            "https://api.woosmap.com/stores/"
            + str(x)
            + "?key=woos-85314341-5e66-3ddf-bb9a-43b1ce46dbdc"
        )
        r = session.get(url, headers=headers)
        website = "companioncare.co.uk"
        typ = "<MISSING>"
        country = "GB"
        store = str(x)
        logger.info("Pulling Store %s..." % str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"store_id":' in line:
                name = line.split('"name": "')[1].split('"')[0]
                phone = line.split('"phone": "')[1].split('"')[0]
                lurl = line.split('"website": "')[1].split('"')[0]
                add = line.split('"lines": ["')[1].split('"]')[0].replace('"', "")
                try:
                    city = line.split('"city": "')[1].split('"')[0]
                except:
                    city = "<MISSING>"
                state = "<MISSING>"
                if city == "<MISSING>":
                    city = add.rsplit(",", 1)[1].strip()
                try:
                    zc = line.split('zipcode": "')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                try:
                    lat = line.split('"coordinates": [')[1].split(",")[0]
                    lng = (
                        line.split('"coordinates": [')[1]
                        .split(",")[1]
                        .strip()
                        .split("]")[0]
                    )
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                try:
                    hours = (
                        "Mon: "
                        + line.split('"1": {"hours": [')[1]
                        .split('"start": "')[1]
                        .split('"')[0]
                        + "-"
                        + line.split('"1": {"hours": [{"end": "')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + line.split('"2": {"hours": [')[1]
                        .split('"start": "')[1]
                        .split('"')[0]
                        + "-"
                        + line.split('"2": {"hours": [{"end": "')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + line.split('"3": {"hours": [')[1]
                        .split('"start": "')[1]
                        .split('"')[0]
                        + "-"
                        + line.split('"3": {"hours": [{"end": "')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + line.split('"4": {"hours": [')[1]
                        .split('"start": "')[1]
                        .split('"')[0]
                        + "-"
                        + line.split('"4": {"hours": [{"end": "')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + line.split('"5": {"hours": [')[1]
                        .split('"start": "')[1]
                        .split('"')[0]
                        + "-"
                        + line.split('"5": {"hours": [{"end": "')[1].split('"')[0]
                    )
                    try:
                        hours = (
                            hours
                            + "; Sat: "
                            + line.split('"6": {"hours": [')[1]
                            .split('"start": "')[1]
                            .split('"')[0]
                            + "-"
                            + line.split('"6": {"hours": [{"end": "')[1].split('"')[0]
                        )
                    except:
                        hours = hours + "; Sat: Closed"
                    try:
                        hours = (
                            hours
                            + "; Sun: "
                            + line.split('"7": {"hours": [')[1]
                            .split('"start": "')[1]
                            .split('"')[0]
                            + "-"
                            + line.split('"7": {"hours": [{"end": "')[1].split('"')[0]
                        )
                    except:
                        hours = hours + "; Sun: Closed"
                except:
                    hours = "<MISSING>"
                try:
                    r2 = session.get(lurl, headers=headers)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if "is temporarily closed" in line2 or "is closed" in line2:
                            if "Chichester is closed" not in line2:
                                hours = "Temporarily Closed"
                except:
                    pass
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
