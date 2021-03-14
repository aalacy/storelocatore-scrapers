import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("virginmobile_ca")


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
    ids = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=None,
        max_search_results=20,
    )
    for lat, lng in search:
        session = SgRequests()
        logger.info(str(lat) + "-" + str(lng) + "...")
        url = (
            "https://virgin.know-where.com/virginmobile/cgi/selection?lang=en&ll="
            + str(lat)
            + "%2C"
            + str(lng)
            + "&stype=ll&async=results"
        )
        r = session.get(url, headers=headers)
        website = "virginmobile.ca"
        typ = "<MISSING>"
        country = "CA"
        loc = "<MISSING>"
        if r.encoding is None:
            r.encoding = "utf-8"
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            if '<span class="kw-results-FIELD-NAME ultra"' in line:
                name = line.split('font-size:16px; ">')[1].split("<")[0].strip()
            if '<td class="kw-results-info" data-kwsite="' in line:
                store = line.split('data-kwsite="')[1].split('"')[0]
                add = ""
                city = ""
                csz = ""
                city = ""
                zc = ""
                phone = ""
                state = ""
                hours = ""
                name = ""
            if '-address" >' in line:
                add = line.split('-address" >')[1].split("<")[0]
            if 'city-state">' in line:
                csz = line.split('city-state">')[1].split("<")[0].strip()
                zc = csz.rsplit(" ", 1)[1]
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().rsplit(" ", 1)[0]
            if '<i class="fa fa-phone"></i>' in line:
                phone = (
                    line.split('<i class="fa fa-phone"></i>')[1].split("<")[0].strip()
                )
            if 'kw-detail-hours-list-row ">' in line:
                next(lines)
                g = next(lines)
                day = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                g = next(lines)
                g = next(lines)
                g = next(lines)
                ope = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                g = next(lines)
                g = next(lines)
                g = next(lines)
                g = next(lines)
                g = next(lines)
                g = next(lines)
                clo = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                hrs = day + " " + ope + "-" + clo
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
                hours = (
                    hours.replace('<b style="font-weight: bold">', "")
                    .replace("</b>", "")
                    .replace("  ", " ")
                )
            if "Services</h4>" in line:
                if store not in ids:
                    ids.append(store)
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
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
        time.sleep(7)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
