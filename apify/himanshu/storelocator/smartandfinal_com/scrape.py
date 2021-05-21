import csv
from sgrequests import SgRequests
from sglogging import sglog
import cloudscraper


DOMAIN = "smartandfinal.com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def set_headers(scraper, headers):
    init_url = "https://www.smartandfinal.com/proxy/init"
    r = scraper.post(init_url, headers=headers)
    csrf_token = r.json()["token"]
    scraper.cookies["has_js"] = "1"
    scraper.cookies["XSRF-TOKEN"] = csrf_token
    headers["x-csrf-token"] = csrf_token
    cookies = []
    for cookie in scraper.cookies:
        cookies.append("{}={}".format(cookie.name, cookie.value))
    headers["cookie"] = "; ".join(cookies)
    return headers


def fetch_data():

    addresses = []

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,la;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://www.smartandfinal.com/stores/?coordinates=22.056438388643095,167.97404364999997&zoom=2",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    }

    session = SgRequests()
    scraper = cloudscraper.create_scraper(sess=session)
    new_headers = set_headers(scraper, headers)
    url = "https://www.smartandfinal.com/proxy/store/getall?store_type_ids=1,2,3"
    r = scraper.get(url, headers=new_headers)
    data = r.json()
    for loc in data["stores"]:
        store_number = loc["store_number"]
        location_type = ""
        country_code = ""
        hours_of_operation = ""
        phone = ""
        dictionary = {}
        weekday = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        for day, h in enumerate(loc["store_hours"]):

            dictionary[weekday[day]] = h["open"] + "-" + h["close"]
        hours_of_operation = ""
        for h1 in dictionary:
            hours_of_operation = hours_of_operation + " " + h1 + " " + dictionary[h1]

        phone = loc["phone"]
        name = loc["storeName"].replace("-", "").replace(".", "")
        page_url = (
            "https://www.smartandfinal.com/stores/"
            + str(name.replace(" ", "-").lower())
            + "-"
            + str(store_number)
            + "/"
            + str(loc["locationID"])
        )

        store = [
            DOMAIN,
            page_url,
            loc["storeName"].capitalize(),
            loc["address"].capitalize(),
            loc["city"].capitalize(),
            loc["state"].capitalize(),
            loc["zip"],
            country_code,
            store_number,
            phone,
            location_type,
            loc["latitude"],
            loc["longitude"],
            hours_of_operation,
        ]

        if str(store[2]) + str(store[-3]) not in addresses:
            log.info(
                "Append info to locations: {} : {}".format(
                    loc["storeName"], loc["address"]
                )
            )
            addresses.append(str(store[2]) + str(store[-3]))

            store = [
                str(x).encode("ascii", "ignore").decode("ascii").strip()
                if x
                else "<MISSING>"
                for x in store
            ]

            yield store


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    write_output(data)
    log.info("Finish processed")


scrape()
