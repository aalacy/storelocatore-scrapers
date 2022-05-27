from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda-indonesia.com"
    api_url = "https://www.honda-indonesia.com/api/dealers"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("url")
        location_name = j.get("name") or "<MISSING>"
        ad = (
            "".join(j.get("address")).replace("\n", " ").replace("\r", " ").strip()
            or "<MISSING>"
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        try:
            state = j.get("province").get("province_name")
        except:
            state = "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "IN"
        try:
            city = j.get("city").get("city_name")
        except:
            city = "<MISSING>"
        if city == "<MISSING>":
            city = a.city or "<MISSING>"
        if state == "<MISSING>":
            state = a.state or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = str(j.get("telephone")).replace("[Hunting]", " ").strip() or "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
            phone = " ".join(phone.split())
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        if phone.find("(") != -1:
            phone = phone.split("(")[0].strip()
        phone = (
            " ".join(phone.split())
            .replace(" äóñ", "")
            .replace(" - ", "-")
            .replace("021-58356048021-58356897", "021-58356048 021-58356897")
            .strip()
            or "<MISSING>"
        )
        if phone == "-":
            phone = "<MISSING>"
        if phone.find(" 0") != -1:
            phone = phone.split(" 0")[0].strip()
        hours_of_operation = (
            "".join(j.get("working_hour"))
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("<br>", " ")
            .replace("Showroom :", "")
            .replace("<p>", "")
            .replace("</p>", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if (
            hours_of_operation.find("div") != -1
            or hours_of_operation.find("span") != -1
        ):
            a = html.fromstring(hours_of_operation)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("<") != -1:
            hours_of_operation = hours_of_operation.split("<")[0].strip()
        if hours_of_operation.find("Bengkel") != -1:
            hours_of_operation = hours_of_operation.split("Bengkel")[0].strip()
        if hours_of_operation.find("Service") != -1:
            hours_of_operation = hours_of_operation.split("Service")[0].strip()
        store_number = j.get("id")

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
