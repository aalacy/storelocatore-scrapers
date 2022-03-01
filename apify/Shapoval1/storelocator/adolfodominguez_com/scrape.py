from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.adolfodominguez.com/"
    api_url = "https://www.adolfodominguez.com/on/demandware.store/Sites-ad-us-Site/en_US/Stores-FindStores?showMap=true&radius=2000000.0&lat=35.86166&long=104.195397"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:

        page_url = "https://www.adolfodominguez.com/en-us/stores?showMap=true"
        location_name = j.get("name") or "<MISSING>"
        location_type = "<MISSING>"
        if "EL CORTE INGLÉS" in location_name:
            location_type = "El Corto Ingles"
        ad = "".join(j.get("address1"))
        if ad.find("Email") != -1:
            ad = ad.split("Email")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if (
            street_address.isdigit()
            or street_address == "<MISSING>"
            or len(street_address) < 10
        ):
            street_address = ad.split(",")[0].strip()
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("countryCode")
        city = j.get("city") or "<MISSING>"
        store_number = j.get("ID")
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if str(phone).find("(") != -1:
            phone = phone.split("(")[0].strip()
        hours_of_operation = j.get("storeHours") or "<MISSING>"

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
            raw_address=f"{ad} {city}, {state} {postal}".replace(
                "<MISSING>", ""
            ).strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
