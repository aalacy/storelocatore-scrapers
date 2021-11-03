from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.fivestarseniorliving.com"
    api_url = "https://www.fivestarseniorliving.com/sitemap.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url.count("/") != 6 or page_url.find("communities") == -1:
            continue

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        jsblock = "".join(
            tree.xpath('//script[contains(text(), "addressLocality")]/text()')
        )
        js = json.loads(jsblock)
        for j in js["@graph"]:

            location_name = j.get("name")

            try:
                street_address = j.get("address").get("streetAddress")
            except:
                street_address = js["@graph"][4].get("address").get("streetAddress")
            try:
                state = j.get("address").get("addressRegion")
            except:
                state = js["@graph"][4].get("address").get("addressRegion")
            try:
                postal = j.get("address").get("postalCode")
            except:
                postal = js["@graph"][4].get("address").get("postalCode")
            try:
                country_code = j.get("address").get("addressCountry")
            except:
                country_code = js["@graph"][4].get("address").get("addressCountry")
            try:
                city = j.get("address").get("addressLocality")
            except:
                city = js["@graph"][4].get("address").get("addressLocality")
            slug = page_url.replace("https://www.fivestarseniorliving.com", "").strip()
            session = SgRequests()
            r = session.get(
                "https://www.googletagmanager.com/gtm.js?id=GTM-MFVKXDD",
                headers=headers,
            )
            text = r.text.replace("\\", "").strip()
            try:
                phone = (
                    text.split(f"{slug}")[1]
                    .split("]")[0]
                    .replace('","value","', "")
                    .replace('"', "")
                    .strip()
                )
            except:
                phone = "<MISSING>"

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
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                hours_of_operation=SgRecord.MISSING,
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
