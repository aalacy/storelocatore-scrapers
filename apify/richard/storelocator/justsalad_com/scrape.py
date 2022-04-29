from sgrequests import SgRequests
from geopy.geocoders import Nominatim
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

geolocator = Nominatim(user_agent="justsalad_com_scraper")

URL = "https://justsalad.com"


def fetch_data():
    # store data
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()

    stores = session.get(
        "https://justsalad-admin.azurewebsites.net/v1/justsaladstores", headers=HEADERS
    ).json()["features"]

    for store in stores:

        latlon = store["geometry"]

        # Lat
        lat = latlon["coordinates"][1]

        # Long
        lon = latlon["coordinates"][0]

        # Get loc info
        location = geolocator.reverse(f"{lat}, {lon}").raw

        # Country
        country = location["address"]["country_code"].upper()

        if country != "US":
            continue

        if not store["properties"]["locationID"][0].isalpha():
            store = store["properties"]

            # Name
            location_title = (
                store["locationName"]
                .encode("ascii", "replace")
                .decode()
                .replace("?", "'")
            )

            # Store ID
            location_id = store["locationID"]

            location_link = "https://justsalad.com/locations"

            # Type
            location_type = "<MISSING>"

            # Street
            street_address = (
                store["locationAddress"].replace("<br>", "").replace("  ", " ")
            )

            # Phone
            phone = store["locationPhone"]

            # city
            city = "<MISSING>"
            if "city" in location["address"].keys():
                city = location["address"]["city"]
            elif "town" in location["address"].keys():
                city = location["address"]["town"]
            elif "county" in location["address"].keys():
                city = location["address"]["county"]

            # zip
            zipcode = location["address"]["postcode"]

            # State
            state = location["address"]["state"]

            # Hour
            hour = " ".join([store["hours1"], store["hours2"], store["hours3"]])

            # Store data
            yield SgRecord(
                locator_domain="justsalad.com",
                page_url=location_link,
                location_name=location_title,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country,
                store_number=location_id,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lon,
                hours_of_operation=hour,
            )


def scrape():
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1


if __name__ == "__main__":
    scrape()
