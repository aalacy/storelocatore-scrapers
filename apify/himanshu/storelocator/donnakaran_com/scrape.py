from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.donnakaran.com/store-locator/all-stores.do"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//form[@id="countryStoreFilter"]/select/option')
    for d in div:
        country_code = "".join(d.xpath(".//@value"))

        session = SgRequests()
        r = session.get(
            f"https://www.donnakaran.com/store-locator/all-stores.do?countryCode={country_code}",
            headers=headers,
        )
        tree = html.fromstring(r.text)
        block = tree.xpath('//div[@class="ml-storelocator-store-address"]')
        for b in block:
            slug = "".join(
                b.xpath('.//div[@class="eslStore ml-storelocator-headertext"]/a/@href')
            )
            page_url = f"https://www.donnakaran.com{slug}"

            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            location_name = "".join(tree.xpath('//div[@class="eslStore"]/text()'))
            adr1 = (
                "".join(tree.xpath('//div[@class="eslAddress1"]/text()'))
                .replace("Address 1", "")
                .strip()
            )
            adr2 = (
                "".join(tree.xpath('//div[@class="eslAddress2"]/text()'))
                .replace("Address 2", "")
                .strip()
            )
            street_address = adr1 + " " + adr2
            state = (
                "".join(tree.xpath('//span[@class="eslStateCode"]/text()'))
                or "<MISSING>"
            )
            postal = (
                "".join(tree.xpath('//span[@class="eslPostalCode"]/text()'))
                or "<MISSING>"
            )
            city = (
                "".join(tree.xpath('//span[@class="eslCity"]/text()'))
                .replace(",", "")
                .strip()
                or "<MISSING>"
            )
            try:
                latitude = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "storeLocatorDetailPageReady")]/text()'
                        )
                    )
                    .split('"latitude":')[1]
                    .split(",")[0]
                    .strip()
                )
                longitude = (
                    "".join(
                        tree.xpath(
                            '//script[contains(text(), "storeLocatorDetailPageReady")]/text()'
                        )
                    )
                    .split('"longitude":')[1]
                    .split("}")[0]
                    .strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                "".join(tree.xpath('//div[@class="eslPhone"]/text()')) or "<MISSING>"
            )
            hours_of_operation = (
                " ".join(
                    tree.xpath('//span[@class="ml-storelocator-hours-details"]/text()')
                )
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
            tmpcls = "".join(tree.xpath('//span[@style="color:#FF0000"]/text()'))
            if tmpcls.find("Temporarily closed") != -1:
                hours_of_operation = "Temporarily closed"

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
    locator_domain = "https://www.donnakaran.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
