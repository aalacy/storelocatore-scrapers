from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4

log = sglog.SgLogSetup().get_logger(logger_name="speedycafe.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.speedway.com/locations/search"
    locator_domain = "https://www.speedway.com"

    headers = {
        "authority": "www.speedway.com",
        "method": "POST",
        "path": "/locations/search",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "191",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.speedway.com",
        "referer": "https://www.speedway.com/locations",
        "sec-ch-ua": '"Chromium";v="93", " Not A;Brand";v="99", "Google Chrome";v="93"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    session = SgRequests()

    max_distance = 200
    max_results = 90

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=max_distance,
        granularity=Grain_4(),
    )

    for lat, lng in search:
        lat = "{:.7f}".format(lat)
        lng = "{:.7f}".format(lng)
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        payload = {
            "SearchType": "search",
            "SearchText": "US",
            "StartIndex": "0",
            "Limit": max_results,
            "Latitude": lat,
            "Longitude": lng,
            "Radius": "20000",
            "Filters[FuelType]": "Unleaded",
            "Filters[OnlyFavorites]": "false",
            "Filters[Text]": "",
        }

        try:
            req = session.post(base_link, headers=headers, data=payload)
            base = BeautifulSoup(req.text, "lxml")
        except:
            continue

        items = base.find_all(class_="c-location-card")
        for item in items:

            latitude = item["data-latitude"]
            longitude = item["data-longitude"]
            search.found_location_at(float(latitude), float(longitude))
            link = locator_domain + item.a["href"]

            location_name = ""
            if "COMING SOON" in item.text.upper():
                continue

            street_address = item.find(class_="c-location-heading").text.strip()
            city = item.find(
                "li", attrs={"data-location-details": "address"}
            ).text.split(",")[0]
            state = item["data-state"]
            zip_code = (
                item.find("li", attrs={"data-location-details": "address"})
                .text.split(",")[-1]
                .split()[-1]
            )
            country_code = "US"
            store_number = item["data-costcenter"]

            try:
                location_type = ", ".join(
                    list(
                        item.find(class_="c-location-options--fuel").ul.stripped_strings
                    )
                )
            except:
                try:
                    location_type = (
                        ", ".join(
                            list(
                                item.find(
                                    class_="c-location-options--amenities"
                                ).ul.stripped_strings
                            )
                        )
                        .split(" mi,")[1]
                        .strip()
                    )
                except:
                    location_type = ""
            hours_of_operation = ""
            try:
                if (
                    "open 24"
                    in item.find(class_="c-location-options--amenities").text.lower()
                ):
                    hours_of_operation = "Open 24 Hours"
            except:
                pass
            try:
                phone = item.find(
                    "li", attrs={"data-location-details": "phone"}
                ).text.strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
