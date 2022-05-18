from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.noodlecanteen.co.nz/"
    api_url = "http://www.noodlecanteen.co.nz/locations-list/"
    api_urls = [api_url]
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="pager"]/li[@class="pager-next last"]/a')
    for d in div:
        last_page_num = "".join(d.xpath(".//@href"))
        last_page = f"http://www.noodlecanteen.co.nz/locations-list/{last_page_num}/"
        api_urls.append(last_page)
        for apis in api_urls:
            r = session.get(apis)
            tree = html.fromstring(r.text)
            div = tree.xpath(
                '//table//tr[.//td[@class="views-field views-field-phone"]]'
            )
            for d in div:

                slug = "".join(d.xpath("./td[4]//a/@id")).replace("\n", "").strip()
                page_url = f"http://www.noodlecanteen.co.nz/store-location/?{slug}"
                street_address = (
                    "".join(d.xpath("./td[2]/text()")).replace("\n", "").strip()
                )
                city = "".join(d.xpath("./td[1]/text()")).replace("\n", "").strip()
                phone = "".join(d.xpath("./td[3]/text()")).replace("\n", "").strip()
                hours_of_operation = (
                    "".join(
                        d.xpath(
                            './/preceding::p[contains(text(), "All stores open:")][1]/text()'
                        )
                    )
                    .replace("All stores open:", "")
                    .strip()
                )
                country_code = "New Zealand"
                state = "".join(d.xpath(".//preceding::h2[1]//text()")).strip()
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
                map_link = (
                    "".join(
                        tree.xpath(
                            "//script[contains(text(), 'case \"Riccarton\"')]/text()"
                        )
                    )
                    .split(f'case "{slug}"')[1]
                    .split('"src","')[1]
                    .split('");')[0]
                    .strip()
                )
                try:
                    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=SgRecord.MISSING,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=SgRecord.MISSING,
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
