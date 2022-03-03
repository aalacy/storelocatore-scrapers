from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.gamestop.it/"
    api_url = "https://www.gamestop.it/StoreLocator/GetStoresForStoreLocatorByProduct?value=&skuType=0&language=en-it"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.gamestop.it/StoreLocator"
        location_name = j.get("Name")
        street_address = (
            f"{j.get('Address')} {j.get('StreetNumber')}".replace(
                "undefined", ""
            ).strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        postal = j.get("Zip") or "<MISSING>"
        country_code = "IT"
        city = j.get("City") or "<MISSING>"
        if city == "undefined":
            city = "<MISSING>"
        state = j.get("Province") or "<MISSING>"
        if state == "undefined":
            state = "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        if latitude == "undefined":
            latitude = "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        if longitude == "undefined":
            longitude = "<MISSING>"
        phone = j.get("Phones") or "<MISSING>"
        if phone == "undefined":
            phone = "<MISSING>"
        if phone.find("0/0") != -1:
            phone = phone.split("/0")[0].strip()
        if phone.find("- 0") != -1:
            phone = phone.split("- 0")[0].strip()

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
        hours_of_operation = " ".join(hours_of_operation.split()).replace(
            "-------------", ""
        )

        if (
            hours_of_operation
            == "Il presente non è un negozio aperto al pubblico e alla vendita."
        ):
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Gli orari ") != -1:
            hours_of_operation = hours_of_operation.split("Gli orari ")[0].strip()
        if (
            hours_of_operation.find("Day1 Hour1") != -1
            or hours_of_operation == "undefined"
        ):
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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
