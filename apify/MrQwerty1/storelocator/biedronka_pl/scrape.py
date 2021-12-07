from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coordinates(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text.replace("!--", "").replace("--", ""))
    lat = "".join(tree.xpath("//div[@data-latitude]/@data-latitude"))
    lng = "".join(tree.xpath("//div[@data-longitude]/@data-longitude"))

    return lat, lng


def fetch_data(sgw: SgWriter):
    for i in range(1, 300):
        r = session.get(f"https://www.biedronka.pl/pl/sklepy/lista,,,page,{i}")
        tree = html.fromstring(r.text)

        divs = tree.xpath("//ul[@class='shopList']/li")
        for d in divs:
            location_name = "".join(d.xpath(".//h4/text()")).strip()
            city = location_name
            zs = d.xpath(".//span[@class='shopAddress']/text()")
            zs = list(filter(None, [s.strip() for s in zs]))
            if len(zs) == 1:
                zs.append(SgRecord.MISSING)
            postal, street_address = zs

            slug = str(html.tostring(d)).split('href="')[1].split('"')[0]
            store_number = slug.split("id,")[1].split(",title")[0]
            page_url = f"https://www.biedronka.pl{slug}"

            _tmp = []
            hours = d.xpath(".//span[contains(@class, 'hours')]")
            for h in hours:
                day = "".join(h.xpath("./preceding-sibling::text()[1]")).strip()
                inter = "".join(h.xpath("./text()")).strip()
                _tmp.append(f"{day} {inter}")
            hours_of_operation = ";".join(_tmp)

            try:
                latitude, longitude = get_coordinates(page_url)
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code="PL",
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        if len(divs) < 18:
            break


if __name__ == "__main__":
    locator_domain = "https://www.biedronka.pl/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
