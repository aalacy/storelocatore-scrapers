from lxml import html
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


logger = SgLogSetup().get_logger("bylinebank_com")
session = SgRequests()


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.bylinebank.com/"
    api_url = "https://www.bylinebank.com/sitemap/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="sitemap_locations"]/ul/li/a')

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1//text()"))
        ad = "".join(tree.xpath('//span[@class="address"]/text()'))
        location_type = "Branch"
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[1].strip()
        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
                .split('"latitude":')[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
                .split('"longitude":')[1]
                .split("}")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = "".join(tree.xpath('//a[@class="phone_number"]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Lobby Hours"]/following-sibling::table//tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Sat - Sun -", "")
            .replace("Sun -", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("am") == -1:
            hours_of_operation = "<MISSING>"

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)

    header = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS",
    }

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=70,
        expected_search_radius_miles=70,
        max_search_results=None,
    )

    for lat, long in search:

        result_coords = []
        url = "https://bylinebank.locatorsearch.com/GetItems.aspx"
        data = (
            "address="
            + "&lat="
            + str(lat)
            + "&lng="
            + str(long)
            + "&searchby=ATMSF%7C&SearchKey=&rnd=1569844320549"
        )
        pagereq = session.post(url, data=data, headers=header)
        soup = BeautifulSoup(pagereq.text, "html.parser")
        add2 = soup.find_all("add2")
        address1 = soup.find_all("add1")
        loc = soup.find_all("marker")
        name = soup.find_all("title")
        locator_domain = "https://www.bylinebank.com"
        location_type = "ATM"
        for i in range(len(address1)):
            street_address = address1[i].text
            city = add2[i].text.split(",")[0]
            state = add2[i].text.replace(",,", ",").split(",")[1].split()[0]

            zip1 = add2[i].text.replace(",,", ",").split(",")[1].split()[1]
            if "<b>" in add2[i].text:
                phone = add2[i].text.split("<b>")[1].replace("</b>", "").strip()
            else:
                phone = "<MISSING>"

            location_name = name[i].text.replace("<br>", "").strip()
            page_url = "https://www.bylinebank.com/locator/"

            if len(zip1) == 3 or len(zip1) == 7:
                country_code = "CA"
            else:
                country_code = "US"

            hours_of_operation = "<MISSING>"
            latitude, longitude = "<MISSING>", "<MISSING>"
            try:
                latitude = loc[i].attrs["lat"]
                longitude = loc[i].attrs["lng"]
            except:
                pass
            result_coords.append((latitude, longitude))

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip1,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {city}, {state} {zip1}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
