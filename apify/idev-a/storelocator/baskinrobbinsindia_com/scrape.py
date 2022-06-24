from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address

session = SgRequests()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://baskinrobbinsindia.com/"

    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.INDIA,
            SearchableCountries.BANGLADESH,
            SearchableCountries.SRI_LANKA,
        ],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )
    for lat, long in search:

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        }

        r = session.get(
            f"https://stockist.co/api/v1/u11410/locations/search?tag=u11410&latitude={str(lat)}&longitude={str(long)}&filter_operator=and&distance=500000&_=st_3cb74uyu05ix1isqz8lrw",
            headers=headers,
        )

        try:
            js = r.json()["locations"]
        except:
            search.found_nothing()
            continue
        search.found_location_at(lat, long)
        for j in js:

            page_url = "https://baskinrobbinsindia.com/pages/store-locator"
            location_name = j.get("name") or "<MISSING>"
            ad = j.get("address_line_1") or "<MISSING>"
            if ad:
                ad = "".join(ad).replace("\n", " ").replace("\r", "").strip()
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address.isdigit():
                street_address = ad
            state = j.get("state") or "<MISSING>"
            postal = j.get("postal_code") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            if city == "0":
                city = "<MISSING>"
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            store_number = j.get("id")
            phone = j.get("phone") or "<MISSING>"
            if str(phone).find(",") != -1:
                phone = str(phone).split(",")[0].strip()
            if str(phone).find("/") != -1:
                phone = str(phone).split("/")[0].strip()
            if phone == "-":
                phone = "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
