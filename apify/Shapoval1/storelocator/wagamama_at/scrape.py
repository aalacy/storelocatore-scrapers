from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wagamama.com"
    api_url = "https://www.wagamama.com/_nuxt/static/1638873726/home/state.js"
    session = SgRequests()
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
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        slug = "".join(
            tree.xpath('//ul[contains(@class, "HeaderNavDesktop")]/li[2]//a/@href')
        )
        if slug.find(".us") != -1:
            continue
        page_url = f"{spage_url}{slug}"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        slug = tree.xpath(
            '//div[./a[contains(@href, "tel")]]/following::div[1]/a[1]/@href'
        )
        tmp = []
        tmp.append(page_url)
        for b in slug:

            page_url = f"{spage_url}{b}"

            tmp.append(page_url)
        for t in tmp:

            if t == "https://www.wagamama.at":
                t = "https://www.wagamama.at/restaurants/parndorf"
            if t == "https://www.wagamama.bh":
                t = "https://www.wagamama.bh/restaurants/bahrain-city-centre"
            if t == "https://www.wagamama.gi":
                t = "https://www.wagamama.gi/restaurants/gibraltar-ocean-village"
            if t == "https://www.wagamamanorway.no":
                t = "https://www.wagamamanorway.no/restaurants/oslo-airport"
            if t == "https://www.wagamama.om":
                t = "https://www.wagamama.om/restaurants/al-qurum-complex"
            if t == "https://www.wagamama.sk":
                t = "https://www.wagamama.sk/restauracie/bratislava"
            if t == "https://www.wagamama.se":
                t = "https://www.wagamama.se/restauranger/stockholm-waterfront"
            page_url = t
            if page_url.count("/") != 4:
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
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./a]/following::div[@class="VenueOverview__preview_1D9p"][2]/following-sibling::ul/li/span/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())
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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
