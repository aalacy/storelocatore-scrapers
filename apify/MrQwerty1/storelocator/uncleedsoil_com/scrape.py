import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "Referer": "https://www.uncleedsoil.com/",
        "Content-Type": "application/json",
    }

    params = (
        ("gridAppId", "a8221148-8d80-4b78-bb9c-475145f56fe9"),
        ("viewMode", "site"),
        (
            "instance",
            "wixcode-pub.0adc267734a3927053a45bf292274972075abde7.eyJpbnN0YW5jZUlkIjoiMjU4N2UwYzktODZiNC00NjI1LThiNWUtOWZiNmNiYTQzZDBlIiwiaHRtbFNpdGVJZCI6IjRlYWY3ZTJiLTY3MGMtNDIwZC04MGVhLTIyZmQ4ZDgyNjY0MSIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYzODQzMTI1NDk4MSwiYWlkIjoiYTJkYjZkYmEtNzRmMy00Nzk3LWJlMTctMzFmMTdhMzQ0MjNjIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjA0ODcxOTA3LTM5YWEtNDlkNS05ZGMwLWE4MjNmZWIwMDU5MSIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6Ikhhc0RvbWFpbixTaG93V2l4V2hpbGVMb2FkaW5nLEFkc0ZyZWUiLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiYzMxNzI5NDEtNTNlMS00Y2ZjLTkyMWYtMWJjY2M1MmY3ZGIwIiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==",
        ),
    )

    data = {
        "routerPrefix": "/oil-change-service-locations",
        "routerSuffix": "/",
        "fullUrl": "https://www.uncleedsoil.com/oil-change-service-locations/",
        "config": {
            "patterns": {
                "/": {
                    "pageRole": "a281a1e0-6ed0-45c4-ad85-0719e5844353",
                    "title": "Oil Change Locations | Uncle Ed's Oil Shoppe",
                    "config": {
                        "collection": "Items",
                        "pageSize": 30,
                        "sort": [{"title": "asc"}],
                        "lowercase": True,
                    },
                    "seoMetaTags": {
                        "robots": "index",
                        "description": "Uncle Ed's Oil Shoppe has 29 oil change locations conveniently located throughout Ann Arbor, Battle Creek, Kalamazoo: '', Detroit.",
                        "keywords": "",
                        "og:image": "",
                    },
                }
            }
        },
        "pageRoles": {
            "a281a1e0-6ed0-45c4-ad85-0719e5844353": {
                "id": "buvz8",
                "title": "Locations (All)",
            }
        },
        "requestInfo": {"env": "browser", "formFactor": "desktop"},
    }
    r = session.post(
        "https://www.uncleedsoil.com/_api/wix-code-public-dispatcher/routers/data-binding/pages",
        headers=headers,
        params=params,
        data=json.dumps(data),
    )
    js = r.json()["result"]["data"]["items"]

    for j in js:
        location_name = j.get("title")
        slug = j.get("slug") or ""
        page_url = (
            f"https://www.uncleedsoil.com/oil-change-service-location/{slug.lower()}"
        )
        p = j.get("phone") or ""
        phone = p.split("<u>")[1].split("<")[0]

        a = j.get("address") or {}
        s = a.get("streetAddress") or {}
        street_address = " ".join(s.values())
        city = a.get("city")
        state = a.get("subdivision")
        postal = a.get("postalCode") or ""
        if "-" in postal:
            postal = postal.split("-")[0].strip()

        g = a.get("location") or {}
        latitude = g.get("latitude")
        longitude = g.get("longitude")

        _tmp = []
        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//p[./strong]")

        for h in hours:
            day = "".join(h.xpath(".//text()")).strip()
            inter = "".join(h.xpath("./following-sibling::p[1]//text()")).strip()
            _tmp.append(f"{day} {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.uncleedsoil.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
