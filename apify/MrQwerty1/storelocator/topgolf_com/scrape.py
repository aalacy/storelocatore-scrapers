from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    hours = tree.xpath(
        "//div[contains(text(), 'Hours')]/following-sibling::div/div[1]//span/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = ";".join(hours)

    return hoo


def fetch_data(sgw: SgWriter):
    for i in range(1, 500):
        api = f"https://topgolf.com/api/locations/list?lookup=true&page={i}&limit=20"
        r = session.get(api, headers=headers)
        js = r.json()["data"]

        for j in js:
            location_name = j.get("name")
            slug = j.get("alias")
            page_url = f"https://topgolf.com/us/{slug}/"
            street_address = j.get("address")
            city = j.get("city")
            state = j.get("state")
            postal = j.get("post_code")
            country = j.get("country")

            phone = j.get("phone")
            hours_of_operation = ""
            if phone == "TBA":
                hours_of_operation = "Coming Soon"
                phone = SgRecord.MISSING

            latitude = j.get("latitude")
            longitude = j.get("longitude")
            store_number = j.get("site_id")

            if not hours_of_operation:
                hours_of_operation = get_hoo(page_url)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(js) < 20:
            break


if __name__ == "__main__":
    locator_domain = "https://topgolf.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
