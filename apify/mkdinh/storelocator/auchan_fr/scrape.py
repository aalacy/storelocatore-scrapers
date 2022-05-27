import re
from bs4 import BeautifulSoup
from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipAndGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("auchan.pl")


def fetch_locations(code, latlng, session):
    lat, lng = latlng
    html = session.execute_async_script(
        f"""
        fetch('https://www.auchan.fr/offering-contexts?address.zipcode={code}&location.latitude={lat}&location.longitude={lng}&accuracy=MUNICIPALITY&sellerType=GROCERY', {{
            "headers": {{
                "accept": "application/crest",
                "accept-language": "en-US,en;q=0.9",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-crest-renderer": "journey-renderer",
                "x-requested-with": "XMLHttpRequest"
            }},
            "referrer": "https://www.auchan.fr/nos-magasins",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": null,
            "method": "GET",
            "mode": "cors",
            "credentials": "include"
        }})
            .then(res => res.text())
            .then(arguments[0])
    """
    )

    soup = BeautifulSoup(html, "html.parser")
    locations = soup.find_all("div", class_="journeyPosItem")

    return locations


def fetch_data():

    with SgFirefox(is_headless=True) as session:
        session.get("https://www.auchan.fr")
        session.set_script_timeout(300)
        search = DynamicZipAndGeoSearch(
            [SearchableCountries.FRANCE], max_search_distance_miles=10
        )
        for code, latlng in search:
            for location in fetch_locations(code, latlng, session):
                store_number = location.attrs["data-id"]
                location_name = (
                    location.find("span", class_="place-pos__name").getText().strip()
                )
                location_type = location.attrs["data-type"]

                city = location.attrs["data-city"]
                postal = location.attrs["data-zipcode"]
                country_code = SearchableCountries.FRANCE

                lat = location.attrs["data-lat"]
                lng = location.attrs["data-lng"]

                hours_of_operation = []
                hours = location.find_all("div", class_="pos-details__line")
                for hour in hours:
                    if not hour.attrs.get("for"):
                        continue

                    day = (
                        hour.find("span", class_="pos-details__line-start")
                        .getText()
                        .strip()
                    )
                    day_hour = (
                        hour.find("span", class_="pos-details__line-end")
                        .getText()
                        .strip()
                    )

                    day_hour = re.sub(r"\n", " ", day_hour)
                    day_hour = re.sub(r"\s\s+", "", day_hour)

                    hours_of_operation.append(f"{day}: {day_hour}")
                hours_of_operation = ",".join(hours_of_operation)

                yield SgRecord(
                    locator_domain="auchan.fr",
                    location_name=location_name,
                    location_type=location_type,
                    store_number=store_number,
                    city=city,
                    zip_postal=postal,
                    country_code=country_code,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for row in data:
            writer.write_row(row)
