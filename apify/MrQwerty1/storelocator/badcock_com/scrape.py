from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    apis = [
        "https://www.badcock.com/allshops",
        "https://www.badcock.com/StoreLocator/GetRemainingShops",
    ]

    for api in apis:
        r = session.get(api, headers=headers)
        tree = html.fromstring(r.text)
        li = tree.xpath("//li[@data-shopid]")

        for l in li:
            location_name = "".join(l.xpath(".//a[@class='shop-link']/text()")).strip()
            store_number = location_name.split("(")[1].replace(")", "").strip()
            if "coming" in location_name:
                continue
            page_url = "https://www.badcock.com" + "".join(
                l.xpath(".//a[@class='shop-link']/@href")
            )
            line = l.xpath(".//div[@class='short-description']/p[not(./strong)]/text()")
            line = list(filter(None, [l.strip() for l in line]))
            street_address = line[0]
            line = line[1]
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[1]
            country_code = "US"
            phone = "".join(l.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            latitude = "".join(
                l.xpath(".//input[@class='shop-coordinates']/@data-latitude")
            )
            longitude = "".join(
                l.xpath(".//input[@class='shop-coordinates']/@data-longitude")
            )

            _tmp = []
            hours = l.xpath(
                ".//p[./strong and  ./strong[not(contains(text(),'Phone'))] and ./strong[not(contains(text(),'Fax'))]]"
            )
            for h in hours:
                day = "".join(h.xpath("./strong/text()")).strip()
                time = "".join(h.xpath("./text()")).strip()

                _tmp.append(f"{day} {time}")

            hours_of_operation = "; ".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.badcock.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
