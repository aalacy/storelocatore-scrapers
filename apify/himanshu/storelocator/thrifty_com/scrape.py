from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def fetch_data():

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://www.thrifty.com/"

    search = static_zipcode_list(radius=100, country_code=SearchableCountries.USA)
    search = search + static_zipcode_list(
        radius=100, country_code=SearchableCountries.CANADA
    )

    for zip_code in search:
        page_url = f"https://www.thrifty.com/loc/modules/multilocation/?near_location={zip_code}&services__in=&published=1&within_business=true"

        try:
            json_r = session.get(page_url, headers=headers).json()
        except:
            continue
        for data in json_r["objects"]:
            store_number = data["id"]

            location_type = "Thrifty"
            location_name = get(data, "location_name")
            street_address = get(data, "street")
            city = get(data, "city")
            state = get(data, "state")
            zipp = get(data, "postal_code")
            country_code = get(data, "country")
            if country_code not in ["CA", "US"]:
                continue
            phone = get(data["phonemap"], "phone")
            latitude = get(data, "lat")
            longitude = get(data, "lon")
            page_url = get(data, "location_url")

            hours = data["formatted_hours"]["primary"]["days"]
            HOO = [f"{hour['label']} {hour['content']}" for hour in hours]
            hours_of_operations = ", ".join(HOO) if len(HOO) else MISSING

            yield SgRecord(
                locator_domain=base_url,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city.strip(),
                state=state.strip(),
                zip_postal=zipp.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=str(latitude),
                longitude=str(longitude),
                hours_of_operation=hours_of_operations,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
