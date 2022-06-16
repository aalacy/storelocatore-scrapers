import usaddress
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.somisomi.com"
    api_url = "https://www.somisomi.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax?gridAppId=691d9f7c-e5ae-45f7-80d2-dd4da634f76d&instance=wixcode-pub.588edeff9198d27630ab073685d1f3a85b52f122.eyJpbnN0YW5jZUlkIjoiOGRiODM4NDAtZTM3Zi00MjgwLWFjZDAtNmRmODAwMzQyNmQ2IiwiaHRtbFNpdGVJZCI6IjdmNTg2Njk0LTQ5OTEtNGIyOC1hMmRiLTZjNDRjMzk3MTU0YiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYxNTQwNjg1NzkxOCwiYWlkIjoiMmI4NDk2MjctOWUwOC00NmFlLWEyZjYtZDlhZTBjMDE1MmQzIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjM3NjM4MmIzLTM2ZTEtNDRkNy1hZDNjLTg4NzI3YzQ2ODcyMyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsQWRzRnJlZSxIYXNEb21haW4sSGFzRUNvbW1lcmNlIiwidGVuYW50IjpudWxsLCJzaXRlT3duZXJJZCI6ImQ0OGYzZDhhLTBiNGQtNGE4MC05NTEwLTBhZWM1ZWNmN2Q3OCIsImluc3RhbmNlVHlwZSI6InB1YiIsInNpdGVNZW1iZXJJZCI6bnVsbH0=&viewMode=site"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-XSRF-TOKEN": "1615406830|cnOGV4TfqKLT",
        "x-wix-site-revision": "1841",
        "Content-Type": "application/json",
        "Origin": "https://www.somisomi.com",
        "Connection": "keep-alive",
        "Referer": "https://www.somisomi.com/_partials/wix-thunderbolt/dist/clientWorker.72a932ba.bundle.min.js",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    params = (
        ("gridAppId", "691d9f7c-e5ae-45f7-80d2-dd4da634f76d"),
        (
            "instance",
            "wixcode-pub.588edeff9198d27630ab073685d1f3a85b52f122.eyJpbnN0YW5jZUlkIjoiOGRiODM4NDAtZTM3Zi00MjgwLWFjZDAtNmRmODAwMzQyNmQ2IiwiaHRtbFNpdGVJZCI6IjdmNTg2Njk0LTQ5OTEtNGIyOC1hMmRiLTZjNDRjMzk3MTU0YiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYxNTQwNjg1NzkxOCwiYWlkIjoiMmI4NDk2MjctOWUwOC00NmFlLWEyZjYtZDlhZTBjMDE1MmQzIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjM3NjM4MmIzLTM2ZTEtNDRkNy1hZDNjLTg4NzI3YzQ2ODcyMyIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IlNob3dXaXhXaGlsZUxvYWRpbmcsQWRzRnJlZSxIYXNEb21haW4sSGFzRUNvbW1lcmNlIiwidGVuYW50IjpudWxsLCJzaXRlT3duZXJJZCI6ImQ0OGYzZDhhLTBiNGQtNGE4MC05NTEwLTBhZWM1ZWNmN2Q3OCIsImluc3RhbmNlVHlwZSI6InB1YiIsInNpdGVNZW1iZXJJZCI6bnVsbH0=",
        ),
        ("viewMode", "site"),
    )
    data = '["Locations",null,[{"title":"asc"},{"comingsoon":"asc"}],0,40,null,null]'
    r = session.post(api_url, headers=headers, params=params, data=data)
    js = r.json()["result"]
    for j in js["items"]:
        ad = "".join(j.get("address")).replace("\n", " ")
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.get("city")
        if city.find("Promenade Santa Monica") != -1:
            city = "Santa Monica"
            street_address = street_address + " " + "Promenade"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        page_url = "https://www.somisomi.com/locations-title"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = "".join(j.get("hours")).replace("\n", " ").strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
