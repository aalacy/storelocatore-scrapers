from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://graphql.contentful.com/content/v1/spaces/13n1l6os99jz/"

    headers = {"authorization": "Bearer BlDmgl7JtKeJ-tRqK8y-Nxt5Q7bjpRiJUb6aL2vHw8U"}
    data = {
        "query": '        query storeCollection {            storeCollection(skip: 0, limit: 1000, where:{AND: [{type: "Drybar Shop"}]}) {                items {                    title                    number                    bookerLocationId                    type                    information                    contact                    slug                    settings                    arrivalInformation                }            }        }    '
    }

    r = session.post(api, headers=headers, data=data)
    js = r.json()["data"]["storeCollection"]["items"]

    for j in js:
        location_name = j.get("title") or ""
        if "test " in location_name.lower():
            continue

        slug = j.get("slug") or ""
        page_url = f"https://www.drybarshops.com/service/locator/detail/{slug}"
        location_type = j.get("type")
        store_number = str(j.get("bookerLocationId"))

        c = j.get("contact") or {}
        s = j.get("settings") or {}

        street_address = c.get("street1")
        city = c.get("city") or ""
        if "Street" in city:
            city = city.split("Street")[-1].strip()
        state = c.get("state")
        postal = c.get("postalCode") or ""
        country_code = "US"
        if len(postal.strip()) > 5:
            country_code = "CA"
        phone = c.get("phoneNumber") or ""
        if not phone.strip():
            phone = SgRecord.MISSING
        latitude, longitude = c.get("coordinates") or [
            SgRecord.MISSING,
            SgRecord.MISSING,
        ]

        _tmp = []
        hours = s.get("operatingHours") or []
        for h in hours:
            try:
                if h[0][0].isdigit():
                    continue
            except:
                continue
            _tmp.append(": ".join(h))

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        status = s.get("operatingStatus") or ""
        if "coming" in status.lower():
            continue

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "thedrybar.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
