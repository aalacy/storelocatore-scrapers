from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wagamama.com/"
    api_url = "https://www.wagamama.com/restaurants/search"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="SelectLocaleDropdown-content"]/a')
    for d in div:
        country_code = "".join(d.xpath("./@data-country"))
        sub_page_url = "".join(d.xpath(".//@href"))
        sitemap_url = f"{sub_page_url}sitemap.xml"
        if country_code == "northern ireland":
            sitemap_url = "https://www.wagamamani.com/sitemap.xml"
        if (
            sitemap_url.find("us") != -1
            or sitemap_url == "https://www.wagamama.com/"
            or sitemap_url == "https://www.wagamama.fr/sitemap.xml"
            or sitemap_url == "https://www.wagamama.es/sitemap.xml"
        ):
            continue
        try:
            r = session.get(sitemap_url, headers=headers)
            tree = html.fromstring(r.content)
        except:
            continue
        div = tree.xpath(
            '//url/loc[contains(text(), "restaurants/")] | //url/loc[contains(text(), "restauranter/")] | //url/loc[contains(text(), "ristoranti/")] | //url/loc[contains(text(), "restauracie/")] | //url/loc[contains(text(), "restauranger/")]'
        )
        for b in div:
            page_url = "".join(b.xpath(".//text()")).replace("https://", "https://www.")
            if (
                page_url.find("/en/") != -1
                or page_url.find("/fr/") != -1
                or page_url.find("/de_nl/") != -1
                or page_url.find("/ar/") != -1
            ):
                continue
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
            ad = " ".join(tree.xpath("//p[./a]/text()[1]")).replace("\n", "").strip()
            if ad.find("you can order") != -1:
                ad = ad.split("you can order")[0].strip()
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            city = a.city or "<MISSING>"

            phone = (
                "".join(tree.xpath("//p[./a]/a[1]/text()")).replace("\n", "").strip()
            )
            if phone.count("+") == 2:
                phone = "+" + phone.split("+")[1].strip()
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            hours = tree.xpath('//ul[contains(@class, "hours")]/li/span/text()')

            hours = list(filter(None, [a.strip() for a in hours]))
            try:
                hours_of_operation = " ".join(hours[:14])
            except:
                hours_of_operation = "<MISSING>"
            if hours_of_operation.count("- - ") == 7:
                hours_of_operation = "Closed"

            text = "".join(tree.xpath('//a[contains(@href,"maps")]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if latitude == "<MISSING>":
                text = "".join(tree.xpath('//img[contains(@src, "maps")]/@src'))
                try:
                    latitude = text.split("center=")[1].split(",")[0].strip()
                    longitude = (
                        text.split("center=")[1].split(",")[1].split("&")[0].strip()
                    )
                except:
                    latitude, longitude = "<MISSING>", "<MISSING>"
            if country_code == "northern ireland":
                country_code = "United Kingdom"

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
