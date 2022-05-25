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
        status = a.get("status")

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
        if str(postal).find("Singapore") != -1:
            postal = str(postal).replace("Singapore", "").strip()
        store_number = a.get("number") or "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = a.get("phone") or "<MISSING>"
        if str(phone).find("/") != -1:
            phone = str(phone).split("/")[0].strip()
        if str(phone).find(",") != -1:
            phone = str(phone).split(",")[0].strip()
        hours = a.get("hours")
        tmp_1 = []
        tmp_2 = []
        tmp_3 = []
        tmp_4 = []
        tmp_5 = []
        tmp_6 = []
        tmp_7 = []

        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "monday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_1.append(line)
        monday = "; ".join(tmp_1).replace("; monday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "tuesday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_2.append(line)
        tuesday = "; ".join(tmp_2).replace("; tuesday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "wednesday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_3.append(line)
        wednesday = "; ".join(tmp_3).replace("; wednesday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "thursday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_4.append(line)
        thursday = "; ".join(tmp_4).replace("; thursday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "friday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_5.append(line)
        friday = "; ".join(tmp_5).replace("; friday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "saturday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_6.append(line)
        saturday = "; ".join(tmp_6).replace("; saturday", " |").strip() or "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("dayOfWeek")
                if day != "sunday":
                    continue
                opens = h.get("openTime")
                opens = "".join(opens[:-2]) + ":" + "".join(opens[-2:])
                closes = h.get("closeTime")
                closes = "".join(closes[:-2]) + ":" + "".join(closes[-2:])
                line = f"{day} {opens} - {closes}"
                tmp_7.append(line)
        sunday = "; ".join(tmp_7).replace("; sunday", " |").strip() or "<MISSING>"
        hours_of_operation = (
            f"{monday}; {tuesday}; {wednesday}; {thursday}; {friday}; {saturday}; {sunday}".replace(
                "; <MISSING>", ""
            ).strip()
            or "<MISSING>"
        )
        if status == "1" or status == "2":
            hours_of_operation = "Coming Soon"
        if hours_of_operation != "<MISSING>":
            hours_of_operation = hours_of_operation.replace("<MISSING>;", "").strip()

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
