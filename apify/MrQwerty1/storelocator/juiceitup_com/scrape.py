from lxml import html
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hours(url):
    _id = url[0]
    url = url[1]
    data = {"_m_": "HoursPopup", "HoursPopup$_edit_": _id, "HoursPopup$_command_": ""}

    try:
        r = session.post(url, data=data)
        tree = html.fromstring(r.text)
    except:
        return {_id: "Coming Soon"}

    _tmp = []
    hours = tree.xpath("//tr")
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        time = "".join(h.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    hoo = ";".join(_tmp)

    return {_id: hoo}


def fetch_data(sgw: SgWriter):
    urls = []
    hours = []
    r = session.get("https://www.juiceitup.com/stores/?CallAjax=GetLocations")
    js = r.json()

    for j in js:
        urls.append(
            [j.get("FranchiseLocationID"), "https://www.juiceitup.com" + j.get("Path")]
        )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hour = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = "https://www.juiceitup.com" + j.get("Path")
        _id = j.get("FranchiseLocationID")
        location_name = j.get("BusinessName")
        street_address = f'{j.get("Address1")} {j.get("Address2") or ""}'.strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = hour.get(_id)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=_id,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.juiceitup.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
