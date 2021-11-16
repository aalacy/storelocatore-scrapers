from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = 'https://www.vodacom.cd/integration/drcportal/store_locator/portal'
    page_url = 'https://www.vodacom.cd/particulier/assisstance/nos-vodashops/find-vodashops'
    data = '{\n  "method": "findNearestStore",\n  "longitude": 49.6074752,\n  "latitude": 34.5276416,\n  "source": "portal"\n}'
    r = session.post(api, data=data)
    js = r.json()["response"]["stores"]

    for j in js:
        location_name = j.get("nameStructure")
        street_address = j.get('address') or ''
        if '(' in street_address:
            street_address = street_address.split('(')[0].strip()
        city = j.get("city")
        state = j.get("region")
        location_type = j.get('shopType')
        latitude = j.get("lat")
        longitude = j.get("lon")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code='CD',
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.vodacom.cd/"
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))) as writer:
        fetch_data(writer)
