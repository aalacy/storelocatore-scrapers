const Apify = require('apify');
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const records = [];
  const rootUrl = new URL('https://www.aquaaston.com/sites/aah/home/hotels.parametricSearch.do?destinationId=&startDate=2019-08-15&endDate=2050-08-31');
  const { data } = JSON.parse(await request.get({
    url: rootUrl.href,
    headers: {
      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
      Accept: 'application/json, text/javascript, */*; q=0.01'
    }
  }));

  for (const poiData of data) {
    let $
    try {
      $ = cheerio.load(await request.get((new URL(poiData.url, rootUrl.origin).href)))
    // some locations do not have page, or there might be some other error. Anyway save what we can.
    } catch (error) {
      console.log(`The url ${error.options.uri} from property "${poiData.name}" returned an error: ${error}`);
      $ = cheerio.load('')
    }
    const addressBlock = $('address')
    records.push({
      locator_domain: 'aquaaston.com',
      location_name: poiData.name,
      street_address: $('span[itemprop="streetAddress"]', addressBlock).text().trim() || '<MISSING>',
      city: poiData.location_name || $('span[itemprop="addressLocality"]', addressBlock).text().trim() || '<MISSING>',
      state: $('span[itemprop="addressRegion"]', addressBlock).text().trim() || '<MISSING>',
      zip: $('span[itemprop="postalCode"]', addressBlock).text().trim() || '<MISSING>',
      country_code: '<MISSING>',
      store_number: poiData.id,
      phone: poiData.phoneNumber,
      location_type: poiData.typeDesc.join(' '),
      latitude: poiData.location.latitude,
      longitude: poiData.location.longitude,
      hours_of_operation: '<MISSING>'
    })
  }

	return records;

	// End scraper

}
