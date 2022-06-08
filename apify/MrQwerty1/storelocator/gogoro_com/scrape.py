from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_street(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def fetch_data(sgw: SgWriter):
    api = "https://official-site-pro.gogoroapp.com/PartnerService/Gogoro/GetVmList?offset=0&pageSize=10000"
    r = session.get(api, headers=headers)
    js = r.json()["Data"]

    for j in js:
        location_name = j["LocName"]["en-US"]
        raw_address = j["Address"]["en-US"]
        street_address = get_street(raw_address)
        city = j["City"]["en-US"]
        state = j["District"]["en-US"]
        postal = j.get("ZipCode")
        country_code = "TW"
        store_number = j.get("Id")
        page_url = f"https://www.gogoro.com/findus/?station={store_number}"
        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")

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
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gogoro.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
