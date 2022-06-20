from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://rbcroyalbank.com/"
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=250,
        max_search_results=None,
    )
    for z in zips:
        api_url = f"https://maps.rbcroyalbank.com/api/?q={str(z)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        }
        r = session.get(api_url, headers=headers)
        try:
            js = r.json()["locations"]
        except:
            zips.found_nothing()
            continue
        for j in js:

            location_name = j.get("name") or "<MISSING>"
            street_address = j.get("address") or "<MISSING>"
            street_address = (
                str(street_address)
                .replace("&acirc;", "â")
                .replace("&nbsp;", " ")
                .replace("&amp;", "&")
                .replace("&ocirc;", "ô")
                .replace(",", "")
            )
            city = j.get("city") or "<MISSING>"
            state = j.get("province") or "<MISSING>"
            postal = j.get("postalCode") or "<MISSING>"
            country_code = "CA"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("location")[0] or "<MISSING>"
            longitude = j.get("location")[1] or "<MISSING>"
            zips.found_location_at(latitude, longitude)
            hours_of_operation = "<MISSING>"
            branch = j.get("branch")
            atm = j.get("atm")
            type_slug = "<MISSING>"
            if branch:
                type_slug = "branch"
            if atm and not branch:
                type_slug = "atm"
            store_number = j.get("transit")
            if type_slug == "atm":
                store_number = j.get("atmIds")[0]
            page_url = f"https://maps.rbcroyalbank.com/{state}-{city}-{type_slug}-{store_number}"
            tmp = []
            if branch:
                tmp.append("branch")
            if atm:
                tmp.append("atm")
            location_type = ", ".join(tmp)
            hours = j.get("storeHours") or "<MISSING>"
            tmp = []
            if hours != "<MISSING>":
                for h in range(len(hours)):
                    day = (
                        str(h)
                        .replace("0", "Sunday")
                        .replace("1", "Monday")
                        .replace("2", "Tuesday")
                        .replace("3", "Wednesday")
                        .replace("4", "Thursday")
                        .replace("5", "Friday")
                        .replace("6", "Saturday")
                    )
                    opens = hours[h][0]
                    closes = hours[h][1]
                    line = f"{day} {opens} - {closes}"
                    if opens == closes:
                        line = f"{day} Closed"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "<MISSING>"
            status_h = j.get("storeStatus").get("status")
            if (
                hours_of_operation == "<MISSING>"
                and status_h == "closed"
                and "branch" in location_type
            ):
                hours_of_operation = "Closed"

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
