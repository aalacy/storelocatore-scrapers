from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.riotinto.com"
    api_urls = [
        "https://www.riotinto.com/operations/australia",
        "https://www.riotinto.com/operations/canada",
        "https://www.riotinto.com/operations/iceland",
        "https://www.riotinto.com/operations/madagascar",
        "https://www.riotinto.com/operations/mongolia",
        "https://www.riotinto.com/operations/new-zealand",
        "https://www.riotinto.com/operations/south-africa",
        "https://www.riotinto.com/operations/us",
    ]
    for api_url in api_urls:
        slug = api_url.split(".com")[1].strip()
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath(
            f'//div[@class="component-content"]//a[contains(@href, "{slug}")]'
        )
        for d in div:

            slug = "".join(d.xpath(".//@href"))
            page_url = f"https://www.riotinto.com{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            div = (
                tree.xpath(
                    '//div[@class="component-content"]/div[1]/div[@class="rt-content-card rt-content-card--contact"][1]'
                )
                or "<MISSING>"
            )
            if div == "<MISSING>":
                div = tree.xpath(
                    '//div[@class="component-content"]/div[1]//div[@class="rt-content-card__details-wrapper"]'
                )
            for d in div:

                location_name = "".join(d.xpath(".//h3/text()"))
                info = d.xpath(".//text()")
                info = list(filter(None, [a.strip() for a in info]))
                ad = " ".join(info[1:]).replace("\n", "").replace("\xa0", "").strip()
                if ad.find("T:") != -1:
                    ad = ad.split("T:")[0].strip()
                if ad.find("E:") != -1:
                    ad = ad.split("E:")[0].strip()
                if ad.find("W:") != -1:
                    ad = ad.split("W:")[0].strip()
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                if street_address == "Hafnarfjordor":
                    street_address = ad.split("Hafnarfjordor")[0].strip()
                state = a.state or "<MISSING>"
                postal = a.postcode or "<MISSING>"
                country_code = api_url.split("/")[-1].strip()
                city = a.city or "<MISSING>"
                if street_address.find("Ulaanbaatar") != -1:
                    street_address = street_address.replace("Ulaanbaatar", "").strip()
                    city = "Ulaanbaatar"
                if ad.find("Hafnarfjordor") != -1:
                    city = "Hafnarfjordor"

                phone = "".join(info).split("T:")[1].strip()
                if phone.find("(") != -1:
                    phone = phone.split("(")[0].strip()
                session = SgRequests()
                r = session.get("https://www.riotinto.com/operations", headers=headers)
                tree = html.fromstring(r.text)
                try:
                    latitude = (
                        "".join(tree.xpath("//*[@data-properties]/@data-properties"))
                        .split(f"{slug}")[0]
                        .split('Latitude":"')[-1]
                        .split('",')[0]
                        .strip()
                    )
                    longitude = (
                        "".join(tree.xpath("//*[@data-properties]/@data-properties"))
                        .split(f"{slug}")[0]
                        .split('Longitude":"')[-1]
                        .split('",')[0]
                        .strip()
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
                    hours_of_operation=SgRecord.MISSING,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
