from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sofacompany.com/"
    api_url = "https://sofacompany.com/nl-be/graphql?hash=1412213180"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]["sc_storelocator"]
    for j in js:
        country_code = j.get("storelocator_country_id") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            str(j.get("storelocator_address"))
            .replace("/ Gänsemarktpassagen ", "")
            .strip()
            or "<MISSING>"
        )
        state = "<MISSING>"
        postal = (
            str(j.get("storelocator_postcode")).replace("None", "").strip()
            or "<MISSING>"
        )
        city = "".join(j.get("storelocator_city")) or "<MISSING>"
        if city.find("(") != -1:
            city = city.split("(")[0].strip()
        if city.find(".") != -1:
            city = city.split(".")[0].strip()
        if country_code == "NL":
            state = postal.split()[1].strip()
            postal = postal.split()[0].strip()
        latitude = j.get("storelocator_lat") or "<MISSING>"
        longitude = j.get("storelocator_lon") or "<MISSING>"
        phone = j.get("storelocator_phone") or "<MISSING>"
        hours = j.get("working_hours_block")
        a = html.fromstring(hours)
        hours_of_operation = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Book videorådgivning", "")
            .replace("Normale åpningstider:", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("Helligdage") != -1:
            hours_of_operation = hours_of_operation.split("Helligdage")[0].strip()
        if hours_of_operation.find("Notera att") != -1:
            hours_of_operation = hours_of_operation.split("Notera att")[0].strip()
        if hours_of_operation.find("COVID-19:") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Een adviesgesprek") != -1:
            hours_of_operation = hours_of_operation.split("Een adviesgesprek")[
                0
            ].strip()
        if hours_of_operation.find("Husk du") != -1:
            hours_of_operation = hours_of_operation.split("Husk du")[0].strip()
        if hours_of_operation.find("Det finns") != -1:
            hours_of_operation = hours_of_operation.split("Det finns")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=SgRecord.MISSING,
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
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
