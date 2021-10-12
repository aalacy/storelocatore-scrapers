from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.buildabear.co.uk/on/demandware.store/Sites-buildabear-uk-Site/en_GB/Stores-GetNearestStores?latitude=51.5073509&longitude=-0.1277583&countryCode=UK&distanceUnit=mi&maxdistance=2000"

    r = session.get(api)
    js = r.json()["stores"].items()

    for _id, j in js:
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("stateCode")
        postal = j.get("postalCode")
        country_code = j.get("countryCode")
        if country_code == "UK":
            country_code = "GB"
        page_url = f"https://www.buildabear.co.uk/locations?StoreID={_id}"
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        source = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//li")
        for h in hours:
            _tmp.append(" ".join("".join(h.xpath(".//text()")).split()))

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=_id,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.buildabear.co.uk/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
