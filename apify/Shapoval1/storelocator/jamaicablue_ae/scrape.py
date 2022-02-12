from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("days")
        time = h.get("hours")
        line = f"{day} {time}"
        tmp.append(line)
    hours_of_operation = " ".join(tmp).strip()
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jamaicablue.ae"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {"action": "fc_store_locations", "post_id": "7"}

    r = session.post(
        "https://www.jamaicablue.ae/wp-admin/admin-ajax.php", headers=headers, data=data
    )
    js = r.json()["locations"]
    for j in js:

        page_url = "https://www.jamaicablue.ae/store-locations/"
        location_name = j.get("name")
        ad = f"{j.get('address_1')} {j.get('address_2')}".strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "AE"
        city = a.city or "<MISSING>"
        if "Dubai" in location_name:
            city = "Dubai"
        try:
            latitude = f"{j.get('location')}".split("|")[1].split(",")[0].strip()
            longitude = f"{j.get('location')}".split("|")[1].split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("opening_hours") or "<MISSING>"
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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
