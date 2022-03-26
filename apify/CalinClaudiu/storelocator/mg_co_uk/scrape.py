import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.static import static_zipcode_list, SearchableCountries
from sgrequests import SgRequests


def write_output(data):
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for row in data:
            writer.write_row(row)


def get(store, key):
    return store.get(key, SgRecord.MISSING) or SgRecord.MISSING


session = SgRequests()


def fetch_with_retry(url, retry=0):
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Host": "www.mg.co.uk",
    }

    try:
        res = session.get(url, headers=headers)
        return res
    except Exception:
        if retry < 3:
            return fetch_with_retry(url, retry + 1)
        else:
            return None


def fetch_data():
    page_url = "https://www.mg.co.uk/dealers"
    search = static_zipcode_list(10, country_code=SearchableCountries.BRITAIN)

    for zipcode in search:
        url = f"https://www.mg.co.uk/api/dealer-lookup?postcode={zipcode}"

        res = fetch_with_retry(url)

        if res.status_code != 200:
            continue

        stores = res.json()
        for store in stores:
            locator_domain = "mg.co.uk"
            location_name = get(store, "fca_name")
            store_number = get(store, "id")

            details = store.get("sales_details") or store.get("after_sales")
            street_address = get(details, "address1")

            city = get(details, "town")
            if re.search(r"^MG", city):
                city = get(details, "address2")

            state = get(store, "state")
            postal = get(details, "postcode")

            latitude = get(details, "latitude")
            longitude = get(details, "longitude")
            phone = get(details, "phoneNumber")
            hours_of_operation = ", ".join(
                f"{day}: {hours}" for day, hours in details["hours"].items()
            )

            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="UK",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
