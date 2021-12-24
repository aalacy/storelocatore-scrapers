from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://nespresso.bg/"
    api_urls = [
        "https://www.nespresso.bg/en/stores?type=json&ver=1",
        "https://www.nespresso.hr/en/stores?type=json&ver=1",
        "https://www.nespresso.rs/en/stores?type=json&ver=1",
        "https://www.nespresso.si/en/stores?type=json&ver=1",
    ]
    for api_url in api_urls:
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        js = r.json()
        for j in js["stores"]:

            page_url = j.get("url") or api_url.split("?")[0].strip()
            location_name = j.get("name")
            street_address = j.get("street") or "<MISSING>"
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = j.get("countryName")
            city = "<MISSING>"
            latitude = "".join(j.get("coordinatesGoogleMap")).split(",")[0].strip()
            longitude = "".join(j.get("coordinatesGoogleMap")).split(",")[1].strip()
            phone = j.get("phone") or "<MISSING>"
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            h = eval(j.get("workingHoursObject"))
            tmp = []
            for d in days:
                day = d
                opens = h.get(f"{d}").get("from")
                closes = h.get(f"{d}").get("to")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp).replace("; sun  - ", "").strip() or "<MISSING>"
            )
            if city == "<MISSING>":
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                city = (
                    "".join(tree.xpath('//div[@class="item item-city"]/text()'))
                    .replace("- СОФИЯ", "СОФИЯ")
                    .replace("\n", "")
                    .strip()
                )
            if street_address == "<MISSING>":
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                street_address = (
                    "".join(tree.xpath('//div[@class="item item-name"]/text()'))
                    .replace("\n", "")
                    .strip()
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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
