from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://teegschwendner.de/"
    api_url = "https://uberall.com/api/storefinders/MGg7yqu7WSC5TBl7uC0353TJeDnGgo/locations/all?v=20211005&language=de&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["response"]["locations"]
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("streetAndNumber")
        state = j.get("province") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        r = session.get(
            f"https://uberall.com/api/storefinders/MGg7yqu7WSC5TBl7uC0353TJeDnGgo/locations/{store_number}?v=20211005&language=de&fieldMask=businessId&fieldMask=callToActions&fieldMask=city&fieldMask=country&fieldMask=descriptionLong&fieldMask=descriptionShort&fieldMask=distance&fieldMask=email&fieldMask=fax&fieldMask=googlePlaceId&fieldMask=id&fieldMask=identifier&fieldMask=keywords&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=openingHours&fieldMask=openingHoursNotes&fieldMask=phone&fieldMask=photos&fieldMask=province&fieldMask=socialPost&fieldMask=specialOpeningHours&fieldMask=streetAndNumber&fieldMask=timezone&fieldMask=zip&fieldMask=customItems&fieldMask=events&fieldMask=menus&fieldMask=paymentOptions&fieldMask=people&fieldMask=products&fieldMask=averageRating&fieldMask=reviewCount&fieldMask=reviews&fieldMask=socialProfiles&fieldMask=website"
        )
        js = r.json()["response"]
        phone = js.get("phone")
        hours = js.get("openingHours")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            for h in hours:
                day = (
                    str(h.get("dayOfWeek"))
                    .replace("1", "Monday")
                    .replace("2", "Tuesday")
                    .replace("3", "Wednesday")
                    .replace("4", "Thursday")
                    .replace("5", "Friday")
                    .replace("6", "Saturday")
                    .replace("7", "Sunday")
                )
                opens = h.get("from1")
                closes = h.get("to1")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp).replace("None - None", "Closed").strip()
        city_slug = str(city).replace(" ", "-").lower()
        street_address_slug = str(street_address).replace(" ", "-").lower()
        page_url = f"https://www.teegschwendner.de/Fachgeschaefte/#!/l/{city_slug}/{street_address_slug}/{store_number}"

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
