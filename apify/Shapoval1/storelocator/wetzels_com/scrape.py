import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wetzels.com/"
    api_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/13346/stores.js?callback=SMcallback2"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    div = r.text.split("SMcallback2(")[1].split("}]})")[0] + "}]}"
    js = json.loads(div)

    for j in js["stores"]:

        page_url = "https://www.wetzels.com/find-a-location"
        location_name = j.get("name")
        ad = (
            "".join(j.get("address"))
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("The Bronx", ",The Bronx")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if (
            str(street_address) == "<MISSING>"
            or street_address.isdigit()
            or street_address.replace("#", "").strip().isdigit()
        ):
            street_address = ad.split(",")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if not postal.isdigit() and postal != "<MISSING>":
            country_code = "CA"
        if ad.find("República de Panamá") != -1:
            country_code = "PA"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("ext") != -1:
            phone = phone.split("ext")[0].strip()
        if phone == "N/A":
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
            store_number=SgRecord.MISSING,
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
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
