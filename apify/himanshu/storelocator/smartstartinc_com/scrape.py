import re

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="smartstartinc.com")

session = SgRequests()

states = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NA": "National",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "https://www.smartstartinc.com/"

    r_token = session.get(base_url, headers=headers)
    token = r_token.text.split("ss_webapi_bearer = '")[1].split("'")[0]
    company_id = r_token.text.split("ss_api_company_id = '")[1].split("'")[0]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Authorization": "Bearer " + token,
    }

    max_results = 50
    max_distance = 50

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Running sgzip ..")
    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        locations_url = (
            "https://webapi.smartstartinc.com/api/Shared/StoreLocations/LookupByLatLong"
            "?companyId="
            + str(company_id)
            + "&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&limit=50"
        )

        json_data = session.get(locations_url, headers=headers).json()["Data"]

        for script in json_data:

            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = ""
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            page_url = ""
            hours_of_operation = ""

            location_name = script["Name"]
            street_address = script["AddressLine1"]
            if script["AddressLine2"]:
                street_address += " " + script["AddressLine2"]
            store_number = script["StoreNumber"]
            state = script["State"]
            city = script["City"]
            phone = script["WebPhoneNumber"]

            if script["HoursOfOperation"]:
                hours_of_operation = re.sub(r"\s+", " ", script["HoursOfOperation"])
                hours_of_operation = hours_of_operation.replace("<br>", "")
            latitude = str(script["Latitude"])
            longitude = str(script["Longitude"])

            search.found_location_at(float(latitude), float(longitude))

            if state in states:
                zipp = script["PostalCode"]
                page_url = (
                    "https://www.smartstartinc.com/locations/"
                    + states[state].replace(" ", "-").lower()
                    + "-"
                    + city.replace(" ", "-").lower()
                    + "-"
                    + script["AddressLine1"].replace(" ", "-").lower()
                    + "-"
                    + zipp.replace(" ", "-").lower()
                )
                country_code = "US"
            else:
                continue

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
