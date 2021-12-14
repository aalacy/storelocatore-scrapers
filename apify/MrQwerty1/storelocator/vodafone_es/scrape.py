from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(api_url):
    _tmp = []
    r = session.get(api_url, headers=headers)
    try:
        j = r.json()["hours"]
        for day, inters in j.items():
            i = []
            for inter in inters:
                start = inter.get("from")
                end = inter.get("to")
                i.append(f"{start}-{end}")
            _tmp.append(f'{day}: {",".join(i)}')
    except:
        pass

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://tiendas.vodafone.es/api-stores"
    r = session.get(api, headers=headers)

    for j in r.json()["locations"]:
        location_name = j.get("name")
        store_number = j.get("external_id")
        page_url = j.get("url")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        street_address = j.get("street_address")
        city = j.get("locality")
        state = j.get("region")
        postal = j.get("postcode")
        api_url = j.get("api_url")
        if api_url:
            hours_of_operation = get_hoo(api_url)
        else:
            hours_of_operation = SgRecord.MISSING

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="ES",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.es/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
