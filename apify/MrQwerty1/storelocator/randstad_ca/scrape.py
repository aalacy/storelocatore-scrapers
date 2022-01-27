import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hours(page_url):
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//*[contains(@class, 'time-table__item ')]")
    for l in li:
        day = "".join(l.xpath("./span[1]/text()")).strip()
        time = "".join(l.xpath("./span[2]/text()")).strip()
        line = f"{day} {time}".strip()
        if line:
            _tmp.append(line)

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.randstad.ca/api/branches/get-callback"
    for i in range(1, 1000):
        data = {
            "callback": "@Callbacks/getSearchResults",
            "currentRoute": {
                "path": "/locations/:searchParams*",
                "url": f"/locations/page-{i}/",
                "isExact": True,
                "params": {"searchParams": f"page-{i}/"},
                "routeName": "our-offices",
            },
            "data": {"language": "en"},
        }
        r = session.post(api, headers=headers, data=json.dumps(data))
        js = r.json()["searchResults"]["hits"]["hits"]

        for j in js:
            j = j.get("_source")
            location_name = "".join(j.get("title_office") or [])
            page_url = f'{locator_domain}{"".join(j.get("url") or [])}'
            adr = "".join(j.get("address_line1") or [])
            adr2 = "".join(j.get("address_line2") or [])
            street_address = f"{adr} {adr2}".strip()
            if not street_address:
                continue
            city = "".join(j.get("locality") or [])
            state = "".join(j.get("administrative_area") or [])
            postal = "".join(j.get("postal_code") or [])
            store_number = page_url.split("_")[1].replace("/", "")
            try:
                phone = j.get("field_phone")[0].strip()
                if phone.find("\n") != -1:
                    phone = phone.split("\n")[0].strip()
            except TypeError:
                phone = SgRecord.MISSING

            try:
                latitude = j.get("lat")[0]
                longitude = j.get("lng")[0]
            except TypeError:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
            hours_of_operation = get_hours(page_url)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="CA",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 5:
            break


if __name__ == "__main__":
    locator_domain = "https://www.randstad.ca"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
