from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.phs.org/"
    api_url = "https://www.phs.org/locations/Pages/hospitals.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="clearfix locRegion"]/ul/li/strong/a')
    for d in div:
        location_type = "hospitals"
        slug = "".join(d.xpath(".//@href")).split("/")[1].strip()
        location_name = "".join(d.xpath(".//text()"))
        page_url = f"https://{slug}.phs.org/Pages/default.aspx"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        street_address = (
            "".join(tree.xpath('//div[@class="pageIntro__address"]/span/text()[1]'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        ad = (
            "".join(tree.xpath('//div[@class="pageIntro__address"]/span/text()[2]'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "const dCenter")]/text()'))
            .split("lat:")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "const dCenter")]/text()'))
            .split("lng:")[1]
            .split("}")[0]
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(tree.xpath('//div[@class="pageIntro__phone"]//a/text()'))
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)

    locator_domain = "https://www.phs.org/"
    api_url = "https://www.phs.org/Style%20Library/jsondata/clinic-locations-data.js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["services"]:

        slug = j.get("detailsLink")
        loc_id = j.get("locationId")
        page_url = f"https://www.phs.org{slug}"
        location_name = j.get("name")
        location_type = j.get("service")
        country_code = "US"
        store_number = j.get("id")
        phone = j.get("phone") or "<MISSING>"
        if str(phone).find("or") != -1:
            phone = str(phone).split("or")[0].strip()
        hours_of_operation = j.get("hoursString")
        if hours_of_operation == "Please call for an appointment":
            hours_of_operation = "<MISSING>"
        city = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        street_address = "<MISSING>"
        ad = "<MISSING>"
        for j in js["locations"]:
            locs_id = j.get("_id")
            if locs_id == loc_id:
                street_address = j.get("address1")
                ad = "".join(j.get("address2"))
                city = ad.split(",")[0].strip()
                state = ad.split(",")[1].split()[0].strip()
                postal = ad.split(",")[1].split()[1].strip()
                latitude = j.get("latitude")
                longitude = j.get("longitude")

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
