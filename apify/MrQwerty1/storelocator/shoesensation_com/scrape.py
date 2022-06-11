from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.shoesensation.com",
        "Connection": "keep-alive",
        "Referer": "https://www.shoesensation.com/store-locator",
        "TE": "Trailers",
    }

    r = session.post(
        "https://www.shoesensation.com/store_locator/location/updatemainpage",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[contains(text(), 'Details')]")
    for d in div:
        page_url = "".join(d.xpath(".//@data-href"))

        r = session.get(page_url)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath("//h1[@class='mw-sl__details__name']/text()")
        ).strip()
        line = tree.xpath(
            "//li[@class='mw-sl__details__item mw-sl__details__item--location']/div[@class='info']/text()"
        )
        line = list(
            filter(
                None, [" ".join(l.replace("United States", "").split()) for l in line]
            )
        )

        street_address = line[0].rsplit(",", 1)[0].strip()
        if not street_address[0].isdigit():
            for s in street_address:
                if s.isdigit():
                    ind = street_address.index(s)
                    street_address = street_address[ind:]
                    break
        if street_address == "56007, USA":
            street_address = "Leland Dr"
        if street_address.find("3100 N Broadway St, Poteau, OK 74953, USA") != -1:
            street_address = street_address.split(",")[0].strip()

        city = line[0].rsplit(",", 1)[1].strip()
        state = line[1].split(",")[0].strip()
        postal = line[1].split(",")[1].strip()

        if f", {city}" in street_address:
            street_address = street_address.split(f", {city}")[0].strip()
        country_code = "US"
        store_number = page_url.split("-")[-1]
        if store_number.isalpha():
            store_number = SgRecord.MISSING

        phone = "".join(tree.xpath("//a[@class='btn btn-link phone']/text()")).strip()
        text = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude, longitude = text.split("&center=")[1].split(",")
            if "0.00" in latitude:
                raise IndexError
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        divs = tree.xpath("//div[@class='mw-sl__infotable__row']")
        for di in divs:
            day = "".join(di.xpath("./span[1]/text()")).replace("|", "").strip()
            time = "".join(di.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp).replace("<br />", " ")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.shoesensation.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
