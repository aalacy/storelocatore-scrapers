import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "brownsshoes.com"
BASE_URL = "https://www.brownsshoes.com/en"
LOCATION_URL = "https://www.brownsshoes.com/en/find-a-store/"
HEADERS = {
    "Host": "www.brownsshoes.com",
    "Referer": "https://www.brownsshoes.com/en/find-a-store",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Site": "origin",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Mode": "navigate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "Cookie": "_vuid=d6371674-e769-4fde-9f1d-d42309d543f1; __cfduid=de0fa01ca57689eddad16d6a1020f41421614651123; dwac_eaec2a44670c8d27339192c2da=39T4sMnMKnuU-IlIEoMaqZ4Nw-Xf_RqoSmA%3D|dw-only|||CAD|false|America%2FMontreal|true; cqcid=bc8va6irWZrOLdpEIHaRVCEeQh; cquid=||; sid=39T4sMnMKnuU-IlIEoMaqZ4Nw-Xf_RqoSmA; dwanonymous_f75b325ed75eeb7c3c140bef0629f074=bc8va6irWZrOLdpEIHaRVCEeQh; _pxhd=1a64b583c984b3aebe221a4618b1570d7df61fad772d0dbbf26d40fa965af449:ae7e4471-7afc-11eb-a2e9-3f3935ecae26; __cq_dnt=0; dw_dnt=0; dwsid=DK-clEPtlqcrtVJb8KYkL012p8FV3KZ09S0WA4O055qnKGK83Cw01RN5ipznp8IQun9oC1NPqFE0EKd3LUs5NQ==; _gcl_au=1.1.370255592.1614651126; _ga=GA1.2.1172099715.1614651127; _gid=GA1.2.855461353.1614651127; _pxvid=ae7e4471-7afc-11eb-a2e9-3f3935ecae26; _pin_unauth=dWlkPVlURXlNR0UwTm1VdFptRTBZaTAwWkdSbExXSXpNelV0TkRZd01UWTVZV0ZpWldZMw; __cq_uuid=ab6EMsIVWosLITBnnZtlQV6Ni9; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; etuix=i78RxHQFdjz0RIAbd7d1it.jSmoCFzALY7Ltb6LENsWJzDGpYxGYrQ--; _hjTLDTest=1; _hjid=cb92c684-64f6-4b99-8457-cc2ecc4a847d; _hjFirstSeen=1; ltkmodal-suppression-d804ce5f-d175-4e05-b5b1-124d819fcf44=Sun%20Mar%2002%202031%2009%3A21%3A05%20GMT%2B0700%20(Waktu%20Indonesia%20Barat); _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _gsid=dc744deb-67c2-4b95-9a4d-94d0797d2c59; STSID320104=87d63c11-6b61-4937-8d78-df662ad8675e; ltkmodal-impression-d804ce5f-d175-4e05-b5b1-124d819fcf44=09fe4424-9b74-4b7a-bd04-29bf8768e473; ltkpopup-session-depth=2-3; _uetsid=afe903807afc11eba15733a6daeed148; _uetvid=afe952a07afc11eb8f42c1299eb52378; _derived_epik=dj0yJnU9WC1MRFFHOFYzOXBqUGs1b3UxNm01MGJrNkdrS1dzZWQmbj14T203cktQWmlFRnVtQTZwbmJlTTZRJm09MSZ0PUFBQUFBR0E5cFdjJnJtPTEmcnQ9QUFBQUFHQTlwV2M; _px3=391265b72909b2b395710407ed611686f17d3f026b43b6e4f2eb9a385bdad5e5:P8KHLskNKwoPcnn1DrAxetCz3A38r+46IXWpIPGCFgW8PU8EtwBFZiyje0bdENhJoYWP3xtbQxFpbEuFjiaixQ==:1000:RNM8KXeOVwT4xyYVhV/H1EiuzlGhAcZ403YA8FCzMw2iuHIK97Tkzl6OsMiYZfoZRhsKQHl1vsRaKEVZKXr3nH+VnR0a+ExKCSU7iQaLzUSk86OjzJjOYttqmf2rXMzR4mKWwYuqoUZcozplRvh0t/kVaD7Id7x0my5zJknLCZ8=",
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
    stores = soup.find("div", {"class": "store-locator-results"}).find_all(
        "div", {"class": "bs-store-details"}
    )
    locations = []
    for row in stores:
        info = row.find("div", {"class": "store-details"})
        locator_domain = DOMAIN
        location_name = handle_missing(
            row.find("div", {"class": "store-name"}).text.strip()
        )
        address = (
            row.find("address", {"class": "bs-store-address"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        if len(address) > 4:
            street_address = ", ".join(address[:2])
            city = handle_missing(address[2])
            state = handle_missing(address[3])
        else:
            street_address = handle_missing(address[0])
            city = handle_missing(address[1])
            state = handle_missing(address[2])
        zip_code = handle_missing(address[-1])
        country_code = "CA"
        store_number = info["data-store-id"]
        phone = row.find("a", {"class": "storelocator-phone"}).text.strip()
        hours_of_operation = row.find("div", {"class": "bs-store-hours-list"}).get_text(
            strip=True, separator=" "
        )
        if "TEMPORARILY CLOSED" in hours_of_operation:
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        geo = (
            row.find("a", {"class": "bs-store-map"})["href"]
            .replace("https://maps.google.com/?daddr=", "")
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
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
