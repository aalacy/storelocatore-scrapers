import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("holidayinnclubvacations_com")


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
    for x in range(1, 4):
        url = "https://holidayinnclub.com/api/resorts?page=" + str(x)
        r = session.get(url, headers=headers)
        website = "holidayinnclubvacations.com"
        country = "US"
        typ = "Hotel"
        hours = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"_content_type_uid":"' in line:
                items = line.split('"_content_type_uid":"')
                for item in items:
                    if '{"entries":' not in item:
                        name = item.split('"displayTitle":"')[1].split('"')[0]
                        loc = (
                            "https://holidayinnclub.com/explore-resorts/"
                            + item.split(',"resortSlugs":"')[1].split('"')[0]
                        )
                        phone = item.split('{"phoneNumber":"')[1].split('"')[0]
                        add = item.split('"address":"')[1].split("\\n")[0]
                        city = item.split('"destination":{"displayTitle":"')[1].split(
                            ","
                        )[0]
                        state = (
                            item.split('"destination":{"displayTitle":"')[1]
                            .split(",")[1]
                            .split('"')[0]
                            .strip()
                        )
                        zc = (
                            item.split('"address":"')[1].split('"')[0].rsplit(" ", 1)[1]
                        )
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split("}")[0]
                        store = "<MISSING>"
                        if "Apple Mountain Resort" in name:
                            city = "Clarkesville"
                            state = "Georgia"
                        if "Coming Soon" not in item:
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
