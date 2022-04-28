from curses import raw
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = ""
base_url = ""
urls = {
    "Vietnam": "https://www.volvocars.com/en-vn/contact-us",
    "Malta": "https://www.volvocars.com/mt/find-a-showroom",
    "Georgia": "https://www.volvocars.com/ge/find-a-showroom",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            locations = soup.select("div.oxp-exteriorFeatureTwo div.extf-content")
            for _ in locations:
                if not _.text.strip():
                    continue
                location_name = raw_address = phone = ""
                bb = [
                    b
                    for b in _.select("p", recursive=False)
                    if "Welcome" not in b.text and "კეთილი იყოს" not in b.text
                ]
                for x, pp in enumerate(bb):
                    _pp = list(pp.stripped_strings)
                    p_text = " ".join(_pp)
                    if not _pp:
                        continue
                    if "volvo car" in p_text.lower():
                        continue
                    if (
                        "Co., Ltd" in p_text
                        or "Email" in p_text
                        or "ელ.ფოსტა" in p_text
                    ):
                        continue
                    if not location_name:
                        location_name = p_text.split(":")[-1].strip()
                        continue
                    if "Hotline" in _pp or "Tel" in _pp or "ტელ" in _pp:
                        if not phone:
                            if len(_pp) == 1:
                                phone = _pp[0].split(":")[-1].split("If")[0].strip()
                            else:
                                phone = _pp[1].split(":")[-1].split("If")[0].strip()
                    elif not raw_address:
                        for aa in _pp:
                            if "Address" in aa or "მისამართი" in aa:
                                continue
                            raw_address += " " + aa.replace(":", "").strip()

                if country == "Malta":
                    addr = raw_address.split(",")
                    city = addr[-1].strip().split()[-1].replace(".", "")
                    zip_postal = addr[-1].strip().split()[-2]
                    state = ""
                    street_address = ", ".join(addr[:-2])
                elif country == "Georgia":
                    addr = raw_address.split(",")
                    city = addr[-2].strip().split()[0].replace(".", "")
                    zip_postal = addr[-2].strip().split()[-1]
                    state = ""
                    street_address = ", ".join(addr[:-2])
                else:
                    addr = parse_address_intl(raw_address + ", ")
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    street_address = street_address
                    city = addr.city
                    state = addr.state
                    zip_postal = addr.postcode
                yield SgRecord(
                    page_url=base_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country,
                    phone=phone,
                    locator_domain=locator_domain,
                    raw_address=raw_address.strip(),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
