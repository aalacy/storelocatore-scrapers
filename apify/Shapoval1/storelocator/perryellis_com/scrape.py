from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.perryellis.com/"
    api_url = "https://api.zenlocator.com/v1/apps/app_cqvdfh5t/locations/search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["locations"]
    for j in js:

        page_url = "https://www.perryellis.com/pages/store-locator"
        location_name = j.get("name")
        ad = j.get("visibleAddress") or "<MISSING>"
        if ad == "<MISSING>":
            ad = j.get("address")
        location_type = j.get("type") or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = j.get("region") or a.state or "<MISSING>"
        if state.find("/") != -1:
            state = state.split("/")[0].strip()
        postal = j.get("postcode") or a.postcode or "<MISSING>"
        country_code = j.get("countryCode")
        city = j.get("city") or a.city or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        try:
            phone = j.get("contacts").get("con_vakq85z8").get("text")
        except:
            phone = "<MISSING>"
        hours = j.get("hours")
        hours_of_operation = "<MISSING>"
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        if "hoursOfOperation" in hours:
            for d in days:
                day = str(d).capitalize()
                time = hours.get("hoursOfOperation").get(f"{d}")
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        r = session.get(
            "https://api.zenlocator.com/v1/apps/app_cqvdfh5t/init?widget=MAP",
            headers=headers,
        )
        js = r.json()["hours"]
        for j in js:
            hours_id = j.get("id")
            _tmp = []
            if hours_id == hours:
                for d in days:
                    day = str(d).capitalize()
                    time = j.get("hoursOfOperation").get(f"{d}")
                    line = f"{day} {time}"
                    _tmp.append(line)
                hours_of_operation = "; ".join(_tmp)

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
