import uuid
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    if len(street) < 7:
        street = line.split(",")[0].strip()

    return street


def fetch_data(sgw: SgWriter):
    ccs = ["th", "tw", "sg", "my", "id", "hk"]
    for cc in ccs:
        locator_domain = f"https://{cc}.oakley.com/"
        page_url = f"https://{cc}.oakley.com/en/store-finder"
        api = f"https://{cc}.oakley.com/assets/json/{cc}-stores.json"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            country_code = cc.upper()
            street_address = j.get("address") or ""
            if cc in ("th", "tw", "hk"):
                street_address = get_street(street_address)
            city = j.get("city") or ""
            state = j.get("state") or ""
            postal = j.get("postal") or ""
            store_number = uuid.uuid4().hex
            location_name = j.get("name")
            phone = j.get("phone") or ""
            phone = phone.replace("Sementara", "").strip()
            if "/" in phone:
                phone = phone.split("/")[0].strip()
            if "E" in phone:
                phone = phone.split("E")[0].strip()

            latitude = j.get("lat")
            longitude = j.get("lng")

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
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
