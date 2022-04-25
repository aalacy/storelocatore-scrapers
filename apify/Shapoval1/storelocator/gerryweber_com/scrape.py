import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day")
        time = h.get("hours")
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.gerryweber.com/"
    api_url = "https://www.gerryweber.com/en-eu/storefinder/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    div = (
        r.text.split(':stores-data="')[1]
        .split("</storefinder>")[0]
        .replace(">", "")
        .replace("\n", "")
        .replace("&quot;", '"')
        .strip()
    )
    div = "".join(div[:-1])
    js = json.loads(div)
    for j in js:

        page_url = "https://www.gerryweber.com/en-eu/storefinder/"
        location_name = (
            "".join(j.get("name")).replace("&amp;", "&").replace("&#39;", "`").strip()
        )
        street_address = (
            str(j.get("street")).replace("&#39;", "`").strip() or "<MISSING>"
        )
        state = "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country")
        if country_code == "NL" and str(postal).find(" ") != -1:
            state = str(postal).split()[1].strip()
            postal = str(postal).split()[0].strip()
        city = j.get("city") or "<MISSING>"
        city = str(city).replace("&#39;", "").strip()
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        brands = []
        gerryweber = j.get("gerryweber")
        taifun = j.get("taifun")
        samoon = j.get("samoon")
        outlet = j.get("outlet")
        if gerryweber:
            brands.append("gerryweber")
        if taifun:
            brands.append("taifun")
        if samoon:
            brands.append("samoon")
        if outlet:
            brands.append("outlet")

        location_type = ", ".join(brands) or "<MISSING>"
        if not gerryweber and not taifun and not samoon:
            location_type = "outlet"
        phone = (
            str(j.get("phone"))
            .replace("\n", "")
            .replace("\r", "")
            .replace("Würzburg", "")
            .replace("/ -3754", "")
            .replace("/ im Haus", "")
            .replace("direkt", "")
            .replace("- privat", "")
            .replace("NULL", "")
            .replace("None", "")
            .replace("(Retouren)", "")
            .replace("Challenge", "")
            .replace("Kaarst", "")
            .strip()
            or "<MISSING>"
        )
        if phone.count("+") > 2:
            phone = phone.split("+")[1].strip()
        if len(phone) < 6 or phone == "0031-":
            phone = "<MISSING>"
        hours = j.get("openingTimes") or "<MISSING>"
        hours_of_operation = "<MISSING>"
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
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
