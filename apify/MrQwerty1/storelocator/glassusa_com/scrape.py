import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_states(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//a[@class='state-li']/@href")


def get_address(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    try:
        text = "".join(tree.xpath("//script[contains(text(), 'areaServed')]/text()"))
        j = json.loads(text)["provider"]["address"]
    except:
        j = {}
    street = j.get("streetAddress")
    city = j.get("addressLocality")
    state = j.get("addressRegion")
    postal = j.get("postalCode")

    return street, city, state, postal


def generate_pin_dict(text):
    d = dict()
    for t in text.split("\n"):
        if t.find("branch") != -1:
            line = (
                t.strip()[:-1].replace(":", '":').replace(",", ',"').replace("{", '{"')
            )
            js = eval(f'{line.split("pop")[0][:-2]}}}')
            _id = js.get("branch")
            lat = js.get("latitude")
            lon = js.get("longitude")
            d[_id] = {"lat": lat, "lon": lon}
        if t.find("];") != -1:
            break
    return d


def fetch_data(sgw: SgWriter):
    states = get_states("https://www.glassusa.com/locations/")

    for s in states:
        r = session.get(f"https://www.glassusa.com{s}", headers=headers)
        tree = html.fromstring(r.text)
        items = tree.xpath("//li[@class='group-container']")
        text = "".join(tree.xpath("//script[contains(text(),'mapMarker ')]/text()"))
        _tmp = generate_pin_dict(text)
        for item in items:
            store_number = "".join(item.xpath("./@data-branch"))
            page_url = "https://www.glassusa.com" + "".join(
                item.xpath(".//span[@class='item-more']/a/@href")
            )
            line = item.xpath(".//span[@class='item-address']/span[not(@class)]/text()")
            line = list(filter(None, [l.replace("\xa0", " ").strip() for l in line]))

            if len(line) > 1:
                street_address = ", ".join(line[:-1])
                line = line[-1]
                city = line.split(",")[0].strip()
                line = line.split(",")[1].strip()
                state = line.split()[0]
                postal = line.split()[1]
            elif not line:
                street_address, city, state, postal = get_address(page_url)
            else:
                line = line.pop()
                street_address = SgRecord.MISSING
                city = line.split(",")[0].strip()
                state = line.split(",")[1].strip()
                postal = SgRecord.MISSING

            country_code = "US"
            location_name = "".join(
                item.xpath(".//span[@class='loc-name highlight']/text()")
            ).strip()
            phone = "".join(
                item.xpath(
                    ".//span[@class='item-phone']/span[@class='highlight']/text()"
                )
            ).strip()
            latitude = _tmp.get(store_number, {}).get("lat")
            longitude = _tmp.get(store_number, {}).get("lon")
            if latitude == "0" or longitude == "0":
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.glassusa.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
