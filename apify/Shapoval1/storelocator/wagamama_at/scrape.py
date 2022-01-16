from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wagamama.com"
    api_url = "https://www.wagamama.com/_nuxt/static/1641920796/state.js"
    session = SgRequests(verify_ssl=False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    div = r.text.split('url="')
    for d in div:
        try:
            spage_url = (
                d.split('url:"')[1]
                .replace("\\u002F\\u002F", "//")
                .split('"')[0]
                .strip()
            )
        except:
            spage_url = d.split('"')[0].replace("\\u002F\\u002F", "//").strip()
        if spage_url.find("wagamama") == -1:
            continue

        try:
            country_code = d.split('code="')[1].split('"')[0].strip()
        except:
            country_code = "<MISSING>"
        if spage_url == "https://www.wagamama.gr":
            spage_url = "https://www.wagamama.com.gr"
        if spage_url.find("us") != -1:
            continue
        sitemap_url = f"{spage_url}/sitemap.xml"

        r = session.get(sitemap_url, headers=headers)
        tree = html.fromstring(r.content)
        div = tree.xpath(
            '//url/loc[contains(text(), "restaurants/")] | //url/loc[contains(text(), "restauranter/")] | //url/loc[contains(text(), "ristoranti/")] | //url/loc[contains(text(), "restauracie/")] | //url/loc[contains(text(), "restauranger/")]'
        )
        for b in div:
            page_url = "".join(b.xpath(".//text()")).replace("https://", "https://www.")
            try:
                r = session.get(page_url, headers=headers)
                tree = html.fromstring(r.text)
            except:
                continue
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
            if country_code == "<MISSING>" and page_url.find("wagamamani") != -1:
                country_code = "NI"
            if ".ie/" in page_url:
                country_code = "IE"
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
