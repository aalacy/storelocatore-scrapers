const Apify = require('apify');

const enqueueStatePages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: '#main > div > div.StateList-container > div > div > div > div > div a',
  pseudoUrls: [
    'https://stores.rue21.com/[[a-z]][[a-z]].html',
  ],
  userData: {
    urlType: 'state',
  },
});

const enqueueCityPages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a',
  pseudoUrls: [
    'https://stores.rue21.com/[[a-z]][[a-z]]/[(\\w|-)+].html',
  ],
  userData: {
    urlType: 'city',
  },
});

const enqueueDetailPages = async ({ page }, { requestQueue }) => Apify.utils.enqueueLinks({
  page,
  requestQueue,
  selectors: 'a',
  pseudoUrls: [
    'https://stores.rue21.com/[[a-z]][[a-z]]/[.*]/[.*].html',
  ],
  userData: {
    urlType: 'detail',
  },
});

module.exports = {
  enqueueStatePages,
  enqueueCityPages,
  enqueueDetailPages,
};
