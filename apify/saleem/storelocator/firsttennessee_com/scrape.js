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
  const $ = cheerio.load(await request.get({ url: 'https://www.firsttennessee.com/support/contact-us/location-listing', headers: { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15', Accept: 'application/json, text/javascript, */*; q=0.01'}}));

  $('.js-location-list__item').each((_, poiElement) => {
    const {street_address, city, state, zip, phone, hours_of_operation} = $('.ftb-listing-item__content', poiElement).text().trim().match(
      /(\s*?(?<street_address>[\d\D]+?)\s*?\n)+?\s*?\b(?<city>[-\.A-Za-z ]+?),?\s*?\b(?<state>[A-Z]{2})\b\s*?\b(?<zip>[\d-]{5,10})\s*(?<phone>[\(\)\d-\. ]{7,})\b\s*?(?<hours_of_operation>[\d\D]+)\b\s*?$/
    ).groups;

    records.push({
      locator_domain: 'firsttennessee.com',
      location_name: $('.ftb-listing-item__title', poiElement).text().trim(),
      street_address,
      city,
      state,
      zip,
      country_code: 'US',
      store_number: '<MISSING>',
      phone,
      location_type: $(poiElement).attr('data-private') === 'True'? 'private' : $(poiElement).attr('data-commercial') === 'True'? 'commercial' : 'retail',
      latitude: '<MISSING>',
      longitude: '<MISSING>',
      hours_of_operation: hours_of_operation.replace(/\s+/g, ' ').trim(),
    })
  })

	return records;

	// End scraper

}
