import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.thewhitecompany.com"
    api_url = "https://www.thewhitecompany.com/uk/sitemap_Store-en_GB-GBP-7842621379062607619.xml"
    session = SgRequests()
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        slug = page_url.split("/")[-1].strip()

        session = SgRequests()
        r = session.get(
            f"https://www.thewhitecompany.com/uk/store-locator-endpoint/storesData/{slug}",
            headers=headers,
        )
        js = r.json()["data"]["shop"]

        a = js.get("address")
        location_name = js.get("displayName")
        ad = f"{a.get('line1')} {a.get('line2')} {a.get('town')} {a.get('postalCode')}"

        street_address = f"{a.get('line1')} {a.get('line2')}".strip()
        state = "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("country").get("isocode") or "<MISSING>"
        city = a.get("town") or "<MISSING>"
        if country_code == "US":
            b = usaddress.tag(ad, tag_mapping=tag)[0]
            city = a.get("line2")
            state = b.get("state")
            postal = b.get("postal")
            street_address = f"{b.get('address1')} {b.get('address2')}".replace(
                "None", ""
            ).strip()
        latitude = js.get("geoPoint").get("latitude") or "<MISSING>"
        longitude = js.get("geoPoint").get("longitude") or "<MISSING>"
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        try:
            hours = js.get("openingHours").get("weekDayOpeningList") or "<MISSING>"
        except:
            hours = "<MISSING>"

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
            try:
                hours = js.get("specialOpeningSchedule").get("weekDayOpeningList")
            except:
                hours = "<MISSING>"
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

        if location_name.find("PERMANENTLY CLOSED") != -1:
            hours_of_operation = "PERMANENTLY CLOSED"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.thewhitecompany.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
