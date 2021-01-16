import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import urllib.parse
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kellyservices_ca")
session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    zipcodes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=100,
    )

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "rxVisitor=1606802947054SPKKB4VUDOOQ5E35F25PO888KVDCHSGA; dtCookie=v_4_srv_1_sn_B60D4E23E8AC4868EF07BB5019D5BA46_perc_100000_ol_0_mul_1_app-3Afeb6e3cc1673e5e4_1; rxvt=1606805233166|1606802947059; dtPC=1$3432565_164h-vWMMNFVFMOKKDNHMWPKCCRLWUUNPCHOOD-0e14; dtLatC=1; dtSa=true%7CC%7C-1%7CSearch%7C-%7C1606803487264%7C3432565_164%7Chttps%3A%2F%2Fbranchlocator.kellyservices.com%2Fdefault.aspx%7CKelly%20Services%20-%20Branch%20Locator%7C1606803434274%7C%7C",
        "Host": "branchlocator.kellyservices.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    }

    base_url = "https://www.kellyservices.ca"

    loc_search_url = "https://branchlocator.kellyservices.com/default.aspx?s=&l="
    r_loc_search = session.get(loc_search_url, headers=headers)
    soup_loc_search = BeautifulSoup(r_loc_search.text, "lxml")
    view_state = urllib.parse.quote(
        soup_loc_search.find("input", {"id": "__VIEWSTATE"})["value"]
    )
    event_validation = urllib.parse.quote(
        soup_loc_search.find("input", {"id": "__EVENTVALIDATION"})["value"]
    )

    for zip_code in zipcodes:
        try:
            if zip_code == 81132:
                zip_code = 10016

            data = ""
            if zip_code == 10016:
                data = "__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%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%2BLf%2Bo8PLt712LOvzu1DvZnodm8G23l1qAWiw%3D%3D&__VIEWSTATEGENERATOR=CA0B0334&__EVENTVALIDATION=%2FwEdAE3%2Fg%2FmTOQChtZgt6KP%2FBkVSN3W2tLsLLK8pySpHWqlSgnCJ5pZeQ66%2Bqouo43wVZw0P1x6FYtKIrzXsy%2B6tf%2BLYcyq2f6sFSmr8SCx%2FbhKMr%2B5vkqLQvDEJ1mpcK37a202XE9VTVkNEV%2BvmBGMfxuMFfZmnBlECFZyyPPxjbZrL8i7IGGSeNkDDkxjDlzlDXVaZlI1tu7vMI0B0Skrz4iR5js29MSWeYokYriZYC%2FxznVNOCRtxYGVwNyvNRztDTBS5hskmwfv8lAteD%2BjBSql%2BCUf1b2NXlffB2lbfYdRXAPpmYxiN4hPY7vPGpsvVuHAO4aejy6KHVRFt5fsBSeVxP4S5vHc7g9h1wWVmEio3u85Mr8%2FeJogsT0qaMwABtte2jNQiDJ5kxIXKjAT1CA3Uwxzms0Q07G4CNarrnTsXeSua0IctGs1cKsogqo8Dj9jfhOGdXpznnasoZa%2FkqAiWmxdMBDJqQorUinbVLZ%2FD%2BeztYiNzywc7XG89h9Xx0IZDke1E83Ly4RaAQxIJeIc2dtARnmkh%2FbmKHCTDYGLrYvb4QXriZ6ee36DnDV04PBiEPyI49UG4SiY9TYXbJg45EyFd7zIlF8VPT4fAZMhv6xTVE5%2FW8pk8xOOsh2cTv%2BnPtJU5DV1ASKyzEVLUdjlnPm2YFD9kahuFPj0mASg3b37E%2FieMCt2Rd8l9vafH8p1jEuRVHpsd%2BY2lxyoXzBPhbeQyPSMaBrK60SfFhu5hVM2H6oK%2BP8NiZlsbIe0TdvJVlflEQRyoKIumZqqZGn7%2FIbMVFjYnyHS%2FtUx0FMnn1N17gFLUoiT0xBpLxvNffXw0uzxlpG45dvlvNzNepRulD%2Fz3FARIz%2BZmkk4yJ8REsmgX6I7sKJqPNyw9ukkmMd0BcpaIT8QhRE%2F3Oi9WVaRdUeP1%2FzPLR2XXtsFSS4Uq4uMptQwFnLIhITzHFJCEJIf%2B%2F%2F64ShqDkeSj98S%2Bu1H9aBLVyIYVlczDiXaloz22tWp52MCd3qsfyrfwmtbzJOWPvnuMSyXS5J%2Barq%2B4CYTS64ezxQLgEnq10HW11T7CTA8TTs%2FVgV2YZ2K5o04j%2FkDRvKfmI26ycOjDra%2BjfoP23ZQdmqxAfdMtkXcZcs8LbL9F1pZQOPxr1s8Sc1Zi7L4267Q0512uf4FMLQLcn%2B8VcgmS26Jow3ASXgT7eTPaN4Rx6%2FWCWYg8fkuw6RD%2BnpMCAatGw1bjkvnt432XEaQdwY7jIUp25MiG2sS8L78t2ZbbaIs6Q93xTzftj5hJx5m85qP9gzdNMYUq4WracCzwuv3eFMtZvDWpM90LY7sBXAUcD%2FQB0Jc6YFU96ief2lP%2BmVnn1Ha8kSLXP6K2ht6za4pf5eO1UaYuqSZm%2FhJLGtDBPWs2vCXYvZ86bGLpq%2FzWxp1LM2wOBFyK1yKIPl6N%2FsNS9zDLMEyPlUiE4nFK9%2Fh1Nelnj26g6eZunl3CKz2xcDZJyMYR5S3bvwtcq%2FUxK6%2FWkCmVzxCnpIiZyQ4UTMeomKXML%2FH9Lq8WfStrSMChxzYy9DZ3835h7W1lcmRVjtTdVzRZn7DFyWrI8V%2FOY7qic3S0ZDjCzqE9M2ZhdeT8VcySt16rvCMCIUpaLVJWEP4UM52i16schl8lhsxv%2FDy5D9CO4g%2BZ3kQbn67PXrQhyZZebxbVHVYa68VFG7ZZ&ddlInLanguage=1&txtLanguage=1&txtSecondaryLanguage=1&txtPrimaryLanguage=1&ddlBranchTypes=15&txtZip=&txtCity=New+York&ddlStates=NY&btnSearch=+Search+&txtServiceLine=0&txtDisplayMode=expanded"
            else:
                data = (
                    "__VIEWSTATE="
                    + view_state
                    + "&__EVENTVALIDATION="
                    + event_validation
                    + "&txtZip="
                    + str(zip_code)
                    + "&btnSearch=+Search"
                )
            r_locations = session.post(
                "https://branchlocator.kellyservices.com/default.aspx",
                headers=headers,
                data=data,
            )

            soup_locations = BeautifulSoup(r_locations.text, "lxml")

            for location in soup_locations.find_all(
                "a", {"onclick": re.compile("setLocation")}
            ):
                geo_url = location["href"].replace("'", "")
                address_list = (
                    location["onclick"]
                    .replace("setLocation(", "")
                    .replace(")", "")
                    .replace("'", "")
                    .split(",")
                )

                locator_domain = base_url
                location_name = "<MISSING>"
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                country_code = "US"
                store_number = "<MISSING>"
                phone = "<MISSING>"
                location_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                page_url = "<MISSING>"
                hours_of_operation = "<MISSING>"

                store_number = (
                    str(location.parent.parent.find_previous_sibling("td").text)
                    .strip()
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                )

                phone = re.sub(
                    r"\s+",
                    " ",
                    str(address_list[-2])
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )
                ca_zip_list = re.findall(
                    r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}",
                    str(address_list),
                )
                us_zip_list = re.findall(
                    re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_list)
                )
                state_list = re.findall(
                    r"([A-Z]{2})",
                    str(address_list)
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )

                if state_list:
                    state = re.sub(
                        r"\s+",
                        " ",
                        str(state_list[-1])
                        .strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", ""),
                    )

                if ca_zip_list:
                    zipp = re.sub(
                        r"\s+",
                        " ",
                        str(ca_zip_list[-1])
                        .strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", ""),
                    )
                    country_code = "CA"

                if us_zip_list:
                    zipp = re.sub(
                        r"\s+",
                        " ",
                        str(us_zip_list[-1])
                        .strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", ""),
                    )
                    country_code = "US"

                location_name = re.sub(
                    r"\s+",
                    " ",
                    str(address_list[0])
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )
                street_address = re.sub(
                    r"\s+",
                    " ",
                    str(" ".join(address_list[1:-5]).strip())
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )
                city = re.sub(r"\s+", " ", str(address_list[-5]))

                latitude = re.sub(
                    r"\s+",
                    " ",
                    str(geo_url.split("&sll=")[1].split(",")[0])
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )
                longitude = re.sub(
                    r"\s+",
                    " ",
                    str(geo_url.split("&sll=")[1].split(",")[1])
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", ""),
                )
                if latitude == "0":
                    latitude = "<MISSING>"
                if longitude == "0":
                    longitude = "<MISSING>"

                store = [
                    locator_domain,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipp,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                    page_url,
                ]

                if str(store[2] + str(store[-7]) + store[1]) in addressess:
                    continue
                addressess.append(str(store[2] + str(store[-7]) + store[1]))
                store = [
                    str(x)
                    .strip()
                    .strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    if x
                    else "<MISSING>"
                    for x in store
                ]
                yield store
        except:
            continue


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
