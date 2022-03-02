from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("name")
        ouverture = h.get("ouverture")
        fermeture = h.get("fermeture")
        line = f"{day} {ouverture} - {fermeture}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://micromania.fr/"
    api_url = "https://www.micromania.fr/on/demandware.store/Sites-Micromania-Site/default/Stores-FindStoresLocator?radius=30&postalCode=paris&csrf_token=-aRBephiEex8KboABax_fj_74-9XYUYYzXvSLwT-O_XSDYu-qsPFA6OuhxU5ZaMv5413L2kNfArzexrWkRxSFGiNGiAjoyZTqMO7nCA8qSnMKgugfI71YWylExISVUbMd_DF6RorW_6swxnmIdrQGcy_3Ur1IL0rzP1TLrcBp-BBplxXPpA%3D"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["stores"]
    for j in js:
        store_id = j.get("ID")
        page_url = f"https://www.micromania.fr/magasin?storeid={store_id}"
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        state = j.get("stateCode")
        if state == "Province":
            state = "<MISSING>"
        postal = j.get("postalCode")
        country_code = "FR"
        city = j.get("city")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("storeHours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)

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
