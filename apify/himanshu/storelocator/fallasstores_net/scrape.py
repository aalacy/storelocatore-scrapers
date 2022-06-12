from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fallasstores.net/"
    api_url = "https://api.storerocket.io/api/user/1vZ4v6y4Qd/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]["locations"]
    for j in js:

        page_url = "https://www.fallasstores.net/store-locator-map"
        location_name = j.get("name") or "<MISSING>"
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        if str(ad).find("PR,") != -1:
            street_address = " ".join(ad.split(",")[:-3])
            city = ad.split(",")[-3].strip()
            state = ad.split(",")[-2].strip()
            postal = ad.split(",")[-1].strip()
        if str(location_name).find("El Paso- S-antonio") != -1:
            street_address = ad.split(",")[0].strip()
        if ad.find(" Puerto Rico") != -1:
            state = "PR"
        phone = j.get("phone") or "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = str(d).capitalize()
            times = j.get(f"{d}")
            line = f"{day} {times}"
            tmp.append(line)
        hours_of_operation = " ;".join(tmp) or "<MISSING>"
        if hours_of_operation.count("None") == 7:
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
