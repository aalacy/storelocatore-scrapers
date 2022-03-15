from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.bel-bo.be/graphql"
    params = (
        (
            "query",
            "query Retailers($seller:String){retailerList(filters:{seller_code:{eq:$seller}}){id entity_id created_at updated_at seller_code name image description contact_phone contact_fax contact_mail meta_title meta_keywords meta_description show_contact_form allow_store_delivery address{id address_id street postcode city region region_id country_id latitude longitude __typename}opening_hours{day day_of_the_week closed time_slots{start_time end_time __typename}__typename}special_opening_hours{day date description_nl description_fr __typename}__typename}}",
        ),
        ("operationName", "Retailers"),
        ("variables", "{}"),
        ("nl", ""),
    )
    r = session.get(api, headers=headers, params=params)
    js = r.json()["data"]["retailerList"]

    for j in js:
        location_name = j.get("name")
        a = j.get("address") or {}
        street_address = a.get("street")
        if not street_address:
            continue
        city = a.get("city")
        state = a.get("region")
        postal = a.get("postcode")
        country = a.get("country_id")

        phone = j.get("contact_phone") or ""
        phone = phone.replace("/", " ")
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        location_type = j.get("__typename")
        store_number = j.get("seller_code")
        page_url = f"https://www.bel-bo.be/stores/{store_number}"

        _tmp = []
        hours = j.get("opening_hours") or []
        for h in hours:
            day = h.get("day")
            if h.get("closed"):
                _tmp.append(f"{day}: Closed")
                continue

            try:
                t = h["time_slots"][0]
            except:
                t = dict()
            start = t.get("start_time")
            end = t.get("end_time")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

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
    locator_domain = "https://www.bel-bo.be/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.bel-bo.be/nl/stores",
        "content-type": "application/json",
        "authorization": "",
        "store": "nl",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
