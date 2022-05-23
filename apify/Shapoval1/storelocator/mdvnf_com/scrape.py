from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mdvnf.com"
    api_url = "https://www.mdvnf.com/Locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//td[@class="top"]/a[1]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.mdvnf.com/{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//td[@class="top normal"]')
        for d in div:

            location_name = "".join(d.xpath(".//span/text()"))
            info = d.xpath(".//span/following-sibling::text()")
            info = list(filter(None, [a.strip() for a in info]))
            ad = "".join(info[-1]).replace(",,", ",").strip()
            ad = " ".join(ad.split())
            address_line = " ".join(info)
            street_address = " ".join(info[:-1]).strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()
            country_code = "US"
            city = ad.split(",")[0].strip()
            if city.find("/") != -1:
                city = city.split("/")[1].strip()
            try:
                store_number = location_name.split("-")[-1].strip()
            except:
                store_number = "<MISSING>"

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
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
                raw_address=address_line,
            )

            sgw.write_row(row)

    locator_domain = "https://www.mdvnf.com"
    page_url = "https://www.mdvnf.com/Locations.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//td[./a]")
    for d in div:

        location_name = "".join(d.xpath(".//a/text()"))
        info = d.xpath(".//a/following-sibling::text()")
        info = list(filter(None, [a.strip() for a in info]))
        ad = "".join(info[-1]).replace(",,", ",").strip()
        ad = " ".join(ad.split())
        address_line = " ".join(info)
        street_address = " ".join(info[:-1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        if city.find("/") != -1:
            city = city.split("/")[1].strip()
        location_type = "MDV locations"

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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=address_line,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
