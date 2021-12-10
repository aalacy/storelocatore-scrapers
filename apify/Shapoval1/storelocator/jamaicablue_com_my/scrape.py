from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jamaicablue.com.my"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {"action": "fc_store_locations", "post_id": "7"}

    r = session.post(
        "https://www.jamaicablue.com.my/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )
    js = r.json()["locations"]
    for j in js:

        page_url = "https://www.jamaicablue.com.my/store-locations/"
        location_name = str(j.get("name")).replace("&amp;", "&").strip()
        ad = f"{j.get('address_1')} {j.get('address_2')}".strip() or "<MISSING>"
        if ad == "<MISSING>":
            ad = f"{j.get('location')}".split("|")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if "40170" in ad:
            postal = "40170"
        country_code = "MY"
        city = a.city or "<MISSING>"
        if "Bangsar" in street_address:
            city = "Bangsar"
        try:
            latitude = f"{j.get('location')}".split("|")[1].split(",")[0].strip()
            longitude = f"{j.get('location')}".split("|")[1].split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("opening_hours") or "<MISSING>"
        tmp = []
        if hours != "<MISSING>":
            for h in hours:
                day = h.get("days")
                time = h.get("hours")
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = " ".join(tmp).strip()

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
