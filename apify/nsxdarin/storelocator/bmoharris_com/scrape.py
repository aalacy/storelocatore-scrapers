import re
import json
from sgzip.static import static_coordinate_list, SearchableCountries
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_locations(lat, lng):
    url = "https://branchlocator.bmoharris.com/rest/locatorsearch?like=0.2783429985749122&lang=en_US"
    payload = {
        "request": {
            "appkey": "1C92EACC-1A19-11E7-B395-EE7D55A65BB0",
            "formdata": {
                "geoip": "false",
                "dataview": "store_default",
                "limit": "3000",
                "google_autocomplete": "true",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "55402",
                            "country": "US",
                            "latitude": lat,
                            "longitude": lng,
                            "state": "MN",
                            "province": "",
                            "city": "Minneapolis",
                            "address1": "",
                            "postalcode": "55402",
                        }
                    ]
                },
                "searchradius": "5000",
                "softmatch": "1",
                "where": {
                    "or": [
                        {
                            "languages": {"ilike": ""},
                            "walkupcount": {"eq": ""},
                            "driveupcount": {"eq": ""},
                            "smartbranch": {"eq": ""},
                            "grouptype": {"in": "BMOHarrisBranches"},
                            "or": {
                                "safedepositsmall": {"eq": ""},
                                "safedepositmedium": {"eq": ""},
                                "safedepositlarge": {"eq": ""},
                                "allpoint": {"eq": ""},
                                "walgreens": {"eq": ""},
                                "speedway": {"eq": ""},
                                "mobilecash": {"eq": ""},
                            },
                        },
                        {
                            "grouptype": {"eq": "BMOHarrisBranches"},
                            "lobby": {"eq": ""},
                            "secondaryid": {"eq": ""},
                        },
                    ]
                },
                "false": "0",
            },
        }
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    r = session.post(url, headers=headers, data=json.dumps(payload))

    return json.loads(r.text).get("response").get("collection", [])


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for item in data:
            writer.write_row(item)


def fetch_data():
    branches = []
    search = static_coordinate_list(100, SearchableCountries.USA)
    for lat, lng in search:
        data = fetch_locations(lat, lng)
        for location in data:
            store_number = location["clientkey"]
            street_address = location["address1"]
            state = location["state"]
            city = location["city"]
            postal = location["postalcode"]
            country_code = location["country"]

            page_url = f"https://branches.bmoharris.com/{re.sub(' ', '-', state).lower()}/{re.sub(' ', '-', state).lower()}/{store_number}"
            location_type = location["grouptype"]
            location_name = location["name"]

            latitude = location["latitude"]
            longitude = location["longitude"]

            phone = location["phone"]

            hours = []
            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            for day in days:
                open = location[f"{day}open"]
                close = location[f"{day}close"]

                if open and close:
                    hour = "Closed" if re.search("closed", open) else f"{open}-{close}"
                    hours.append(f"{day}: {hour}")
            hours_of_operation = ", ".join(hours)

            yield SgRecord(
                locator_domain="bmoharris.com",
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                state=state,
                city=city,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                hours_of_operation=hours_of_operation,
            )

    return branches


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
