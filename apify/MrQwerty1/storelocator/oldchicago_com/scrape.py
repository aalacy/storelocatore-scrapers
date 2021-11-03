import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(page_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Restaurant')]/text()"))
    j = json.loads(text)
    g = j.get("geo") or {}
    lat = g.get("latitude")
    lng = g.get("longitude")
    phone = "".join(tree.xpath("//p[@class='location-phone']/a/text()")).strip()

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = h.get("dayOfWeek")
        start = h.get("opens")
        end = h.get("closes")
        _tmp.append(f"{day}: {start}-{end}")

    return phone, lat, lng, ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    headers = {"Content-Type": "application/json"}
    api = "https://oc-api-prod.azurewebsites.net/graphql"
    r = session.post(api, headers=headers, data=json.dumps(data))

    js = r.json()["data"]["node"]["_locations3pwhxm"]["edges"]

    for j in js:
        j = j["node"]
        a = j.get("address")
        street_address = f"{a.get('streetNumber')} {a.get('route') or ''}".strip()
        city = a.get("city")
        state = a.get("stateCode")
        postal = a.get("postalCode")
        country_code = "US"
        store_number = j.get("locationId")
        page_url = f'https://oldchicago.com/locations/{j.get("slug")}'
        location_name = j.get("title")
        phone = j.get("phone")
        latitude = j.get("latitude") or ""
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("simpleHours", []) or []
        for h in hours:
            day = h.get("days")
            time = h.get("hours")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp)
        if not phone:
            phone, latitude, longitude, hours_of_operation = get_additional(page_url)

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://oldchicago.com/"
    data = {
        "query": 'query LocationList_ViewerRelayQL($id_0:ID!) {node(id:$id_0) {...F0}} fragment F0 on Viewer {_locations3pwhxm:locations(first:1500,geoString:"") {edges {node {id,slug,locationId,title,isOpen,latitude,longitude,simpleHours {days,hours,id},distance,distancefromSearch,searchLatitude,searchLongitude,phone,address {route,streetNumber,stateCode,stateName,city,postalCode,id},comingSoon},cursor},pageInfo {hasNextPage,hasPreviousPage}},id}',
        "variables": {"id_0": "Vmlld2VyOjA="},
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
