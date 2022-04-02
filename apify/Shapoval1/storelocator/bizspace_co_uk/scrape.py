from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bizspace.co.uk/"
    api_url = "https://www.bizspace.co.uk/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[@data-mapid]")

    for d in div:
        slug = "".join(d.xpath("./a/@href"))
        state_slg = "".join(
            tree.xpath(f'//a[contains(@href, "{slug}")]/h4/text()')
        ).lower()
        if state_slg == "wales & the south west":
            state_slg = "wales%20%26%20the%20south%20west"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "content-type": "application/x-www-form-urlencoded",
            "Origin": "https://www.bizspace.co.uk",
            "Connection": "keep-alive",
            "Referer": "https://www.bizspace.co.uk/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }

        params = {
            "x-algolia-agent": "Algolia for JavaScript (3.34.0); Browser",
            "x-algolia-application-id": "G76STO80LV",
            "x-algolia-api-key": "3afbdea905479d7d5dd6d53c8d1bc0ef",
        }

        data = (
            '{"params":"query=&aroundLatLngViaIP=true&getRankingInfo=1&filters=Region%3A%22'
            + state_slg
            + '%22"}'
        )

        r = session.post(
            "https://g76sto80lv-dsn.algolia.net/1/indexes/property/query",
            headers=headers,
            params=params,
            data=data,
        )
        js = r.json()["hits"]
        for j in js:

            location_name = j.get("Name") or "<MISSING>"
            a = j.get("Address")
            street_address = (
                f"{a.get('AddressLine1')} {a.get('AddressLine2')}".replace(
                    "None", ""
                ).strip()
                or "<MISSING>"
            )
            street_address = " ".join(street_address.split())
            state = j.get("Region") or "<MISSING>"
            postal = a.get("Postcode") or "<MISSING>"
            country_code = "UK"
            city = j.get("Town") or "<MISSING>"
            store_number = a.get("Id") or "<MISSING>"
            latitude = a.get("Latitude") or "<MISSING>"
            longitude = a.get("Longitude") or "<MISSING>"
            phone = "<MISSING>"
            location_type = ",".join(j.get("PropertyTypes"))
            hours_of_operation = "<MISSING>"
            hours = j.get("OpeningHours")
            tmp = []
            if hours:
                for h in hours:
                    day = h.get("DayOfWeek")
                    opens = h.get("OpeningTime")
                    closes = h.get("ClosingTime")
                    line = (
                        f"{day} {opens} - {closes}".replace(":00:00", ":00")
                        .replace(":30:00", ":30")
                        .strip()
                    )
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
            slug_page = j.get("TitleUrl")
            page_url = f"https://www.bizspace.co.uk/spaces/{slug_page}"

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
                location_type=location_type,
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
