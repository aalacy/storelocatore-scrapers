import httpx
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumph-motorcycles.ca"
    api_url = "https://www.triumph-motorcycles.ca/dealers/dealer-search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    with SgRequests() as http:
        r = http.get(url=api_url, headers=headers)
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        tree = html.fromstring(r.text)
        div = tree.xpath('//select[@id="dealer-country-select"]/option')
        for d in div:
            slug = "".join(d.xpath(".//@value"))
            url = f"https://www.triumph-motorcycles.ca/api/v2/places/alldealers?LanguageCode={slug}&SiteLanguageCode=en-CA&Skip=0&Take=50000&CurrentUrl=www.triumph-motorcycles.ca"
            r = session.get(url, headers=headers)
            js = r.json()["DealerCardData"]["DealerCards"]
            for j in js:
                slug = "".join(j.get("DealerUrl"))
                if not slug:
                    continue

                page_url = slug
                if page_url.find("http") == -1 and page_url.find("//www") != -1:
                    page_url = f"http:{slug}"
                if page_url.find("http") == -1 and page_url.find("//www") == -1:
                    page_url = f"https://www.triumph-motorcycles.ca{slug}"
                location_name = j.get("Title")
                ad = f"{j.get('AddressLine1')} {j.get('AddressLine2')} {j.get('AddressLine3')} {j.get('AddressLine4')}".replace(
                    "None", ""
                ).strip()
                ad = " ".join(ad.split())
                a = parse_address(International_Parser(), ad)
                street_address = (
                    f"{a.street_address_1} {a.street_address_2}".replace(
                        "None", ""
                    ).strip()
                    or "<MISSING>"
                )
                if street_address.isdigit() or street_address == "<MISSING>":
                    street_address = ad.replace("None", "").strip()
                state = a.state or "<MISSING>"
                country_code = a.country or "<MISSING>"
                city = a.city or "<MISSING>"
                postal = j.get("PostCode") or "<MISSING>"
                if postal == "0":
                    postal = "<MISSING>"
                latitude = j.get("Latitude") or "<MISSING>"
                longitude = j.get("Longitude") or "<MISSING>"
                if latitude == "0" or latitude == "0.000000":
                    latitude, longitude = "<MISSING>", "<MISSING>"
                phone = "".join(j.get("Phone")) or "<MISSING>"
                if phone.find(" - WhatsApp") != -1:
                    phone = phone.split(" - WhatsApp")[0].strip()
                if phone.find(",") != -1:
                    phone = phone.split(",")[0].strip()
                if phone.count("(") == 2:
                    phone = "(" + "" + phone.split("(")[1].strip()
                hours_of_operation = (
                    "".join(j.get("OpeningTimes")).replace("<br/>", " ").strip()
                ) or "<MISSING>"
                hours_of_operation = " ".join(hours_of_operation.split())
                if hours_of_operation == "<MISSING>" and page_url.count("/") > 3:
                    try:
                        r = http.get(url=page_url, headers=headers)
                        assert isinstance(r, httpx.Response)
                        assert 200 == r.status_code
                    except AssertionError:
                        continue

                    tree = html.fromstring(r.text)
                    hours_of_operation = (
                        " ".join(
                            tree.xpath(
                                '//ul[@class="dealer-location__opening-times"]/li//text()'
                            )
                        )
                        .replace("\n", "")
                        .strip()
                    )
                    hours_of_operation = (
                        " ".join(hours_of_operation.split()) or "<MISSING>"
                    )

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
                    raw_address=f"{ad} {postal}".replace("<MISSING>", "").strip(),
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
