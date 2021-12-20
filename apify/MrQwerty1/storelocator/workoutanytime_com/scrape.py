import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.workoutanytime.com/locations"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    text = (
        "".join(tree.xpath("//script[contains(text(), 'storeDataAry')]/text()"))
        .split(" = ")[1]
        .split(";\n")[0]
    )
    js = json.loads(text)

    for j in js:
        adr = j.get("address") or ""
        adr = (
            adr.replace("\n", "")
            .replace("\r", "")
            .replace("<br/>", "<br />")
            .split("<br />")
        )
        adr = list(filter(None, [a.strip() for a in adr]))

        street_address = ", ".join(adr[:-1])
        adr = adr[-1]
        city = adr.split(",")[0]
        adr = adr.split(",")[1].strip()
        state = adr.split()[0]
        postal = adr.split()[-1]
        store_number = j.get("club_id")
        page_url = f'https://workoutanytime.com/{j.get("slug")}/'
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("hours") or ""
        for h in hours.split("<br />"):
            if (h.find(":") != -1 or h.find("-") != -1) and h.find("hours") == -1:
                _tmp.append(h.strip())

        hours_of_operation = ";".join(_tmp).replace("<br/>", ";")

        if j.get("status") == "coming_soon" or j.get("status") == "presales":
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.workoutanytime.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
