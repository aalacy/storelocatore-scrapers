import re
import threading
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

local = threading.local()


def get_cities_from_states():
    response = get_session().get(
        "https://stores.finishline.com/index.html", headers=headers
    )
    soup = bs(response.text, "html.parser")
    links = soup.find_all("a", class_="c-directory-list-content-item-link")
    return [f'https://stores.finishline.com/{link["href"]}' for link in links]


def get_locations_from_cities(urls):
    locations = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_locations, url, locations) for url in urls]
        for future in as_completed(futures):
            pass

    return locations


def get_locations(url, locations):
    response = get_session().get(url, headers=headers)
    soup = bs(response.text, "html.parser")
    links = soup.find_all("a", class_="c-directory-list-content-item-link")
    items = soup.find_all("div", class_="c-location-grid-item")
    is_detail = soup.find("h1", class_="nap-title")

    if len(links):
        for link in links:
            cleaned_url = re.sub(r"\.\.\/", "", link["href"])
            complete_url = f"https://stores.finishline.com/{cleaned_url}"
            get_locations(complete_url, locations)
    elif len(items):
        items = soup.find_all("div", class_="c-location-grid-item")
        for item in items:
            details = item.find("a", string="Store Details")
            if details:
                cleaned_url = re.sub(r"\.\.\/", "", details["href"])
                complete_url = f"https://stores.finishline.com/{cleaned_url}"
                response = get_session().get(complete_url, headers=headers)
                soup = bs(response.text, "html.parser")
                locations.append(get_location(soup, complete_url, True))
            else:
                pass
                locations.append(get_location(item, url, False))
    elif is_detail:
        locations.append(get_location(soup, url, True))


def get_location(item, page_url, is_details):
    location_name = f'{item.find("span", class_="location-name-brand").text.strip()} {item.find("span", class_="location-name-geo").text.strip()}'
    location_name = re.sub(r"\s\s+", " ", location_name)

    street_address = item.find("span", class_="c-address-street-1").text
    city = re.sub(",", "", item.find("span", class_="c-address-city").text)
    state = item.find("abbr", class_="c-address-state").text
    postal = item.find("span", class_="c-address-postal-code").text
    country_code = item.find("abbr", class_="c-address-country-name").text
    phone = item.find("a", class_="c-phone-main-number-link").text

    if is_details:
        hours = item.find(
            "div", class_="nap-hours col-lg-3 col-md-4 col-sm-6 hidden-xs"
        ).find_all("tr", class_="c-location-hours-details-row")
    else:
        hours = item.find(
            "div", class_="c-location-grid-item-hours-today hidden-xs"
        ).find_all("div", class_="c-location-hours-today-details-row")

    hours_of_operation = ", ".join(hour.attrs["content"] for hour in hours)

    return SgRecord(
        locator_domain="jdsports.com",
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        hours_of_operation=hours_of_operation,
    )


def get_session(refresh=False):
    if not hasattr(local, "session") or refresh:
        local.session = SgRequests()

    return local.session


def fetch_data():
    cities = get_cities_from_states()
    locations = get_locations_from_cities(cities)
    return locations


def scrape():
    data = fetch_data()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                },
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for record in data:
            writer.write_row(record)


scrape()
