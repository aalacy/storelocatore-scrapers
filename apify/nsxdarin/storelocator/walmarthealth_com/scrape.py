import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("walmarthealth_com")


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


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=50,
    max_search_results=25,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": ".AspNetCore.Session=CfDJ8KqiTC3ZUV5LnHOBI6LMKZ0jQmMaBZfUsWbrK0Rjbi%2F3xEStH%2BEkI0VKkk1Da6c54e2VQXutcr7RCAopy26JlXPUQXX5eMrUft52pQC%2BQfpfXmamvWn1fjK9b1c%2Fn3Ra6Ug35K1VXuWNOUpaJJTVL%2FhI6lh4Yb1HwgKBRzGtaTuA; _ga=GA1.2.730439241.1624472883; _gid=GA1.2.779310344.1624472883; .AspNetCore.Antiforgery.h2Cz46UegIE=CfDJ8KqiTC3ZUV5LnHOBI6LMKZ2L_mFeyn_PLFDJ7-OsLPSBSyYjJcQeGuOt71Af5Sgux6MV75sYPqtJpXEJynWCiJiYpL_IPFTa0EwQC0VERiRmRLraslJE11CSkVUVLFs4oQ1dmIdZpqMtV1b9_bcuAuo; _gat_gtag_UA_139368345_1=1",
}


def fetch_data():
    ids = []
    country = "US"
    for zipcode in search:
        typ = "<MISSING>"
        url = "https://walmarthealth.com/Home/LocationSelection"
        payload = {
            "ZipCode": zipcode,
            "__RequestVerificationToken": "CfDJ8KqiTC3ZUV5LnHOBI6LMKZ2rA5-yQS1K9YMO0zqQdc0zA8KZWsb20FNQzsu_vVz_Ft5oBey39xPqx18z9IYzEAalF8OiZaqldUTr8qYha3j4X95b-QEuJhm8c4LmIvGQnVPXrxnq6CRO0Gme7Rt9OW4",
        }
        logger.info(("Pulling Postal Code %s..." % zipcode))
        session = SgRequests()
        r = session.post(url, headers=headers, data=payload)
        lines = r.iter_lines()
        website = "walmarthealth.com"
        for line in lines:
            line = str(line.decode("utf-8"))
            if '<h1 class="page-title"' in line:
                name = line.split('">')[1].split("<")[0]
                store = name.rsplit(" ", 1)[1]
                lat = "<MISSING>"
                lng = "<MISSING>"
                phone = "<MISSING>"
                hours = "<MISSING>"
                loc = "<MISSING>"
            if '<text class="sub-title">' in line:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                add = g.split(">")[1].split("<")[0].strip()
                city = h.split(">")[1].split(",")[0].strip().replace("\t", "")
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.rsplit(" ", 1)[1].split("<")[0]
            if '<div class="location-scheduling-container">' in line:
                if store not in ids:
                    ids.append(store)
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
