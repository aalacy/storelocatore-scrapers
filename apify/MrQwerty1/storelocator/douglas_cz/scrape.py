import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    countries = ["CZ", "RO"]

    for cc in countries:
        locator_domain = f"https://www.douglas.{cc.lower()}/"
        api = f"https://www.douglas.{cc.lower()}/StoreLocator/search"
        extra = f"https://www.douglas.{cc.lower()}/storelocator/"

        data = {
            "lat": "0",
            "lng": "0",
            "distance": "0",
            "input": "",
            "catFilter": "",
            "byname": "",
        }
        r = session.post(api, headers=headers, data=data)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@data-id]")

        for d in divs:
            location_name = "".join(
                d.xpath(
                    ".//div[@class='rd__item-result__details__content__shopname']//text()"
                )
            ).strip()
            raw_address = "".join(
                d.xpath(
                    ".//div[@class='rd__item-result__details__content__address']//text()"
                )
            ).strip()
            if cc == "CZ":
                postal = re.findall(r"\d{3} \d{2}|\d{5}", raw_address).pop()
            else:
                postal = re.findall(r"\d{5,6}", raw_address).pop()

            street_address = raw_address.split(postal)[0].strip()
            if street_address.endswith(","):
                street_address = street_address[:-1]

            city = raw_address.split(postal)[-1].strip()
            if "-" in city:
                city = city.split("-")[0].strip()
            if city[-1].isdigit():
                city = " ".join(city.split()[:-1])
            store_number = "".join(d.xpath("./@data-id"))
            page_url = "".join(
                d.xpath(
                    ".//a[@class='rd__button rd__button--tertiary rd__button--lg']/@href"
                )
            )
            if not page_url or page_url == locator_domain:
                page_url = extra

            phone = "".join(d.xpath(".//a[@tel]/text()")).strip()
            if not phone:
                phone = (
                    "".join(d.xpath(".//span[contains(text(), 'Fax.')]/text()"))
                    .replace("Fax.", "")
                    .strip()
                )
            text = "".join(d.xpath("./following-sibling::script[1]/text()"))
            try:
                latitude = text.split(".addStore(")[1].split(",")[1].strip()
                longitude = text.split(".addStore(")[1].split(",")[2].strip()
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            hours = d.xpath(
                ".//div[@class='rd__item-result__details__content__hours']/span/text()"
            )
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=cc,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
