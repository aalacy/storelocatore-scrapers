from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfcku.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Alt-Used": "kfcku.com",
        "Connection": "keep-alive",
        "Referer": "https://kfcku.com/store",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    r = session.get("https://kfcku.com/api/stores?page=1", headers=headers)
    js = r.json()
    last_page = js.get("last_page")
    session = SgRequests()
    for i in range(1, last_page + 1):
        r = session.get(f"https://kfcku.com/api/stores?page={i}", headers=headers)
        js = r.json()
        for j in js["data"]:
            page_url = "https://kfcku.com/store"
            location_name = j.get("name") or "<MISSING>"
            ad = "".join(j.get("address"))
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            if postal == "L3A-FCK-022-024A":
                postal = "<MISSING>"
            state = j.get("district").get("province").get("name")
            country_code = "Indonesia"
            city = j.get("district").get("name")
            services = j.get("store_services")
            tmp = []
            for s in services:
                service = s.get("name")
                line = f"{service}"
                tmp.append(line)
            location_type = ", ".join(tmp) or "<MISSING>"
            latitude = j.get("lat")
            longitude = j.get("long")
            try:
                phone = "".join(j.get("offices").get("phone"))
            except:
                phone = "<MISSING>"
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            try:
                hours_of_operation = j.get("offices").get("working") or "<MISSING>"
            except:
                hours_of_operation = "<MISSING>"
            if hours_of_operation != "<MISSING>":
                hours_of_operation = "".join(hours_of_operation)

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
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
