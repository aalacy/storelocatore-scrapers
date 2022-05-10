import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_address(line):
    state = "".join(re.findall(r"[A-Z]{2,3}", line))
    post = "".join(re.findall(r"\d{4}", line))
    line = line.replace(post, "").replace(state, "").replace("Australia", "").strip()
    while line.endswith(","):
        line = line[:-1].strip()

    if "," in line:
        city = line.split(",")[-1].strip()
        street = ",".join(line.split(",")[:-1])
    else:
        adr = parse_address(International_Parser(), line)
        adr1 = adr.street_address_1 or ""
        adr2 = adr.street_address_2 or ""
        street = f"{adr1} {adr2}".strip()
        city = adr.city or SgRecord.MISSING

    return street, city, state, post


def fetch_data(sgw: SgWriter):
    api = "https://www.rightathome.com.au/index.php?option=com_storelocator&view=map&format=raw&searchall=1&Itemid=588&catid=-1&tagid=-1&featstate=0"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//marker")

    for d in divs:
        raw_address = "".join(d.xpath("./address/text()")).strip()
        street_address, city, state, postal = get_address(raw_address)
        country_code = "AU"
        location_name = "".join(d.xpath("./name/text()")).strip()
        slug = "".join(d.xpath("./url/text()")).strip()
        page_url = f"https://www.rightathome.com.au{slug}"
        phone = "".join(d.xpath("./phone/text()")).strip()
        latitude = "".join(d.xpath("./lat/text()")).strip()
        longitude = "".join(d.xpath("./lng/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rightathome.com.au/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
