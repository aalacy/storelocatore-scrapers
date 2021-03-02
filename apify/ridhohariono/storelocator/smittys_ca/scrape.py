import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "smittys.ca"
BASE_URL = "https://www.smittys.ca/Select-Location"
LOCATION_URL = "https://www.smittys.ca/Select-Location"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    # "Cookie": "__cfduid=d44cc391e02d87d56e55eedf90000edea1614651126; dwac_cduPIiaagX51kaaac2W3Y7btIB=57xZvz7inkM4JnOrRVDC_FQHkXQVApeOgas%3D|dw-only|||CAD|false|Canada%2FPacific|true; cqcid=efa1vUcP9cboGIud7a2l6nlRgW; cquid=||; sid=57xZvz7inkM4JnOrRVDC_FQHkXQVApeOgas; dwanonymous_e5a4fb50d9485024cd9a35bd8d33e899=efa1vUcP9cboGIud7a2l6nlRgW; __cq_dnt=0; dw_dnt=0; dwsid=j99EnVYnxUg2rjHY2EhFgzxkjFZ9x8yFjyNeBB1mPLVnqCqm9OiBFwcWj0a76lKmUfoJst4nY8uVzTjPXFkSrw==; _gcl_au=1.1.693652787.1614651129; _ga=GA1.2.2059391029.1614651130; _gid=GA1.2.1247521517.1614651130; _pin_unauth=dWlkPVlURXlNR0UwTm1VdFptRTBZaTAwWkdSbExXSXpNelV0TkRZd01UWTVZV0ZpWldZMw; __cq_uuid=ab6EMsIVWosLITBnnZtlQV6Ni9; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; ltkpopup-session-depth=1-1; _gsid=ea4c0b27-5042-4819-a786-8f7406c71466; STSID380639=35c4310d-32cf-44af-bec0-7ae06eaec1c1; BVImplmain_site=3532; _derived_epik=dj0yJnU9bndvSWcyZWR5RmdIWlQ0d3hZYXB5RnY4R1JTdXFVZDAmbj0wU3A4ak0wZU1VUnIxSU1welFKeDN3Jm09MSZ0PUFBQUFBR0E5cC13JnJtPTEmcnQ9QUFBQUFHQTlwLXc; datadome=0K8wzlqqQ3xnpd49jAz5lFwbFTP1dqjhEUA88X_vTEODOzXxDfirbhvpmdKk_Mvfvyi8.IoFPDoDycyTrIZ1_nzyQfrfawfpL5fW8vt.N.",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    log.info("Write Output of " + DOMAIN)
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


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    stores = soup.find("div", {"id": "smittis-list"}).find_all(
        "div", {"class": "smitty-items"}
    )
    locations = []
    for row in stores:
        if int(row["rel"]) == 173:
            continue
        info = row.find("div", {"class": "result-details"})
        data = info.find("p").contents
        locator_domain = DOMAIN
        location_name = handle_missing(info.find("h2").text.strip())
        address = data[0].replace("Canada", "").strip().split(",")
        if len(address) >= 4:
            if len(address) > 4:
                street_address = ", ".join(address[:2])
                city = handle_missing(address[2])
                state = handle_missing(address[3])
            else:
                street_address = address[0]
                city = handle_missing(address[1])
                state = handle_missing(address[2])
            zip_code = handle_missing(address[-1])
        elif len(address) == 3:
            street_address = address[0]
            city = handle_missing(address[1])
            state_zip = address[2].strip().split(" ")
            state = handle_missing(state_zip[0])
            zip_code = handle_missing(address[2].replace(state, "").strip())
        else:
            if "10 Aquitania Boulevard" in address:
                street_address = ", ".join(address[:2])
                city = location_name.replace(" - West", "").strip()
            else:
                street_address = handle_missing(address[0])
                city = handle_missing(address[1])
            state = "<MISSING>"
            zip_code = "<MISSING>"
        country_code = "CA"
        store_number = row["rel"]
        phone = handle_missing(data[8].strip())
        location_type = "<MISSING>"
        hours = info.find("div", {"class": "restaurant_hours"})
        if hours:
            hours_of_operation = handle_missing(
                hours.get_text(strip=True, separator=",")
            )
        else:
            hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                locator_domain,
                LOCATION_URL,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
