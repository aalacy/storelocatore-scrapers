from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://spudulike.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    data = {
        "action": "get_stores",
        "lat": "52.633331",
        "lng": "-1.133233",
        "radius": "999",
        "name": "",
    }
    r = session.post(
        "https://spudulikebyjamesmartin.com/wp/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )

    js = r.json()
    for j in js.values():

        page_url = j.get("gu")
        location_name = j.get("na")
        ad = f"{j.get('st')},{j.get('ct')},{j.get('rg')} {j.get('zp')}".replace(
            ",,", ""
        ).strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        if city.find(" ") != -1:
            city = city.split()[-1].strip()
        country_code = "".join(j.get("co")).strip()
        latitude = j.get("lat")
        longitude = j.get("lng")

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
            phone=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
