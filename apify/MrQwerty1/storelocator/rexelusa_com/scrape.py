import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "Origin": "https://www.rexelusa.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = [
        {
            "operationName": "Locations",
            "variables": {"bannerCode": "REXEL"},
            "query": 'query Locations($bannerCode: BannerCodeEnum!) {\n  locations {\n    totalCount\n    nodes {\n      __typename\n      bannerBranchNumber\n      bannerCode\n      branchFeatures\n      branchMarkets\n      displayName\n      distributionCenter {\n        __typename\n        bannerBranchNumber\n        displayName\n        number\n      }\n      holidays {\n        nodes {\n          isOpen\n          __typename\n        }\n        __typename\n      }\n      hours {\n        closeTime\n        dayName\n        isOpen\n        openTime\n        __typename\n      }\n      imageUrl\n      isEntity\n      location {\n        address {\n          city\n          countryCode\n          countrySubdivisionCode\n          formattedLine\n          formattedLines\n          line1\n          line2\n          line3\n          postalCode\n          __typename\n        }\n        coords {\n          lat\n          long\n          __typename\n        }\n        countrySubdivision {\n          code\n          name\n          __typename\n        }\n        __typename\n      }\n      marketingMessage\n      number\n      phone {\n        nationalFormat\n        rawNumber\n        __typename\n      }\n      showOnLocationsPage\n      urlInternal {\n        page\n        routeId\n        slug\n        __typename\n      }\n    }\n    __typename\n  }\n  viewer(bannerCode: $bannerCode) {\n    customerByIdOrDefaultV2 {\n      cmsPageBySlug(slug: "locations") {\n        ...cmsPage\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment cmsPage on CmsPage {\n  id\n  title\n  pageMeta {\n    ...pageMetadata\n    __typename\n  }\n  urlExternal {\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment pageMetadata on PageMetadata {\n  description\n  pageTitlePartial\n  __typename\n}\n',
        }
    ]
    r = session.post(
        "https://www.rexelusa.com/graphql", headers=headers, data=json.dumps(data)
    )
    js = r.json()["data"]["locations"]["nodes"]

    for j in js:
        location_name = j.get("displayName")
        store_number = j.get("number")
        location_type = j.get("bannerCode")
        slug = j["urlInternal"]["slug"]
        page_url = f"https://www.rexelusa.com/locations/{slug}/{store_number}"
        try:
            phone = j["phone"]["nationalFormat"]
        except:
            phone = SgRecord.MISSING

        _tmp = []
        hours = j.get("hours") or []
        for h in hours:
            day = h.get("dayName")
            start = h.get("openTime")
            end = h.get("closeTime")
            if not start or not end:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start} - {end}")
        hours_of_operation = ";".join(_tmp)

        j = j["location"]
        a = j.get("address")
        street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
        city = a.get("city")
        state = a.get("countrySubdivisionCode")
        postal = a.get("postalCode")
        country_code = a.get("countryCode")

        c = j.get("coords") or {}
        latitude = c.get("lat")
        longitude = c.get("long")
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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.rexelusa.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
