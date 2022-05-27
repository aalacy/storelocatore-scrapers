from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.anthonyvincenailspa.co"
    states = [
        "AK",
        "AL",
        "AR",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "x-wix-brand": "wix",
        "authorization": "wixcode-pub.2d39b62408ccb1d7a597175889997e88bcbbbdd9.eyJpbnN0YW5jZUlkIjoiMmM5YjYzNjAtZTI0NS00ZWFkLWFiNDktYWVkMGFkYzUwMDdmIiwiaHRtbFNpdGVJZCI6IjU5MzY0NTFkLWIyYzktNDVmNC1hYjYxLTYzOThhYjk4YzUxNCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTY0NjkyMzk0MDg0MywiYWlkIjoiODM3MzdlMjItZTI5MS00ZTg0LTkxNTctYjgyN2FlOWU0ZGZkIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjY5ODJlYjZiLWQyM2YtNDUyMi05YTY1LWU3YTU2ZDU4NzJhNCIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsSGFzRUNvbW1lcmNlLFNob3dXaXhXaGlsZUxvYWRpbmcsSGFzRG9tYWluIiwidGVuYW50IjpudWxsLCJzaXRlT3duZXJJZCI6IjY3OGVkMTcxLTA1NDktNDM3OS1hNzBlLWI0ZTdjMWQ5ZTNjOCIsImluc3RhbmNlVHlwZSI6InB1YiIsInNpdGVNZW1iZXJJZCI6bnVsbH0=",
        "X-Wix-Client-Artifact-Id": "wix-thunderbolt",
        "commonConfig": "%7B%22brand%22%3A%22wix%22%2C%22BSI%22%3A%22d622e595-93f1-451d-aee5-b9d4e5377c0e%7C4%22%7D",
        "Origin": "https://www.anthonyvincenailspa.com",
        "Connection": "keep-alive",
        "Referer": "https://www.anthonyvincenailspa.com/_partials/wix-thunderbolt/dist/clientWorker.72ed8094.bundle.min.js",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    for s in states:
        json_data = {
            "collectionName": "Location",
            "dataQuery": {
                "filter": {
                    "state": {
                        "$contains": f"{s}",
                    },
                },
                "sort": [],
                "paging": {
                    "offset": 0,
                    "limit": 100,
                },
            },
            "options": {},
            "include": None,
            "segment": "LIVE",
            "appId": "4b69d454-3710-4f4b-bdad-751fdf5bd58c",
        }

        r = session.post(
            "https://www.anthonyvincenailspa.com/_api/cloud-data/v1/wix-data/collections/query",
            headers=headers,
            json=json_data,
        )
        js = r.json()
        for j in js["items"]:
            a = j.get("address")

            page_url = "https://www.anthonyvincenailspa.com/locations"
            location_name = j.get("f") or "<MISSING>"
            street_address = "".join(a.get("formatted")) or "<MISSING>"
            if street_address.find(",") != -1:
                street_address = street_address.split(",")[0].strip()
            state = j.get("state") or "<MISSING>"
            postal = j.get("zipcode") or "<MISSING>"
            country_code = "US"
            city = j.get("city") or "<MISSING>"
            try:
                latitude = j.get("address").get("location").get("latitude")
                longitude = j.get("address").get("location").get("longitude")
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = j.get("phoneNumber")
            if phone == "TBA" or phone == "TBD":
                phone = "<MISSING>"
            hours_of_operation = (
                "".join(j.get("operatingHours"))
                .replace("\n", " ")
                .replace("EVERYDAY", "")
                .replace("TEMPORARY HOURS", "")
                .strip()
            )
            if hours_of_operation.find("COMING ") != -1:
                hours_of_operation = "Coming Soon"
            if hours_of_operation.find("**") != -1:
                hours_of_operation = hours_of_operation.split("**")[0].strip()

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
                raw_address=f"{street_address} {city}, {state} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
