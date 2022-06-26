from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://cdn.contentful.com/spaces/go5rjm58sryl/environments/master/entries?access_token=6b61TxCL9VW-1xwx-Oy4x9OOGMweRyBSDhaXCZM4d-o&include=10&limit=400&content_type=studios&select=sys.id,fields.region,fields.zenotiCenterId,fields.title,fields.slug,fields.address,fields.coordinates,fields.image,fields.openDate,fields.closed,fields.comingSoonStartDate"
    r = session.get(api, headers=headers)
    jj = r.json()

    adr = dict()
    for j in jj["includes"]["Entry"]:
        _id = j["sys"]["id"]
        adr[_id] = j["fields"]

    for j in jj["items"]:
        j = j["fields"]
        _id = j["address"]["sys"]["id"]
        a = adr.get(_id) or {}
        adr1 = a.get("addressLine1") or ""
        adr2 = a.get("addressLine2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        country_code = "US"
        store_number = j.get("Id")
        location_name = j.get("title")
        slug = j.get("slug")
        page_url = f"https://www.corepoweryoga.com/yoga-studios/{state}/{city}/{slug}"

        g = j.get("coordinates") or {}
        latitude = g.get("lat")
        longitude = g.get("lon")

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
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.corepoweryoga.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
