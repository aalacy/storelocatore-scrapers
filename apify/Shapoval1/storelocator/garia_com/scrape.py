from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.garia.com"
    api_url = "https://www.garia.com/api/v1/DealerContinent.json?DealerTypeID=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["items"]
    for j in js:
        id_s = j.get("ID")
        api_url_1 = f"https://www.garia.com/api/v1/DealerCountry.json?DealerContinentID={id_s}&DealerTypeID=1&relationdepth=0&sort=Name"
        r = session.get(api_url_1, headers=headers)
        js = r.json()["items"]
        for j in js:
            id_s_1 = j.get("ID")
            api_url_2 = f"https://www.garia.com/api/v1/Dealer.json?DealerCountryID={id_s_1}&DealerTypeID=1"
            r = session.get(api_url_2, headers=headers)
            js = r.json()["items"]
            for j in js:

                page_url = "https://www.garia.com/find-dealer/"
                ad = f"{j.get('Address')} {j.get('City')} {j.get('State')}".replace(
                    "None", ""
                ).strip()
                location_name = str(j.get("Name")).replace("&amp;", "&").strip()
                country_code = j.get("Country")
                a = parse_address(International_Parser(), ad)
                street_address = j.get("Address")
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                city = a.city or "<MISSING>"
                latitude = j.get("Latitude") or "<MISSING>"
                longitude = j.get("Longitude") or "<MISSING>"
                phone = str(j.get("PhoneNumber")).replace("Luke Roberts", "").strip()
                if phone.find("Sales:") != -1:
                    phone = phone.split("-")[0].replace("Sales:", "").strip()
                if phone.find("/") != -1:
                    phone = phone.split("/")[0].strip()
                hours_of_operation = "<MISSING>"

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
                    raw_address=f"{street_address} {ad}",
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
