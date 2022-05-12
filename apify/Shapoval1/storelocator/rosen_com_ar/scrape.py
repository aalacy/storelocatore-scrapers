from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.rosen.com.ar/"
    page_url = "https://www.rosen.com.ar/files/subpages.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    div = r.text.split("self.stores.json =")[1].split(";")[0].strip()
    js = eval(div)
    for j in js:
        country_code = j
        for c in js[f"{country_code}"]:
            location_type = c
            for l in js[f"{country_code}"][f"{location_type}"]:

                location_name = l.get("name") or "<MISSING>"
                ad = (
                    "".join(l.get("address"))
                    .replace("\n", " ")
                    .replace("\r", "")
                    .strip()
                )
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                city = a.city or "<MISSING>"
                latitude = l.get("lat") or "<MISSING>"
                longitude = l.get("lng") or "<MISSING>"
                phone = l.get("phone") or "<MISSING>"
                hours_of_operation = (
                    "".join(l.get("schedule"))
                    .replace("\n", " ")
                    .replace("\r", " ")
                    .replace("Horario Verano:", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split())

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
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
