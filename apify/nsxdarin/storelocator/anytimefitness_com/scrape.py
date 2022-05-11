from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.anytimefitness.com/"
    api_url = "https://www.anytimefitness.com/wp-content/uploads/locations.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        a = j.get("content")
        page_url = a.get("url") or "<MISSING>"
        location_name = a.get("title") or "<MISSING>"
        street_address = (
            f"{a.get('address')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        if str(postal).find("-") != -1:
            postal = str(postal).split("-")[1].strip()

        country_code = a.get("country") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        if country_code == "ES" and not str(postal).replace(" ", "").isdigit():
            postal = "<MISSING>"
        if country_code == "NL" and str(postal).find(" ") != -1:
            state = str(postal).split()[1].strip()
            postal = str(postal).split()[0].strip()
        store_number = a.get("number") or "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = a.get("phone") or "<MISSING>"
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        if str(phone).find(",") != -1:
            phone = str(phone).split(",")[0].strip()
        hours_of_operation = "<MISSING>"
        hours = a.get("hours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                opens = str(h.get("openTime"))[:2] + ":" + str(h.get("openTime"))[2:]
                closes = str(h.get("closeTime"))[:2] + ":" + str(h.get("closeTime"))[2:]
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STORE_NUMBER})
        )
    ) as writer:
        fetch_data(writer)
