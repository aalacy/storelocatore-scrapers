from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.newbalance.com.au/"
urls = {
    "au": "https://www.newbalance.com.au/stores/all/",
    "nz": "https://www.newbalance.co.nz/stores/all/",
}


def _name(_):
    name = ""
    for nn in (
        _.find_parent()
        .find_parent()
        .find_parent()
        .find_parent()
        .find_previous_siblings()
    ):
        if not nn.text.strip():
            continue
        if "experience-commerce_assets-centerAlignedTextImage" not in nn["class"]:
            continue
        name = nn.select_one("div.bold").text.strip()
        break

    return "New Balance " + name


def nz_addr(addr):
    street_address = " ".join(addr[:-1])
    city = addr[-1].split()[0]
    zip_postal = addr[-1].split()[-1]

    return street_address, city, zip_postal


def au_addr(addr):
    street_address = " ".join(addr[:-1])
    city = " ".join(addr[-1].split()[:-2])
    state = addr[-1].split()[-2]
    zip_postal = addr[-1].split()[-1]

    return street_address, city, state, zip_postal


def fetch_data():
    with SgRequests() as session:
        for country_code, base_url in urls.items():
            if country_code == "nz":
                soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            else:
                soup = bs(session.get(base_url, headers=header1).text, "lxml")
            locations = soup.select("div.container div.card")
            for _ in locations:
                if not _.text.strip():
                    continue

                name = _name(_)
                addr = list(_.p.stripped_strings)
                street_address = city = state = zip_postal = ""
                if country_code == "nz":
                    street_address, city, zip_postal = nz_addr(addr)
                elif country_code == "au":
                    street_address, city, state, zip_postal = au_addr(addr)

                phone = _.select_one("p.tel-number").text.strip()
                hours = list(_.select("p")[2].stripped_strings)

                try:
                    latitude, longitude, temp = (
                        _.select("a")[-1]["href"]
                        .split("/@")[1]
                        .split("/")[0]
                        .split(",")
                    )
                except:
                    latitude = longitude = ""

                yield SgRecord(
                    page_url=base_url,
                    location_name=name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
