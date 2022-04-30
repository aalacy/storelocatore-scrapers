from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://docbsrestaurant.com/"
    api_url = "https://docbsrestaurant.com/locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3/following-sibling::div[./a][1]/a")
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        slug_js = slug.split("/")[-1].strip()
        page_url = f"https://docbsrestaurant.com{slug}"
        r = session.get(
            f"https://docbsrestaurant.com/_next/data/zc-i6VAPi5HXka6E6gACu/en-US/locations/{slug_js}.json"
        )
        js = r.json()["pageProps"]["location"]

        location_name = js.get("name") or "<MISSING>"
        street_address = (
            f"{js.get('address')} {js.get('address2') or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        state = js.get("state") or "<MISSING>"
        postal = js.get("zip") or "<MISSING>"
        country_code = "US"
        city = js.get("city") or "<MISSING>"
        store_number = js.get("id") or "<MISSING>"
        latitude = js.get("latitude") or "<MISSING>"
        longitude = js.get("longitude") or "<MISSING>"
        phone = js.get("phone") or "<MISSING>"
        hours = js.get("hours")[0].get("hours")
        tmp = []
        hours_of_operation = "<MISSING>"
        if hours:
            for h in hours:
                day = h.get("days")
                times = h.get("times")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
