from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING
    country = adr.country or SgRecord.MISSING

    return street, city, state, postal, country


def fetch_data(sgw: SgWriter):
    api = "https://api.storepoint.co/v1/15d9be724cb162/locations?rq"
    r = session.get(api, headers=headers)
    js = r.json()["results"]["locations"]

    for j in js:
        location_name = j.get("name")
        raw_address = j.get("streetaddress") or ""
        raw_address = " ".join(raw_address.split())
        street_address, city, state, postal, country_code = get_international(
            raw_address
        )
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("loc_lat")
        longitude = j.get("loc_long")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            inter = j.get(day.lower())
            if inter:
                _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mysecondcup.com/"
    page_url = "https://www.mysecondcup.com/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
