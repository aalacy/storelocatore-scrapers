import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("regency_hyatt_com")


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
    url = "https://www.hyatt.com/explore-hotels/service/hotels"
    r = session.get(url, headers=headers, timeout=60, stream=True)
    website = "regency.hyatt.com"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"spiritCode":"' in line:
            items = line.split('"spiritCode":"')
            for item in items:
                if '"brand":{"key":"' in item:
                    phone = "<MISSING>"
                    name = item.split('"name":"')[1].split('"')[0]
                    if "Hyatt Regency" in name:
                        CS = False
                        loc = (
                            "https://www.hyatt.com"
                            + item.split('"url":"https://www.hyatt.com')[1].split('"')[
                                0
                            ]
                        )
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split("}")[0]
                        typ = (
                            item.split('"brand":{"key":"')[1]
                            .split('"label":"')[1]
                            .split('"')[0]
                        )
                        store = item.split('"')[0]
                        country = item.split('"country":{"key":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split('"zipcode":"')[1].split('"')[0]
                        add = item.split('"addressLine1":"')[1].split('"')[0]
                        try:
                            add = (
                                add
                                + " "
                                + item.split('"addressLine2":"')[1].split('"')[0]
                            )
                        except:
                            pass
                        try:
                            state = item.split('"stateProvince":{"key":"')[1].split(
                                '"'
                            )[0]
                        except:
                            state = "<MISSING>"
                        zc = item.split('"zipcode":"')[1].split('"')[0]
                        if loc == "":
                            loc = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        if typ == "":
                            typ = "<MISSING>"
                        logger.info(loc)
                        try:
                            r2 = session.get(loc, headers=headers)
                            for line2 in r2.iter_lines():
                                line2 = str(line2.decode("utf-8"))
                                if (
                                    '<span class="opening-date' in line2
                                    and "Opening 20" in line2
                                ):
                                    CS = True
                                if (
                                    "and beyond" in line2
                                    and "Now accepting reservations" in line2
                                ):
                                    CS = True
                                if '"telephone":"' in line2:
                                    phone = line2.split('"telephone":"')[1].split('"')[
                                        0
                                    ]
                        except:
                            pass
                        if country == "GB" or country == "CA" or country == "US":
                            if "Club Maui, " in name:
                                name = "Hyatt Residence Club Maui, Kaanapali Beach"
                            if CS:
                                name = name + " - Coming Soon"
                            if "Salt Lake City" in name:
                                hours = "Coming Soon"
                            else:
                                hours = "<MISSING>"
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
