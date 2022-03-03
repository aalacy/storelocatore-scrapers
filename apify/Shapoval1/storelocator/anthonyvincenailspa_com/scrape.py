from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.anthonyvincenailspa.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    }

    r = session.get("https://www.anthonyvincenailspa.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//text[@font-family="BaskervilleDisplayPT-Regular,Baskerville Display PT"]'
    )

    for d in div:
        state = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        state = " ".join(state.split())

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-XSRF-TOKEN": "1635520207|sdWOI2fCIGJJ",
            "commonConfig": '{"brand":"wix","bsi":"85a1a8f4-f269-49eb-bcbe-77ed48d1c281|3","consentPolicy":{"essential":true,"functional":true,"analytics":true,"advertising":true,"dataToThirdParty":true},"consentPolicyHeader":{}}',
            "x-wix-site-revision": "2572",
            "Content-Type": "application/json",
            "Origin": "https://www.anthonyvincenailspa.com",
            "Connection": "keep-alive",
            "Referer": "https://www.anthonyvincenailspa.com/_partials/wix-thunderbolt/dist/clientWorker.f3a09d43.bundle.min.js",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }

        data = (
            '["Location",{"state":{"$contains":"'
            + state
            + '"}},[],0,100,null,null,null]'
        )

        r = session.post(
            "https://www.anthonyvincenailspa.com/_api/wix-code-public-dispatcher/siteview/wix/data-web.jsw/find.ajax?gridAppId=4b69d454-3710-4f4b-bdad-751fdf5bd58c&instance=wixcode-pub.35f207bd3ef0f582f6c8f35bed1d2a79aa6102f3.eyJpbnN0YW5jZUlkIjoiMmM5YjYzNjAtZTI0NS00ZWFkLWFiNDktYWVkMGFkYzUwMDdmIiwiaHRtbFNpdGVJZCI6IjU5MzY0NTFkLWIyYzktNDVmNC1hYjYxLTYzOThhYjk4YzUxNCIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTYzNTUyMDIyMzcwNCwiYWlkIjoiMmRiMDk3Y2QtYzg3YS00ZDBmLWFiNmMtZWQ1ZTBmNTVkNjkyIiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6IjY5ODJlYjZiLWQyM2YtNDUyMi05YTY1LWU3YTU2ZDU4NzJhNCIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsU2hvd1dpeFdoaWxlTG9hZGluZyxIYXNFQ29tbWVyY2UsSGFzRG9tYWluIiwidGVuYW50IjpudWxsLCJzaXRlT3duZXJJZCI6IjY3OGVkMTcxLTA1NDktNDM3OS1hNzBlLWI0ZTdjMWQ5ZTNjOCIsImluc3RhbmNlVHlwZSI6InB1YiIsInNpdGVNZW1iZXJJZCI6bnVsbH0=&viewMode=site",
            headers=headers,
            data=data,
        )
        js = r.json()
        for j in js["result"]["items"]:

            page_url = "https://www.anthonyvincenailspa.com/locations"
            location_name = j.get("f")
            street_address = "".join(j.get("address").get("formatted"))
            if street_address.find(",") != -1:
                street_address = street_address.split(",")[0].strip()
            phone = j.get("phoneNumber") or "<MISSING>"
            if phone == "TBA" or phone == "TBD":
                phone = "<MISSING>"
            postal = j.get("zipcode")
            country_code = "US"
            city = j.get("city")
            try:
                latitude = j.get("address").get("location").get("latitude")
                longitude = j.get("address").get("location").get("longitude")
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
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
