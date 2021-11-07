import httpx
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumph-motorcycles.ca/"
    api_url = "https://www.triumph-motorcycles.ca/api/v2/places/alldealers?LanguageCode=en-CA&SiteLanguageCode=en-CA&Skip=0&Take=50&CurrentUrl=www.triumph-motorcycles.ca"

    with SgRequests() as http:
        r = http.get(url=api_url)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        js = r.json()["DealerCardData"]["DealerCards"]
        for j in js:
            slug = j.get("DealerUrl")
            page_url = f"https://www.triumph-motorcycles.ca{slug}"
            location_name = j.get("Title")
            ad = f"{j.get('AddressLine1')} {j.get('AddressLine2')} {j.get('AddressLine3')} {j.get('AddressLine4')}"
            ad = " ".join(ad.split())
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
            postal = j.get("PostCode") or "<MISSING>"
            latitude = j.get("Latitude") or "<MISSING>"
            longitude = j.get("Longitude") or "<MISSING>"
            phone = j.get("Phone") or "<MISSING>"
            hours_of_operation = (
                "".join(j.get("OpeningTimes")).replace("<br/>", " ").strip()
            )

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
                raw_address=f"{ad} {postal}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
