import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_urls():

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    with SgRequests() as http:
        r = http.get(
            url="https://www.trevorlindenfitness.com/fitness-clubs/", headers=headers
        )
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        return tree.xpath('//a[text()="MORE INFO"]/@href')


def get_data(url, sgw: SgWriter):

    locator_domain = "https://www.trevorlindenfitness.com"
    page_url = url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    with SgRequests() as http:
        r = http.get(url=page_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)

        location_name = (
            " ".join(tree.xpath("//h1//text()[1]"))
            .replace("\n", "")
            .replace("  ", " ")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//p[@class="add"]/text()'))
            .replace("Delta", ",Delta")
            .replace(
                "1055 Canada Pl #50, Vancouver,", "1055 Canada Pl #50, Vancouver, BC"
            )
        )
        ad = ad.replace(", ,", ",").replace("BC,", "BC")

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        phone = (
            "".join(tree.xpath('//p[@class="phone"]//text()')).replace("\n", "").strip()
        )
        location_type = "Fitness club"
        hours_of_operation = " ".join(
            tree.xpath('//h3[text()="Club hours"]/following-sibling::div[1]//text()')
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Statutory Holidays") != -1:
            hours_of_operation = hours_of_operation.split("Statutory Holidays")[
                0
            ].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):

    urls = get_urls()
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
