import json
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

    return street, city, state, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    api = "https://arcencohogareasy.vtexassets.com/_v/public/assets/v1/published/bundle/public/react/asset.min.js?v=1&files=arcencohogareasy.store-theme@4.0.14,common,0,Locales&workspace=master"
    r = session.get(api, headers=headers)
    text = r.text.split("JSON.parse('")[-1].split("]}]')}")[0] + "]}]"
    js = json.loads(text)

    for j in js:
        raw_address = j.get("direccionLocal")
        street_address, city, state, postal = get_international(raw_address)
        country_code = "AR"
        store_number = j.get("localId")
        location_name = j.get("nombreLocal")
        phone = j.get("telefonoLocal")

        source = j.get("mapSource") or ""
        latitude, longitude = get_coords_from_embed(source)

        hoo1 = j.get("horarioLocal") or ""
        hoo2 = j.get("horarioLocal2") or ""
        hours_of_operations = f"{hoo1};{hoo2}".strip()
        if hours_of_operations.endswith(";"):
            hours_of_operations = hours_of_operations[:-1]

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
            hours_of_operation=hours_of_operations,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.easy.com.ar/"
    page_url = "https://www.easy.com.ar/locales"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
