import json
import threading
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.static import static_zipcode_list
from sgzip.dynamic import SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

local = threading.local()


def get_session(refresh):
    if not hasattr(local, "session") or refresh:
        local.session = SgRequests()

    return local.session


def fetch_stores(postal, retry=0):
    try:

        base = "https://stores.jdsports.com/search.html?q="
        url = base + postal
        return bs(get_session(retry > 0).get(url, headers=headers).text, "lxml")
    except:
        if retry < 3:
            return fetch_stores(postal, retry + 1)


def fetch_locations(postal, retry=0):
    locations = []
    locator_domain = "https://stores.jdsports.com/"
    soup = fetch_stores(postal)

    if not soup:
        return []

    info = soup.find("div", {"class": "search-results-wrapper"})
    info = info.find("ol", {"class": "location-list-results"})

    if info is not None:
        info = info.find_all("li", {"class": "location-list-result js-location-result"})
        for location in info:
            loc_id = location.find("h2", {"class": "location-card-title"}).text.strip()
            name = location.find("span", {"class": "location-name-geo"}).text.strip()

            if location.find("a", {"class": "location-card-title-link"}) is None:
                loc_url = SgRecord.MISSING
            else:
                loc_url = location.find("a", {"class": "location-card-title-link"})[
                    "href"
                ]
            loc_type = location.find(
                "span", {"class": "location-name-brand"}
            ).text.strip()
            if loc_type == "JD Sports":
                loc_url = locator_domain + loc_url
            postal = location.find(
                "span", {"class": "c-address-postal-code"}
            ).text.strip()
            if location.find("span", {"class": "c-address-street-2"}) is None:
                address = location.find(
                    "span", {"class": "c-address-street-1"}
                ).text.strip()
            else:
                address_1 = location.find(
                    "span", {"class": "c-address-street-1"}
                ).text.strip()
                address_2 = location.find(
                    "span", {"class": "c-address-street-2"}
                ).text.strip()
                address = address_1 + address_2
            city = location.find("span", {"class": "c-address-city"}).text.strip()[:-1]
            state = (
                location.find("span", {"class": "c-address-state"})
                or location.find("abbr", {"class": "c-address-state"})
            ).text.strip()
            country = "US"
            phone = location.find(
                "a",
                {"class": "c-phone-number-link c-phone-main-number-link"},
            ).text.strip()
            store_number = loc_id
            hours = location.find(
                "div", {"class": "c-location-hours-today js-location-hours"}
            )["data-days"]
            hours = json.loads(hours)
            hoo = ""
            for day in hours:
                day_name = day["day"]
                if day["intervals"] != []:
                    time = day["intervals"][0]
                    start = str(time["start"])
                    end = str(time["end"])
                    day_hoo = start + " - " + end
                else:
                    day_hoo = "Closed"
                hoo = hoo + day_name + " " + day_hoo + ", "
            hoo = hoo[:-2]

            if loc_url != SgRecord.MISSING:
                soup = bs(
                    get_session(retry > 1).get(loc_url, headers=headers).text, "lxml"
                )
                coords = soup.find("div", {"class": "location-map-wrapper"})
                coords = coords.find("link")["href"]
                coords = coords.split("center=")[1].split("&")[0]
                [lat, long] = coords.split("%2C")
            else:
                lat = SgRecord.MISSING
                long = SgRecord.MISSING

            locations.append(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=loc_url,
                    location_name=name,
                    street_address=address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country,
                    store_number=store_number,
                    phone=phone,
                    location_type=loc_type,
                    latitude=lat,
                    longitude=long,
                    hours_of_operation=hoo,
                )
            )

    return locations


def fetch_data():
    codes = static_zipcode_list(radius=30, country_code=SearchableCountries.USA)
    for postal in codes:
        yield from fetch_locations(postal)


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
