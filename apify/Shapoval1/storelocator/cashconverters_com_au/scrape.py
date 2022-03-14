from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cashconverters.com.au/"
    api_url = "https://www.cashconverters.com.au/c3api/store/query"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["Value"]
    for j in js:
        slug = j.get("link")
        page_url = f"https://www.cashconverters.com.au{slug}"
        phone = j.get("phone")
        location_name = j.get("title")
        latitude = j.get("lat")
        longitude = j.get("lng")
        street_address = j.get("addressline1")
        ad = "".join(j.get("addressline2"))
        state = ad.split()[-2].strip()
        postal = ad.split()[-1].strip()
        country_code = "AU"
        city = " ".join(ad.split()[:-2])
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours = tree.xpath('//h2[text()="Buys and Loans:"]/following-sibling::*/text()')
        hours = list(filter(None, [a.strip() for a in hours]))
        tmp = []
        for h in hours:
            if "Jan" in h:
                continue
            tmp.append(h)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
