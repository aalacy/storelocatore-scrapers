from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.gamestop.ie/"
    api_url = "https://www.gamestop.ie/StoreLocator/GetStoresForStoreLocatorByProduct?value=&skuType=0&language=en-ie"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.gamestop.ie/StoreLocator"
        location_name = j.get("Name")
        street_address = j.get("Address")
        postal = j.get("Zip") or "<MISSING>"
        if postal == "undefined":
            postal = "<MISSING>"
        country_code = "IE"
        city = "".join(j.get("City")) or "<MISSING>"
        if city == "undefined":
            city = "<MISSING>"
        state = "<MISSING>"
        if city.find(",") != -1:
            state = city.split(",")[1].strip()
            city = city.split(",")[0].strip()
        if city.find(" ") != -1:
            city = city.split()[0].strip()
        if state.find(" ") != -1:
            state = state.split()[0].strip()
        if postal == "Dublin":
            postal = "<MISSING>"
            state = "Dublin"
        latitude = j.get("Latitude") or "<MISSING>"
        if latitude == "undefined":
            latitude = "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        if longitude == "undefined":
            longitude = "<MISSING>"
        phone = j.get("Phones") or "<MISSING>"
        if phone == "undefined":
            phone = "<MISSING>"
        hours = j.get("Hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()"))
                .replace("\r\n", "")
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation == "undefined":
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("closed due to") != -1:
            hours_of_operation = "Closed"
        if hours_of_operation.find("will be fully open.") != -1:
            hours_of_operation = hours_of_operation.split("will be fully open. ")[
                1
            ].strip()

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
