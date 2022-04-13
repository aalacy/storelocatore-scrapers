import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://goforward.com/"
    api_url = "https://goforward.com/p/home"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//script[contains(text(), "clinic")]/text()'))
    js = json.loads(div)
    sub_js = json.loads(div)["props"]["pageProps"]["initialState"]["contentful"][
        "pages"
    ].values()

    for j in js["props"]["pageProps"]["initialState"]["clinics"]["clinics"].values():

        location_name = j.get("name")
        location_type = "<MISSING>"
        a = j.get("address")
        ad = " ".join(a.get("lines"))
        street_address = (
            ad.replace("Westfield UTC,", "")
            .replace("Bellevue Square Mall", "")
            .replace("Brickell City Centre", "")
            .replace("Cherry Creek North", "")
            .strip()
        )
        street_address = (
            street_address.replace("Buckhead Village District", "")
            .replace("Prudential Center Retail", "")
            .replace("Walt Whitman Shops", "")
            .strip()
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("postCode") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if str(city).find(",") != -1:
            city = str(city).split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"
        for c in sub_js:
            ids = c.get("id")
            if location_name == ids:
                location_name = c.get("title")
                slug = c.get("path")
                page_url = f"https://goforward.com{slug}"
                location_type = c.get("contentType")
                store_number = c.get("clinicId")

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
            raw_address=f"{ad} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
