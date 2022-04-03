from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.dunnesstores.com/"
    api_url = "https://www.dunnesstores.com/store-locator/stores/ajax.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["payload"]
    for j in js.values():
        for k in j:

            page_url = (
                f"https://www.dunnesstores.com/store-locator/stores/{k.get('id')}"
            )
            if page_url == "https://www.dunnesstores.com/store-locator/stores/999":
                continue
            location_name = "".join(k.get("name")).replace(",", "").strip()
            location_type = k.get("type")
            street_address = (
                f"{k.get('address1')} {k.get('address2')} {k.get('address3')}".strip()
            )
            if street_address.find("Dunnes Stores,") != -1:
                street_address = street_address.replace("Dunnes Stores,", "").strip()
            street_address = street_address.replace(",", "").strip()
            state = k.get("countryRegion")
            postal = "".join(k.get("postcode")) or "<MISSING>"
            if postal.find("C.P.") != -1:
                postal = postal.replace("C.P.", "").strip()
            country_code = k.get("countryIso2").get("value")
            cityI = "".join(k.get("city"))
            if cityI.find(",") != -1:
                cityI = cityI.replace(",", "").strip()
            cityInfo = cityI.split()
            tmpc = []
            for c in cityInfo:
                if c.isdigit():
                    continue
                tmpc.append(c)
            city = " ".join(tmpc).replace("1.", "")
            store_number = k.get("id")
            latitude = k.get("latitude")
            longitude = k.get("longitude")
            phone = k.get("phone") or "<MISSING>"
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            tmp = []
            for d in days:
                day = str(d)
                time = "".join(k.get(f"{d}OpenTimes"))
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace(":--", "").replace("--:", "").strip()
                or "<MISSING>"
            )
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

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
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
