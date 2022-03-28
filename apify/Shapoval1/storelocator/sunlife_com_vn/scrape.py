from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sunlife.com.vn/"
    api_url = "https://www.sunlife.com.vn/content/dam/sunlife/legacy/assets/vn/ve-chung-toi/lien-he/mang-luoi-trung-tam-dich-vu-khach-hang/office_locator.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        city = j.get("p_name")
        page_url = "https://www.sunlife.com.vn/vn/ve-chung-toi/lien-he/mang-luoi-trung-tam-dich-vu-khach-hang/"
        locations = j.get("office_list")
        for l in locations:

            location_name = l.get("officename") or "<MISSING>"
            ad = l.get("address")
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if len(street_address) < 6:
                street_address = ad
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "VN"
            latitude = l.get("lat") or "<MISSING>"
            longitude = l.get("lng") or "<MISSING>"
            phone = str(l.get("telephone")) or "<MISSING>"
            if phone.find("- ext") != -1:
                phone = phone.split("- ext")[0].strip()
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
