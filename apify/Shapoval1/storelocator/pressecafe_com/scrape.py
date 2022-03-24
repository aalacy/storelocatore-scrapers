from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://pressecafe.com/fr/"
    api_url = "http://pressecafe.com/fr/stores/?ajax=1&lat=0.37540639340998183&lng=0&dist=19895123.67285176"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["stores"]:

        a = j.get("fields")
        street_address = a.get("address") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        state = a.get("province") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        location_name = a.get("name") or "<MISSING>"
        phone = "".join(a.get("phone")) or "<MISSING>"
        if phone.find("poste") != -1:
            phone = phone.split("poste")[0].strip()
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        hours_of_operation = (
            f"Monday {a.get('monday_hours')} Tuesday {a.get('tuesday_hours')} Wednesday {a.get('wednesday_hours')} Thursday {a.get('thursday_hours')} Friday {a.get('friday_hours')} Saturday {a.get('saturday_hours')} Sunday {a.get('sunday_hours')}"
            or "<MISSING>"
        )
        page_url = "http://pressecafe.com/fr/stores/"
        if phone == "NA":
            phone = "<MISSING>"
        if postal == "NA":
            postal = "<MISSING>"
        if hours_of_operation.find("NA") != -1:
            hours_of_operation = hours_of_operation.replace("NA", "<MISSING>").strip()
        if hours_of_operation.count("<MISSING>") == 7:
            hours_of_operation = "<MISSING>"
        if (
            hours_of_operation.find(
                "Monday  Tuesday  Wednesday  Thursday  Friday  Saturday  Sunday"
            )
            != -1
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
