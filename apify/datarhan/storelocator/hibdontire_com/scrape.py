import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

base_url = "https://local.hibdontire.com"


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)


def fetch_links(url, session):
    html = session.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    target_div = soup.select_one("#links")
    links = target_div.select("a")
    urls = [a["href"] for a in links]

    return urls


def fetch_states(session):
    return fetch_links(base_url, session)


def fetch_cities(link, session):
    city_url = f"{base_url}{link}"
    return fetch_links(city_url, session)


def fetch_locations(link, session):
    location_url = f"{base_url}{link}"
    return fetch_links(location_url, session)


MISSING = "<MISSING>"


def extract(url, session):
    locator_domain = "hibdontire.com"
    page_url = f"{base_url}{url}"
    html = session.get(page_url).text
    soup = BeautifulSoup(html, "html.parser")
    info = soup.find("div", class_="location-info")

    location_name = info.find("h3").text
    store_number = re.sub(
        r"store\s*",
        "",
        soup.find("div", class_="store-number").find("span").text,
        flags=re.IGNORECASE,
    )

    street_address = soup.find("div", itemprop="streetAddress").text
    city = soup.find("span", itemprop="addressLocality").text
    state = soup.find("span", itemprop="addressRegion").text
    postal = soup.find("span", itemprop="postalCode").text
    country_code = "US"
    latitude = MISSING
    longitude = MISSING

    hours_of_operation = ",".join(
        [li.text for li in soup.find("dl", itemprop="openingHours").find_all("li")]
    )
    phone = soup.find("a", itemprop="telephone").text

    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )


def fetch_data():
    with SgRequests() as session:
        cities = []
        locations = []
        states = fetch_states(session)

        for state in states:
            cities.extend(fetch_cities(state, session))

        for city in cities:
            locations.extend(fetch_locations(city, session))

        for location in locations:
            yield extract(location, session)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
