from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(_id, page_url):
    _tmp = []
    data = {"_m_": "HoursPopup", "HoursPopup$_edit_": _id, "HoursPopup$_command_": ""}

    r = session.post(page_url, data=data)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        inter = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp) or "Coming Soon"


def fetch_data(sgw: SgWriter):
    api = "https://www.fastestlabs.com/locations/?CallAjax=GetLocations"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("FranchiseLocationName")
        slug = j.get("Path")
        page_url = f"https://www.fastestlabs.com{slug}"
        street_address = f'{j.get("Address1")} {j.get("Address2") or ""}'.strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        country = j.get("Country")

        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        location_type = j.get("LocationType")
        store_number = j.get("FranchiseLocationID")
        try:
            hours_of_operation = get_hoo(store_number, page_url)
        except:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country,
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.fastestlabs.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.fastestlabs.com/locations/",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.fastestlabs.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Content-Length": "0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
