import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    cities = ['Toronto','Montreal','Calgary','Ottawa','Edmonton','Mississauga','Winnipeg','Vancouver','Brampton','Hamilton','Quebec','Surrey','Laval','Halifax','London','Markham','Vaughan','Gatineau','Saskatoon','Longueuil','Kitchener','Burnaby','Windsor','Regina','Richmond','Richmond Hill','Oakville','Burlington','Greater Sudbury','Sherbrooke','Oshawa','Saguenay','Levis','Barrie','Abbotsford','Coquitlam','Trois Rivieres','St Catharines','Guelph','Cambridge','Whitby','Kelowna','Kingston','Ajax','Langley','Saanich','Terrebonne','Milton','St Johns','Thunder Bay','Waterloo','Delta','Chatham Kent','Red Deer','Strathcona County','Brantford','St Jean sur Richelieu','Cape Breton','Lethbridge','Clarington','Pickering','Nanaimo','Kamloops','Niagara Falls','North Vancouver','Victoria','Brossard','Repentigny','Newmarket','Chilliwack','Maple Ridge','Peterborough','Kawartha Lakes','Drummondville','St Jerome','Prince George','Sault Ste Marie','Moncton','Sarnia','Wood Buffalo','New Westminster','St John','Caledon','Granby','St Albert','Norfolk County','Medicine Hat','Grande Prairie','Airdrie','Halton Hills','Port Coquitlam','Fredericton','Blainville','St Hyacinthe','Aurora','North Vancouver','Welland','North Bay','Belleville','Mirabel','Shawinigan','Dollard Des Ormeaux','Brandon','Rimouski','Chateauguay','Mascouche','Cornwall','Victoriaville','Whitchurch Stouffville','Haldimand County','Georgina','St Eustache','Quinte West','West Vancouver','Rouyn Noranda','Timmins','Boucherville','Woodstock','Salaberry de Valleyfield','Vernon','St Thomas','Mission','Vaudreuil Dorion','Brant','Lakeshore','Innisfil','Charlottetown','Prince Albert','Langford','Bradford West Gwillimbury','Sorel Tracy','New Tecumseth','Spruce Grove','Moose Jaw','Penticton','Port Moody','West Kelowna','Campbell River','St Georges','Val dOr','Cote St Luc','Stratford','Pointe Claire','Orillia','Alma','Fort Erie','LaSalle','Leduc','Ste Julie','North Cowichan','Chambly','Orangeville','Okotoks','Leamington','St Constant','Grimsby','Boisbriand','Magog','St Bruno de Montarville','Conception Bay South','Ste Therese','Langley','Cochrane','Courtenay','Thetford Mines','Sept Iles','Dieppe','Whitehorse','Prince Edward County','Clarence Rockland','Fort Saskatchewan','La Prairie','East Gwillimbury','Lincoln','Tecumseh','Mount Pearl','Beloeil','LAssomption','Amherstburg','St Lambert','Collingwood','Kingsville','Baie Comeau','Paradise','Brockville','Owen Sound','Varennes','Candiac','Strathroy Caradoc','St Lin Laurentides','Wasaga Beach','Joliette','Essex','Westmount','Mont Royal','Fort St John','Kirkland','Cranbrook','White Rock','St Lazare','Chestermere','Huntsville','Corner Brook','Riverview','Lloydminster (Part)','Yellowknife','Squamish','Riviere du Loup','Cobourg','Beaconsfield','Dorval','St Augustin de Desmaures','Thorold','Camrose','Mont St Hilaire','Pitt Meadows','Port Colborne','Quispamsis','Oak Bay','Ste Marthe sur le Lac','Salmon Arm','Port Alberni','Esquimalt','Miramichi','Niagara on the Lake','Deux Montagnes','Beaumont','Middlesex Centre','Stony Plain','Petawawa','Pelham','St Basile le Grand','Ste Catherine','Midland','Colwood','Central Saanich','Port Hope','Swift Current','Edmundston','LAncienne Lorette','North Grenville','Yorkton','Tracadie','St Colomban','Bracebridge','Greater Napanee','Tillsonburg','Steinbach','Ste Sophie','Kenora']
    for city in cities:
        print(('Pulling City %s...' % city))
        url = 'http://www.jiffylube.ca/Locations/GeocodeAddress'
        payload = {'fieldValue': city}
        r = session.post(url, headers=headers, data=payload)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"Distance":"' in line:
                items = line.split('"Distance":"')
                for item in items:
                    if '"Store_Number":' in item:
                        store = item.split('"Store_Number":')[1].split(',')[0]
                        website = 'jiffylube.ca'
                        name = 'Jiffy Lube'
                        typ = '<MISSING>'
                        hours = ''
                        surl = item.split('StoreUrl":"')[1].split('"')[0] + '/wp-admin/admin-ajax.php?action=load_hours'
                        try:
                            r3 = session.get(surl, headers=headers)
                            if r3.encoding is None: r3.encoding = 'utf-8'
                            lines = r3.iter_lines(decode_unicode=True)
                            for line3 in lines:
                                if '<span class="textday">' in line3:
                                    g = next(lines)
                                    day = g.split('<')[0].strip().replace('\t','')
                                    next(lines)
                                    next(lines)
                                    next(lines)
                                    next(lines)
                                    next(lines)
                                    g = next(lines)
                                    hrs = g.replace('\r','').replace('\t','').replace('\n','')
                                    hrs = hrs.replace('<strong>','').replace('</strong>','')
                                    hrs = hrs.replace('<span class="hours-start">','').replace('</span>','')
                                    hrs = hrs.replace('<span class="hours-end">','')
                                    hrs = day + ': ' + hrs
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                        except:
                            pass
                        phone = item.split('Phone_Number":"')[1].split('"')[0]
                        lat = item.split('"Latitude":')[1].split(',')[0]
                        lng = item.split('"Longitude":')[1].split(',')[0]
                        add = item.split('"Address_Line_1":"')[1].split('"')[0] + ' ' + item.split('"Address_Line_2":"')[1].split('"')[0]
                        add = add.strip()
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split('Region_State":"')[1].split('"')[0]
                        zc = item.split('"Postal_Code":"')[1].split('"')[0]
                        country = 'CA'
                        hours = item.split('"FormattedHours":[')[1].split(']')[0]
                        hours = hours.replace('","','; ').replace('"','')
                        lurl = 'http://www.jiffylube.ca/locations/store/' + store + '/' + item.split('"UrlSlug":"')[1].split('"')[0]
                        if hours == '':
                            hours = '<MISSING>'
                        if zc == '':
                            zc = '<MISSING>'
                        if phone == '--':
                            phone = '<MISSING>'
                        if store not in locs:
                            locs.append(store)
                            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
