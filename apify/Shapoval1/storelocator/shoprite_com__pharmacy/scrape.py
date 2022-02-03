from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://shoprite.com/pharmacy"
    session = SgRequests()
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    payload = "Region=&SearchTerm=21216&FilterOptions%5B0%5D.IsActive=false&FilterOptions%5B0%5D.Name=Online+Grocery+Delivery&FilterOptions%5B0%5D.Value=MwgService%3AShop2GroDelivery&FilterOptions%5B1%5D.IsActive=false&FilterOptions%5B1%5D.Name=Online+Grocery+Pickup&FilterOptions%5B1%5D.Value=MwgService%3AShop2GroPickup&FilterOptions%5B2%5D.IsActive=false&FilterOptions%5B2%5D.Name=Platters%2C+Cakes+%26+Catering&FilterOptions%5B2%5D.Value=MwgService%3AOrderReady&FilterOptions%5B3%5D.IsActive=true&FilterOptions%5B3%5D.IsActive=false&FilterOptions%5B3%5D.Name=Pharmacy&FilterOptions%5B3%5D.Value=MwgService%3AUmaPharmacy&FilterOptions%5B4%5D.IsActive=false&FilterOptions%5B4%5D.Name=Retail+Dietitian&FilterOptions%5B4%5D.Value=ShoppingService%3ARetail+Dietitian&Radius=50000&Take=999&Redirect="

    r = session.post(
        "https://shoprite.com/StoreLocatorSearch", headers=headers, data=payload
    )
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="stores__store"]')
    for d in div:

        page_url = (
            "".join(d.xpath('.//a[@class="store__link"]/@href'))
            .replace(":443", "")
            .strip()
        )
        location_name = "".join(d.xpath('.//span[@class="store__name"]/text()'))
        street_address = "".join(
            d.xpath('.//div[@class="store__address"]/div[1]/text()')
        )
        ad = "".join(d.xpath('.//div[@class="store__address"]/div[2]/text()'))
        state = " ".join(ad.split(",")[1].split()[:-1]).strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = page_url.split("/")[-1].strip()
        latitude = (
            "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
            .split("=")[-1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
            .split("=")[-1]
            .split(",")[1]
            .strip()
        )
        info = d.xpath(
            './/h4[contains(text(), "Pharmacy")]/following-sibling::p/text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        phone = "<MISSING>"
        for i in info:
            if "Phone" in i:
                phone = "".join(i).replace("Phone", "").strip() or "<MISSING>"
        str_info = " ".join(info).replace("\n", " ").replace("\r", " ").strip()
        str_info = " ".join(str_info.split())
        hours_of_operation = str_info
        if hours_of_operation.find("Phone") != -1:
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()
        if hours_of_operation.find("----") != -1:
            hours_of_operation = hours_of_operation.split("----")[0].strip()
        if hours_of_operation.find("Registered") != -1:
            hours_of_operation = hours_of_operation.split("Registered")[0].strip()
        if hours_of_operation == "Retail Dietitian Katie Gallagher, MS, RD, LD":
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        if hours_of_operation.find("Free delivery") != -1:
            hours_of_operation = hours_of_operation.split("Free delivery")[0].strip()
        if hours_of_operation.find("Free RX") != -1:
            hours_of_operation = hours_of_operation.split("Free RX")[0].strip()
        hours_of_operation = hours_of_operation or "<MISSING>"
        address = f"{street_address} {city}, {state} {postal}"
        address = " ".join(address.split())

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
            raw_address=address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
