from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(tree):
    out = {}
    script = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = script.split("var locations =")[1].split("];")[0] + "]"
    lines = eval(text)
    i = 0
    for line in lines:
        out[f"{i}"] = ",".join(map(str, line[-3:-1]))
        i += 1

    return out


def fetch_data(sgw: SgWriter):
    api = "https://www.pizzainn.com/locations/"
    data = {
        "longitude": "-97.12516989999999",
        "latitude": "33.0218117",
        "radius": "10000",
    }
    r = session.post(api, data=data, headers=headers)
    tree = html.fromstring(r.text)
    loc = tree.xpath("//div[@class='row']")
    coords = get_coords(tree)

    i = 0
    for l in loc:
        location_name = "".join(l.xpath(".//h3[@class='loc-name']/a/text()")).strip()
        street_address = "".join(
            l.xpath(".//span[@class='loc-address-1']/text()")
        ).strip()
        line = "".join(l.xpath(".//span[@class='loc-address-3']/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        page_url = "".join(l.xpath(".//h3[@class='loc-name']/a/@href"))
        phone = "".join(l.xpath(".//span[@class='loc-phone']//text()")).strip()

        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        latitude, longitude = coords.get(f"{i}", ",").split(",")

        _tmp = []
        hours = l.xpath(".//span[@class='loc-hours']/text()")
        for h in hours:
            if "; Buffet" in h:
                h = h.split("; Buffet")[0].strip()
            if "; Dining" in h:
                h = h.split("; Dining")[0].strip()
            if "JOIN" in h:
                h = h.split("JOIN")[0].strip()
            if "; DEL/CO" in h:
                h = h.split("; DEL/CO")[0].strip()
            if ", Delivery" in h:
                h = h.split(", Delivery")[0].replace("Dining Room: ", "").strip()
            if "; Delivery" in h:
                h = h.split("; Delivery")[0].strip()
            if "Buffet ends" in h:
                h = h.split("Buffet ends")[0].strip()
            if "Store Hours:" in h:
                h = h.split("; Store Hours:")[0].strip()
            _tmp.append(h)

        hours_of_operation = ";".join(_tmp)
        i += 1

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.pizzainn.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
