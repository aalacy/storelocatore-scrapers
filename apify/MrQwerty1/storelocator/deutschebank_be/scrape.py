from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def flatten(t):
    return [item for sublist in t for item in sublist]


def fetch_data(sgw: SgWriter):
    api = "https://public.deutschebank.be/contact/data/agencies.json"
    r = session.get(api, headers=headers)
    js = r.json()["agencies"]

    for j in js:
        page_url = "https://www.deutschebank.be/fr/contact/trouver-agence-prendre-rendez-vous.html"
        source = j["name"]["fr"]
        if "<a" not in source:
            pass
        else:
            tree = html.fromstring(source)
            page_url = "".join(tree.xpath(".//a/@href"))

        line = j["address"]["fr"]
        if "<br>" in line:
            adr = line.split("<br>")
        else:
            adr = line.split("<br />")
        zc = adr.pop()
        street_address = ", ".join(adr)
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        country_code = "BE"
        store_number = j.get("branchId")
        location_name = j["name_text"]["fr"]
        phone = j["phone"]["fr"]
        latitude = j.get("lat")
        longitude = j.get("long")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = j.get("rangeHours") or []

        for day, h in zip(days, hours):
            h = flatten(h)
            start = h[0].split(" - ")[0]
            end = h[-1].split(" - ")[-1]
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.deutschebank.be/fr"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
