import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[./p[contains(text(), '☎')]]|//div[./h3/strong]")

    js = tree.xpath("//div[@data-block-json]/@data-block-json")
    js_list = []
    for j in js:
        try:
            j = json.loads(j)["location"]
        except:
            continue
        js_list.append(j)

    for d, j in zip(divs, js_list):
        try:
            location_name = d.xpath(".//h3//text()")[0].strip()
            street_address = "".join(
                d.xpath(".//h3/following-sibling::p[1]/text()")
            ).strip()
        except:
            location_name = d.xpath(".//p/strong/text()")[0].strip()
            street_address = d.xpath(".//p[./strong]/text()")[0].strip()

        line = j.get("addressLine2").replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        phone = (
            "".join(d.xpath(".//*[contains(text(), '☎')]//text()"))
            .replace("☎", "")
            .strip()
        )
        if "jason" in phone:
            phone = phone.split("jason")[0].strip()
        if " - " in phone:
            phone = phone.split(" - ")[0].strip()
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")
        hours_of_operation = " ".join(
            ";".join(
                d.xpath(
                    ".//p[./strong[contains(text(), 'Hours')]]/following-sibling::p/text()"
                )
            ).split()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.playtri.com/"
    page_url = "https://www.playtri.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
