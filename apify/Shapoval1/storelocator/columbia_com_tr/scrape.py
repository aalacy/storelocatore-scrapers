import httpx
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address

locator_domain = "https://www.columbia.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def fetch_data(sgw: SgWriter):

    api_url = "https://www.columbia.com.tr/api/inventory/store/all?countryId=0&cityId=0&storeType=10&isActive=true"
    with SgRequests() as http:
        try:
            r = SgRequests.raise_on_err(http.get(url=api_url))
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            js = r.json()["data"]
            for j in js:

                page_url = "https://www.columbia.com.tr/stores"
                location_name = j.get("name") or "<MISSING>"
                ad = "".join(j.get("address"))
                location_type = "Mağazalar"
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                if postal == "227.KM":
                    postal = "<MISSING>"
                country_code = "TR"
                city = a.city or "<MISSING>"
                latitude = j.get("latitude") or "<MISSING>"
                longitude = j.get("longtitude") or "<MISSING>"
                phone = j.get("phone") or "<MISSING>"
                hours_of_operation = j.get("workingHours") or "<MISSING>"

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
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)

        except Exception as e:
            log.info(f"Err at #L100: {e}")


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
