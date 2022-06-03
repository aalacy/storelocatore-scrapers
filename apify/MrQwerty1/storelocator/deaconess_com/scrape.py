import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    params = (
        ("x-algolia-application-id", "384Z147YW1"),
        ("x-algolia-api-key", "eb5ea2fbb3f31a5f31b8236aaad3d350"),
    )
    data = {
        "requests": [
            {
                "indexName": "PRD_Locations",
                "params": "query=&hitsPerPage=5000&maxValuesPerFacet=5000",
            }
        ]
    }
    r = session.post(
        "https://384z147yw1-2.algolianet.com/1/indexes/*/queries",
        params=params,
        data=json.dumps(data),
    )
    js = r.json()["results"][0]["hits"]

    for j in js:
        street_address = j.get("StreetAddress")
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zip")
        country_code = "US"
        store_number = j.get("ItemID")
        slug = j.get("LocationPageURL") or ""
        if slug.startswith("http"):
            page_url = slug
        elif not slug:
            page_url = SgRecord.MISSING
        else:
            page_url = f"https://www.deaconess.com{slug}"

        location_name = j.get("LocationName") or ""
        if "-" in location_name:
            location_name = location_name.split("-")[0].strip()
        phone = j.get("Phone") or ""
        phone = phone.replace("&nbsp;", "").strip()
        if ">" in phone:
            phone = phone.split(">")[1].split("<")[0]
        if "(" in phone:
            phone = phone.split("(")[0].strip()
        if "E" in phone:
            phone = phone.split("E")[0].strip()

        loc = j.get("_geoloc") or {}
        latitude = loc.get("lat")
        longitude = loc.get("lon")
        location_type = j.get("LocationTypeName")
        if "-" in location_type:
            location_type = location_type.split("-")[-1].strip()

        _tmp = []
        source = j.get("OfficeHours") or "<html></html>"
        tree = html.fromstring(source)
        for t in tree.xpath("//text()"):
            if (
                "*" in t
                or "vary" in t.lower()
                or "Located" in t
                or "Patients" in t
                or not t.strip()
            ):
                continue
            _tmp.append(t.replace("&nbsp;", " ").strip())

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.deaconess.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
