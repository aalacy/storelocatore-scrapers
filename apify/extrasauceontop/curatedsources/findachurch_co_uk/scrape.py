from sgscrape import simple_scraper_pipeline as sp
from sgscrape.pause_resume import CrawlStateSingleton, SerializableRequest
from sglogging import sglog
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup as bs
import re

log = sglog.SgLogSetup().get_logger(logger_name="findchurch")
headers = {"User-Agent": "PostmanRuntime/7.19.0"}
session = SgRequests()
crawl_state = CrawlStateSingleton.get_instance()


def get_urls():
    search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN])
    for search_lat, search_lon in search:

        url = (
            "https://www.findachurch.co.uk/ajax/Nearby.ashx?CenterLat="
            + str(search_lat)
            + "&CenterLon="
            + str(search_lon)
        )
        y = 0
        while True:
            y = y + 1
            if y == 10:
                raise Exception
            try:
                response = session.get(url).text  # noqa
                break

            except Exception:
                session = SgRequests()  # noqa
                continue

        soup = bs(response, "html.parser")

        locations = soup.find_all("row")

        for location in locations:
            store_number = location["id"]
            location_name = location["title"]
            city = location["town"]
            latitude = location["latlon"].split(",")[0]
            longitude = location["latlon"].split(",")[1]
            url_city = re.sub(r"[^A-Za-z0-9 ]+", "", city).lower().replace(" ", "-")
            page_url = (
                "https://www.findachurch.co.uk/church/"
                + url_city
                + "/"
                + store_number
                + ".htm?lat="
                + str(latitude)
                + "&lon="
                + str(longitude)
                + "&name="
                + location_name.replace(" ", "---")
            )
            search.found_location_at(latitude, longitude)
            crawl_state.push_request(SerializableRequest(url=page_url))
    crawl_state.set_misc_value("got_urls", True)


def get_location(request_url):
    session = SgRequests()
    url = request_url.url
    log.info(url)

    store_number = url.split(".htm")[0].split("/")[-1]
    location_name = url.split("&name=")[1].replace("---", " ")
    city = url.split("church/")[1].split("/")[0].replace("-", " ")
    latitude = url.split("?lat=")[1].split("&lon")[0]
    longitude = url.split("&lon=")[1].split("&")[0]
    url = url.split("?")[0]
    address = ""
    state = ""
    zipp = ""
    phone = ""
    location_type = ""
    hours = ""

    try:
        response = session.get(url, headers=headers).text

    except Exception:
        response = session.get(url, headers=headers).text
        session = SgRequests()

    if "awaiting verification" in response and "The contact data we hold" in response:

        return {
            "page_url": url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": address,
            "state": state,
            "zip": zipp,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
        }

    soup = bs(response, "html.parser")

    try:
        address_parts = (
            soup.find("div", attrs={"class": "contact_section"})
            .find("span")
            .text.strip()
            .split("\n")
        )

    except Exception:
        response = session.get(url, headers=headers).text
        if (
            "awaiting verification" in response
            and "The contact data we hold" in response
        ):

            return {
                "page_url": url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
            }

        try:
            soup = bs(response, "html.parser")
            address_parts = (
                soup.find("div", attrs={"class": "contact_section"})
                .find("span")
                .text.strip()
                .split("\n")
            )
        except Exception:
            raise Exception

    found_address = "No"
    found_zip = "No"
    for part in address_parts:
        try:
            if part[0].isdigit() is True and found_address == "No":
                address = part
                found_address = "Yes"

            elif bool(re.search(r"\d", part)) is True and found_zip == "No":
                zipp = part
                found_zip = "Yes"

                index = address_parts.index(part)
                state = address_parts[index - 1]

        except Exception:
            pass

    if found_address == "No":
        address = address_parts[0]

    if found_zip == "No":

        if address_parts[-1] == "(This is not necessarily the venue address.)":
            try:
                zipp = address_parts[-3]
                state = address_parts[-4]
            except:
                zipp = "<MISSING>"
                state = "<MISSING>"

        else:
            zipp = address_parts[-2]
            state = address_parts[-3]

    phone = (
        soup.find("span", attrs={"class": "contact_phone"})
        .text.strip()
        .replace(" ", "")
    )

    if "e" in phone:
        phone = "<MISSING>"

    try:
        location_type = soup.find("div", attrs={"class": "tag"}).text.strip()

    except Exception:
        location_type = "<MISSING>"

    try:
        hours_parts = soup.find("section", attrs={"id": "profile_worship"}).find_all(
            "div", {"class": "service_time si_summary"}
        )
        hours = ""
        for part in hours_parts:
            hours = hours + part.text.strip() + ", "
        hours = hours[:-2]

    except Exception:
        hours = "<MISSING>"

    return {
        "page_url": url,
        "location_name": location_name,
        "latitude": latitude,
        "longitude": longitude,
        "city": city,
        "store_number": store_number,
        "street_address": address,
        "state": state,
        "zip": zipp,
        "phone": phone,
        "location_type": location_type,
        "hours": hours
    }


def scrape_loc_urls():
    url_list = [loc for loc in crawl_state.request_stack_iter()]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_location, loc) for loc in url_list]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception as e:
                log.error(str(e))


def scrape():
    if not crawl_state.get_misc_value("got_urls"):
        get_urls()

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField("findachurch.co.uk"),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.ConstantField("UK"),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=scrape_loc_urls,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
