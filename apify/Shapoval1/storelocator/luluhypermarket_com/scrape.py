from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.luluhypermarket.com/en-ae/"
    api_url = "https://www.luluhypermarket.com/en-ae/store-finder"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dropdown-menu country-dropdown "]/a')
    for d in div:
        country_code = "".join(d.xpath(".//@data-isocode")).upper()
        slug_url = "".join(d.xpath(".//@data-url"))
        api_country_url = f"https://www.luluhypermarket.com{slug_url}/ListOfStores"
        cookies = {
            "XSRF-TOKEN": "2256fbc4-ad01-4ce7-a994-58e79ab3afe1",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": "https://www.luluhypermarket.com/en-ae/DeliveryLocation",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers",
        }

        r = session.get(api_country_url, headers=headers, cookies=cookies)
        try:
            js = r.json()["listOfCncPos"]
        except:
            continue
        for j in js:

            location_name = j.get("displayName") or "<MISSING>"
            store_number = j.get("name") or "<MISSING>"
            r = session.get(
                f"https://www.luluhypermarket.com{slug_url}/getStoreByCode?storeCode={store_number}",
                headers=headers,
                cookies=cookies,
            )
            try:
                js = r.json()["listOfCncPos"]
            except:
                continue
            for j in js:

                page_url = f"https://www.luluhypermarket.com{slug_url}"
                a = j.get("address")
                street_address = a.get("line1") or a.get("line1") or "<MISSING>"
                city = a.get("luluCity").get("name") or "<MISSING>"
                if str(city).find("(") != -1:
                    city = str(city).split("(")[0].strip()
                phone = a.get("phone") or "<MISSING>"
                phone = str(phone).replace("Tel:", "").strip()
                hours = j.get("deliverySlots")
                hours_of_operation = "<MISSING>"
                days = [
                    "MONDAY",
                    "TUESDAY",
                    "WEDNESDAY",
                    "THURSDAY",
                    "FRIDAY",
                    "SATURDAY",
                    "SUNDAY",
                ]
                tmp = []
                if hours:
                    for i in days:
                        day = i.capitalize()
                        try:
                            times = hours.get(f"{i}")[0].get("slot")
                        except:
                            continue
                        line = f"{day} - {times}"
                        tmp.append(line)
                    hours_of_operation = " ;".join(tmp)

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
