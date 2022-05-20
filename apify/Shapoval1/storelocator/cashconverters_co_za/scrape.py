from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cashconverters.co.za/"
    api_url = "https://www.cashconverters.co.za/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=c5d52fa6f3&load_all=1&layout=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.cashconverters.co.za/store-locator"
        location_name = j.get("title") or "<MISSING>"
        street_address = "".join(j.get("street")).strip() or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country")
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        if phone.find("\\") != -1:
            phone = phone.split("\\")[0].strip()
        hours = j.get("open_hours")
        h = eval(hours)
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d
            time = "".join(h.get(f"{d}"))
            if time == "0":
                continue
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp).strip()
        if hours_of_operation.count("0;") > 1:
            hours_of_operation = "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
