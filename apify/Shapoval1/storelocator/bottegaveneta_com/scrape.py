from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bottegaveneta.com/"
    countries = ["US", "CA"]
    for c in countries:
        api_url = f"https://www.bottegaveneta.com/on/demandware.store/Sites-BV-INTL-Site/en_ZW/Stores-FindStoresData?countryCode={c}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()
        for j in js["storesData"]["stores"]:
            page_url = j.get("detailsUrl")
            location_name = j.get("name")
            street_address = f"{j.get('address1')} {j.get('address2') or ''}".replace(
                "None", ""
            ).strip()
            phone = j.get("phone")
            state = j.get("stateCode")
            postal = j.get("postalCode")
            country_code = "".join(c).upper()
            city = j.get("city")
            store_number = j.get("ID")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            tmp = []
            for d in days:
                day = d
                time = j.get(f"{d}Hours")
                line = f"{day} {time}".replace("NO DATA", "<MISSING>")
                tmp.append(line)
            hours_of_operation = ";".join(tmp) or "<MISSING>"
            if hours_of_operation.count("<MISSING>") == 7:
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
