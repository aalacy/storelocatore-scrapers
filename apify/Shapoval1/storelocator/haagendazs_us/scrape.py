import httpx
import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):
    with SgRequests() as http:
        locator_domain = "https://haagendazs.us/"
        api_url = "https://www.icecream.com/us/en/brands/haagen-dazs/shops/all-shops"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//a[@class="cmp-button__btn"]')
        for d in div:
            slug = "".join(d.xpath(".//@href"))
            state = "".join(d.xpath(".//preceding::h3[1]/text()"))
            page_url = f"https://www.icecream.com{slug}"
            location_name = "".join(d.xpath("./span/text()"))

            r = http.get(url=page_url, headers=headers)
            assert isinstance(r, httpx.Response)
            assert 200 == r.status_code
            tree = html.fromstring(r.text)

            ad = (
                " ".join(tree.xpath('//p[@class="shop-info__address"]/text()'))
                .replace("\n", "")
                .strip()
            )
            adr = tree.xpath('//p[@class="shop-info__address"]/text()')
            ad = " ".join(ad.split())
            ph = re.findall(r"[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}", ad) or "<MISSING>"
            phone = "".join(ph) or "<MISSING>"
            if phone.count("(") > 1:
                phone = "(" + phone.split("(")[1].strip()
            ad = ad.replace(f"{phone}", "").strip()
            if len(adr) == 3:
                ad = "".join(adr[1]).replace("\r\n", " ").strip()
            if len(adr) < 3:
                ad = "".join(adr[-1]).replace("\r\n", " ").strip()
            a = parse_address(USA_Best_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            postal = a.postcode or "<MISSING>"
            country_code = "US"
            city = a.city or "<MISSING>"
            if city.find("Barrett Pkwy Space Ki11 Kennesaw") != -1:
                street_address = street_address + " " + "Barrett Pkwy Space Ki11"
                city = "Kennesaw"
            if city.find(",") != -1:
                city = city.split(",")[0].strip()
            try:
                latitude = (
                    "".join(tree.xpath('//a[text()="Get directions"]/@href'))
                    .split(",")[-2]
                    .split("=")[1]
                    .strip()
                )
                longitude = (
                    "".join(tree.xpath('//a[text()="Get directions"]/@href'))
                    .split(",")[-1]
                    .strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "0.0":
                latitude, longitude = "<MISSING>", "<MISSING>"
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[text()="Shop Hours"]/following-sibling::ul/li/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation.find("Temporarily Closed") != -1:
                hours_of_operation = "Temporarily Closed"

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
