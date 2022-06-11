from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    if hours != "<MISSING>":
        for h in hours:
            day = h.get("weekDay")
            try:
                opens = h.get("openingTime").get("formattedHour")
            except:
                opens = "<MISSING>"
            try:
                closes = h.get("closingTime").get("formattedHour")
            except:
                closes = "<MISSING>"
            cls = h.get("closed")
            line = f"{day} {opens}-{closes}"
            if cls:
                line = f"{day} Closed"
            tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    if hours_of_operation == "<MISSING>":

        if hours != "<MISSING>":
            for h in hours:
                day = h.get("weekDay")
                try:
                    opens = h.get("openingTime").get("formattedHour")
                except:
                    opens = "<MISSING>"
                try:
                    closes = h.get("closingTime").get("formattedHour")
                except:
                    closes = "<MISSING>"
                cls = h.get("closed")
                line = f"{day} {opens}-{closes}"
                if cls:
                    line = f"{day} Closed"
                tmp.append(line)

    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    api_urls = [
        "https://www.thewhitecompany.com/uk/twccmsservice/components/LeftColumnStores?pageId=storeLocatorPage",
        "https://www.thewhitecompany.com/uk/twccmsservice/components/RightFirstStores?pageId=storeLocatorPage",
        "https://www.thewhitecompany.com/uk/twccmsservice/components/RightSecondStores?pageId=storeLocatorPage",
    ]
    for api_url in api_urls:

        r = session.get(api_url)
        try:
            js = r.json()["data"]["LeftColumnStores"]["components"]
        except:
            try:
                js = r.json()["data"]["RightFirstStores"]["components"]
            except:
                js = r.json()["data"]["RightSecondStores"]["components"]
        for j in js:
            locations = j.get("pointOfServiceList")
            for l in locations:
                slug = l.get("name")
                a = l.get("address")
                page_url = f"https://www.thewhitecompany.com/uk/our-stores/{slug}"
                location_name = l.get("displayName")
                street_address = f"{a.get('line1')} {a.get('line2')}".strip()
                state = "<MISSING>"
                postal = a.get("postalCode")
                country_code = a.get("country").get("isocode")
                if country_code == "US":
                    state = "".join(a.get("postalCode")).split()[0].strip()
                    postal = "".join(a.get("postalCode")).split()[1].strip()
                formattedAddress = a.get("formattedAddress")
                city = a.get("town")
                latitude = l.get("geoPoint").get("latitude")
                longitude = l.get("geoPoint").get("longitude")
                phone = a.get("phone") or "<MISSING>"
                try:
                    hours = (
                        l.get("openingHours").get("weekDayOpeningList") or "<MISSING>"
                    )
                except:
                    hours = "<MISSING>"
                if hours == "<MISSING>":
                    try:
                        hours = l.get("specialOpeningSchedule").get(
                            "weekDayOpeningList"
                        )
                    except:
                        hours = "<MISSING>"

                hours_of_operation = get_hours(hours)

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
                    raw_address=formattedAddress,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "thewhitecompany.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
