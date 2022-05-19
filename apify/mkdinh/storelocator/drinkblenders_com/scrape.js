const Apify = require('apify');

const MISSING = '<MISSING>';
function getOrDefault(value) {
  const data = typeof value === 'string' ? value.trim() : value;
  return data || MISSING;
}

function parseInfo(text, name) {
  const components = text.split(/\n/);
  const hasCity = components.length > 3;
  const city = hasCity ? components[0].replace(/\(|\)/g, '') : name;
  const street_address = hasCity ? components[1] : components[0];
  const phoneAndHours = hasCity ? components[3] : components[2];
  const phoneNumber = phoneAndHours.slice(0, 14).trim();
  const hours = phoneAndHours.slice(15).trim();

  const phone = phoneNumber.replace(/\(|\)|-|\s/g, '').trim();
  const hours_of_operation = hours.replace(/, /g, ',').trim();
  return { city, street_address, phone, hours_of_operation };
}

function parseLocationName(text) {
  return text.replace(/\(|\)/g, '').trim();
}

Apify.main(async () => {
  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({ url: 'https://www.drinkblenders.com/blendersland/' });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    handlePageFunction: async function ({ $, request }) {
      const data = $('h4')
        .map(function () {
          const locationNameElement = $(this);
          // catch empty spot
          if (locationNameElement.is(':empty')) {
            return;
          }

          let location_name = parseLocationName(locationNameElement.text());

          // get address. Address is the next sibling to each name element
          const info = locationNameElement.next().text();
          const { city, street_address, phone, hours_of_operation } = parseInfo(
            info,
            location_name
          );

          return {
            locator_domain: 'drinkblenders.com',
            page_url: request.url,
            location_name: getOrDefault(location_name),
            street_address: getOrDefault(street_address),
            city: getOrDefault(city),
            state: 'CA',
            zip: MISSING,
            country_code: 'US',
            store_number: MISSING,
            phone: getOrDefault(phone),
            location_type: MISSING,
            latitude: MISSING,
            longitude: MISSING,
            hours_of_operation: getOrDefault(hours_of_operation),
          };
        })
        .toArray();

      const pois = data.filter((rec) => rec);
      await Apify.pushData(pois);
    },
  });

  await crawler.run();
});
