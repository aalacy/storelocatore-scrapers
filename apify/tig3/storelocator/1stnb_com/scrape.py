import csv
from sgrequests import SgRequests
from sglogging import sglog
from lxml import etree


# set to True to see more detailed logs
# set to False before commit
IS_TESTING = False

website = "1stnb.com"
log = sglog.SgLogSetup().get_logger(logger_name=website, stdout_log_level="INFO")

# locatortype=3 -> to select only "Branch" types
LIST_URL_TEMPLATE = "https://www.1stnb.com/Content/Locator?search=search&Locatorlisting=3&City=&StateId=0&ZipCodeTxt=&City=&StateId=0&ZipCodeTxt=&locatortype=3&search=[object+HTMLInputElement]&latitude=&longitude=&page={page}"
STORE_URL_TEMPLATE = "https://www.1stnb.com/{path}"

HEADERS_BASE = {
    "Host": "1stnb.com",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

HEADERS_STORE_LIST = {
    "Accept": "text/html, */*; q=0.01",
    "Referer": "https://1stnb.com/locator",
    "X-Requested-With": "XMLHttpRequest",
}

HEADERS_STORE_PAGE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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


def fetch_data():
    locations_list = []

    log.info("Starting to scrap store list urls")

    # Loop to get list of stores urls
    page = 1
    while True:
        log_testing(f"Scraping Store list page = {page}")

        session = SgRequests()
        headers = dict_sort_key({**HEADERS_BASE, **HEADERS_STORE_LIST})
        request_url = LIST_URL_TEMPLATE.format(page=page)

        response = session.get(request_url, headers=headers)
        check_response(response, request_url)

        response_text = response.text

        if check_results(response_text):
            locations_list.append(response_text)
            log_testing(f"Store list page = {page} - DONE")
        else:
            log_testing(f"No records on page = {page} - List scrapping is DONE")
            break

        page += 1

    log.info("Store list pages are DONE. Starting store individual page requests")

    store_list = location_html_to_list(locations_list)
    data_list = []

    store_count = len(store_list)

    # loop over locations to get the data
    i = 1
    for store_path in store_list:
        page_url = STORE_URL_TEMPLATE.format(path=store_path)

        log_testing(f"----- Scraping Store page: {page_url}")

        session = SgRequests()
        headers = dict_sort_key({**HEADERS_BASE, **HEADERS_STORE_PAGE})
        response = session.get(page_url, headers=headers)
        check_response(response, page_url)

        response_text = response.text

        log_testing(f"Scraping Store page: {page_url} - DONE")
        log_testing(f"Store # {i} out of {store_count} is DONE")
        i += 1

        data_list.append(get_store_data(response_text, page_url))

    return data_list


def location_html_to_list(html_list):
    locations_list = []
    for html_item in html_list:
        sel = etree.HTML(html_item)
        items = sel.xpath("//table/tbody//tr")

        for item in items:
            link = item.xpath(".//td[1]//a/@href")
            locations_list.append(link[0])

    return locations_list


def get_store_data(response_text, page_url):
    log_testing(f"Generating data for store page: {page_url}")

    sel = etree.HTML(response_text)

    full_address_raw = sel.xpath(
        '//div[@class="location-details"]/table/tbody/tr/td[2]//text()'
    )
    hours_of_operation_raw = sel.xpath(
        '//div[@class="location-details"]/table/tbody/tr/td[3]//text()'
    )
    hours_of_operation = " ".join(list_strip(hours_of_operation_raw)[3:])
    full_address_raw = list_strip(full_address_raw)

    location_name = full_address_raw[0]
    street_address = full_address_raw[1]
    zip_city_state = full_address_raw[2]

    # remove extra comma, if any (typo in address for https://www.1stnb.com/bell-road)
    zip_city_state = zip_city_state.replace(",,", ",")

    lst = zip_city_state.split(",")
    zip_city_list = lst[0].strip().split(" ")

    state = lst[1].strip()
    zip = zip_city_list[0]
    city = " ".join(zip_city_list[2:]).strip()
    country_code = "US"
    store_number = check_missing()
    phone = check_missing()
    location_type = check_missing()

    # the data exists in JS code
    # such as - searchLocations('32.9042872', '-97.5460499');
    start = response_text.index("searchLocations")
    end = response_text.index(")", start)

    substr = response_text[start:end]
    substr = substr.replace("searchLocations(", "")
    lat_long_list = substr.split(",")
    lat_long_list = list_strip(lat_long_list, " '")

    latitude = lat_long_list[0]
    longitude = lat_long_list[1]

    data = [
        website,
        page_url,
        location_name,
        street_address,
        city,
        state,
        zip,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]

    log_testing(f"Data generated for store page: {page_url}")

    return data


def check_results(response_text):
    sel = etree.HTML(response_text)
    trs = sel.xpath('//div[@id="grdresult"]/table/tbody/tr')
    if len(trs):
        return True

    return False


# For logging more messages during testing
def log_testing(message):
    if IS_TESTING:
        log.info(message)


def check_response(response, request_url):
    if response.status_code != 200:
        log.error(
            f"Request failed for {request_url} with status code: {response.status_code}"
        )
        exit("Exiting")


# to be moved to general class
# Apply strip method to list's elements
# By default only white spaces are removed
def list_strip(list_var, chars=None):
    return [elem.strip(chars) for elem in list_var if elem.strip(chars)]


# to be moved to general class
# sort the dictionary by key
def dict_sort_key(d):
    return dict(sorted(d.items()))


# to be moved to general class
# If empty string - returns "<MISSING>" keyword
def check_missing(val=""):
    if not val:
        return "<MISSING>"
    else:
        return val


# to be moved to general class
# If empty string - returns "<INACCESSIBLE>" keyword
def check_inaccessible(val=""):
    if not val:
        return "<INACCESSIBLE>"
    else:
        return val


def scrape():
    log.info("Start...")
    data = fetch_data()
    log.info("Data fetched. Writing output...")
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()
