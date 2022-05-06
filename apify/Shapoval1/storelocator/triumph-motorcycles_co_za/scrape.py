from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumph-motorcycles.co.za/"
    api_url = "https://www.triumph-motorcycles.co.za/api/v2/places/alldealers?LanguageCode=en-ZA&SiteLanguageCode=en-ZA&Skip=0&Take=50&CurrentUrl=www.triumph-motorcycles.co.za"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["DealerCardData"]["DealerCards"]
    for j in js:

        location_name = j.get("Title")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        ad = f"{j.get('AddressLine1')} {j.get('AddressLine1') or ''}".replace(
            "None", ""
        ).strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = j.get("PostCode") or "<MISSING>"
        country_code = "ZA"
        city = j.get("city") or "<MISSING>"
        slug = j.get("DealerUrl")
        page_url = f"https://www.triumph-motorcycles.co.za{slug}"
        phone = j.get("Phone") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath('//ul[@class="dealer-location__opening-times"]/li//text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
