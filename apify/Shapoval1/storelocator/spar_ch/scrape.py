from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("pretext")
        time = "".join(h.get("text")).replace("\n", "").strip()
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp).replace("\n", "").strip()
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spar.ch/"
    api_url = "https://www.spar.ch/_api/markets?itemsPerPage=9999&page=1&markettype.uid%5B%5D=1&markettype.uid%5B%5D=2&markettype.uid%5B%5D=8&markettype.uid%5B%5D=9"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["hydra:member"]
    for j in js:

        page_url = j.get("singleUrl") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("markettype").get("marketType") or "<MISSING>"
        street_address = j.get("streetNumber") or "<MISSING>"
        try:
            state = j.get("region").get("isoCode")
        except:
            state = "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "CH"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("coordinatex") or "<MISSING>"
        longitude = j.get("coordinatey") or "<MISSING>"
        phone = "".join(j.get("telephone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        if phone.find("Metzgerei:") != -1:
            phone = phone.split("Metzgerei:")[0].replace("Markt:", "").strip()
        hours_of_operation = "<MISSING>"
        hours = j.get("openingHours") or "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
