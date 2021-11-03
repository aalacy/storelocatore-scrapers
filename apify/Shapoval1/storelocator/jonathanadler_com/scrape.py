from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jonathanadler.com/"
    api_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=jonathanadler-com.myshopify.com&latitude=40.735165&longitude=-74.000536&max_distance=10000&limit=100"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["stores"]:

        page_url = "https://jonathanadler.com/apps/store-locator"
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = j.get("phone") or "<MISSING>"
        state = j.get("prov_state") or "<MISSING>"
        postal = j.get("postal_zip") or "<MISSING>"
        country_code = "".join(j.get("country"))
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            "".join(hours.xpath("//*/text()"))
            .replace("\n", "")
            .replace("\r", " ")
            .strip()
        )
        if (
            hours_of_operation.find("Opening Soon") != -1
            or hours_of_operation.find("Opening in ") != -1
        ):
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("The health") != -1:
            hours_of_operation = hours_of_operation.split("The health")[0].strip()
        if hours_of_operation.find("Reduced") != -1:
            hours_of_operation = hours_of_operation.split("Reduced")[0].strip()
        if hours_of_operation.find("Holiday") != -1:
            hours_of_operation = hours_of_operation.split("Holiday")[0].strip()
        if hours_of_operation.find("Available") != -1:
            hours_of_operation = hours_of_operation.split("Available")[0].strip()
        if hours_of_operation.find("Closed until") != -1:
            hours_of_operation = "Temporarily Closed"

        hours_of_operation = hours_of_operation.replace("Hours:", "").strip()

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
