from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_url = "https://api.storerocket.io/api/user/56wpZAy8An/locations?units=miles"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    s = set()
    for j in js["results"]["locations"]:
        slug = j.get("slug")
        page_url = f"https://coinflip.tech/bitcoin-atm?location={slug}"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("location_type_name")
        country_code = j.get("country") or "US"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            f"mon {j.get('mon')} tue {j.get('tue')} wed {j.get('wed')} thu {j.get('thu')} fri {j.get('fri')} sat {j.get('sat')} sun {j.get('sun')}"
            or "<MISSING>"
        )
        raw_address = (
            "".join(j.get("address"))
            .replace(", USA", "")
            .replace(", US", "")
            .replace("8412, 5025", "5025")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), raw_address)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city or "<MISSING>"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"

        line = latitude
        if line in s and line != "<MISSING>":
            continue
        s.add(line)
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
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://coinflip.tech"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
