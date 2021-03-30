from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

logger = SgLogSetup().get_logger("sutherlands_com")

session = SgRequests()

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "storenum=0; _ALGOLIA=anonymous-8722c4dc-e3c4-4db6-a1b3-2d6ef1f8bb67; _ga=GA1.2.960820933.1610610759; _fbp=fb.1.1610610759998.1510881136; laravel_session=ZpRJb3zRSCGuCLnd6lAelk7Pdzbng00RGvG23Uig; 302e79545f8dc1468f3d3ba795b88f1e1d9307b0=ZpRJb3zRSCGuCLnd6lAelk7Pdzbng00RGvG23Uig; _gid=GA1.2.783065270.1611164438; _gat_gtag_UA_7521516_1=1; LTC=eyJpdiI6IkozODBBSzdSMmVSWW5TYTdDRHdMVGc9PSIsInZhbHVlIjoiVDF0TVFZbFhuZ1wvMGFVT3NxRmt2OGN1UzlGZjh2MU1kRDFiTk9FbWdCcXI0WUJGa1wvNlA3YmlRTVhXS1k3XC95cTRGWE1rU2FEcWo5RFAxN1U1bURVXC81MHk1VXgwVTNpaEpNcEFGcHg5QmxVPSIsIm1hYyI6ImEzMGEwYTc0M2ZmZjJjZDMwNWNiMzIzYTJhYjE3ZGEwYjg3MWNhN2YyMzMyNWY0ODk2Y2FhZjU0ZGZmOTFmNzAifQ%3D%3D; XSRF-TOKEN=eyJpdiI6ImdsbU96WEdEXC9WUGY4WCt5ZFwvOWxaUT09IiwidmFsdWUiOiJ5VXQzWkJLMFh4Z2w0Vjg2MVFNaGR3clUwYkd5MDhTcUg3bFljNFRwTHVKUjQ4RnhoYk83akRnU1Uzd1hqSjFIOHU1eVlWek9Mb0pFcWdmYk5WYlRSWjkzUzNzWFN2M1MzUE5zSGx0dm9mMmZLaVBCbytLTEtpbldXYU1UZW1udCIsIm1hYyI6ImQ5N2RiMWEyZjFkMjAzMDdiYjQ0MWJkYzM0M2QxMjU0ZDFjNTQ0NzE1OTM2ZDBiZTUyYTUzNGM1MWJlZWRhN2YifQ%3D%3D",
    "Host": "sutherlands.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "X-CSRF-TOKEN": "XPpILMzHJ0U6NJRG8V7PTp8qcgGoussTlpvHLwtw",
    "X-Requested-With": "XMLHttpRequest",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    zips = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    for zip_code in zips:
        search_url = "https://sutherlands.com/locations/" + zip_code + "?distance=150"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        if len(soup) > 2:
            loc_block = soup.findAll("div", {"class": "card-block"})
            for loc in loc_block:
                linkdiv = loc.findAll("div", {"class": "col-md-4"})[2].findAll("p")
                if len(linkdiv) == 2:
                    title = loc.find("h3").text.strip()
                    street = loc.find("span", {"itemprop": "streetAddress"}).text
                    city = loc.find("span", {"itemprop": "addressLocality"}).text
                    state = loc.find("span", {"itemprop": "addressRegion"}).text
                    pcode = loc.find("span", {"itemprop": "postalCode"}).text
                    phone = loc.find("p", {"class": "phone"}).text.strip()
                    link = "https://sutherlands.com/locations/" + pcode
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    hours = loc.findAll("div", {"class": "col-md-4"})[1].text
                    hours = hours.replace("\n", " ")
                    hours = hours.lstrip("Operating Hours: ")
                    hours = hours.replace("M-F:                     ", "Mon-Fri: ")
                    hours = re.sub(pattern, " ", hours)
                    hours = re.sub(cleanr, " ", hours)
                    storeid = "<MISSING>"
                else:
                    link = linkdiv[2].find("a")["href"]
                    street = loc.find("span", {"itemprop": "streetAddress"}).text
                    city = loc.find("span", {"itemprop": "addressLocality"}).text
                    state = loc.find("span", {"itemprop": "addressRegion"}).text
                    pcode = loc.find("span", {"itemprop": "postalCode"}).text
                    phone = loc.find("p", {"class": "phone"}).text.strip()
                    hours = loc.findAll("div", {"class": "col-md-4"})[1].text
                    hours = hours.replace("\n", " ")
                    hours = hours.lstrip("Operating Hours: ")
                    hours = hours.replace("M-F:                     ", "Mon-Fri: ")
                    hours = re.sub(pattern, " ", hours)
                    hours = re.sub(cleanr, " ", hours)
                    req = session.get(link, headers=headers)
                    soup = BeautifulSoup(req.text, "html.parser")
                    title = soup.find("h1", {"class": "h2"}).text.strip()
                    storeid = link.split("/")[-1]
                    coodiv = soup.findAll("script")
                    scriptcoord = str(coodiv[12])
                    lat = scriptcoord.split("var lat = ")[1].split(";")[0]
                    lng = scriptcoord.split("var lon = ")[1].split(";")[0]

                data.append(
                    [
                        "https://sutherlands.com/",
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        storeid,
                        phone,
                        "<MISSING>",
                        lat,
                        lng,
                        hours,
                    ]
                )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()
