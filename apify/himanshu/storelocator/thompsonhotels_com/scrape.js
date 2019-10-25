const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.thompsonhotels.com/';
 
async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];

        main = $('.artsy-main-ul').find('.artsy-menu-item').find('.artsy-menu-columns').find('li').find('a');
        function mainhead(i)

        {
            if(main.length>i)

                {

          var link = $('.artsy-main-ul').find('.artsy-menu-item').find('.artsy-menu-columns').find('li').find('a').eq(i).attr('href');
          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
              const $  =cheerio.load(html);
              
              var main1 = $('.sec-1').find('address').html();//find('address').text();
              var address_tmp = main1.split('<br>');
              var location_name = address_tmp[0].replace(/<[^>]*>?/gm, '').trim();
              var address = address_tmp[1].replace(/<[^>]*>?/gm, '').trim();
              var city_tmp = address_tmp[2].replace(/<[^>]*>?/gm, '').trim();
              var city_tmp1 = city_tmp.split(',');
              
              if (city_tmp1.length == 2){
                var city =city_tmp1[0];
                var state_tmp = city_tmp1[1];
                var state_tmp1 = state_tmp.split(' ');
                if(state_tmp1.length == 3){

                  var state = state_tmp1[1];
                  var zip = state_tmp1[2];

                }
                else if (state_tmp1.length == 4){
                  var state = state_tmp1[1];
                  var zip = state_tmp1[2]+state_tmp1[3];


            }
                 
                 
              }
               else if (city_tmp1.length == 1){
                var city =city_tmp1[0];
                var state = '<MISSING>';
                var zip = '<MISSING>';
                
              }
               else if (city_tmp1.length == 3){
                var city =city_tmp1[0];
                var state_tmp = city_tmp1[2];
                var state_tmp1 = state_tmp.split(' ');
                    if(state_tmp1.length == 5){

                      var state = 'DC';
                      var zip = state_tmp1[4];

                    }
                    else if (state_tmp1.length == 3){
                      var state = state_tmp1[1];
                      var zip = state_tmp1[2];


                }
                 

              }

             

              var phone_tmp = $('.sec-2').find('a:nth-child(3)').text();
              var phone = phone_tmp.replace('infodc@thompsonhotels.com','<MISSING>');
              if(zip.length == 5 || zip == '<MISSING>' ){

                var country_code = 'US';
               
              }

             
              else{
                var country_code = 'CA';
              }
              

               
              items.push({  

                locator_domain: 'https://www.thompsonhotels.com/', 

                location_name: location_name, 

                street_address: address,

                city: city, 

                state: state,

                zip:  zip,

                country_code: country_code,

                store_number: '<MISSING>',

                phone: phone,

                location_type: '<MISSING>',

                latitude: '<MISSING>',

                longitude: '<MISSING>', 

                hours_of_operation: '<MISSING>',
              
                page_url : link}); 
             
              
                mainhead(i+1);

            }
          });
         
        
       

         

                          
           }


          else{
  
          resolve(items);
  
       }
  } 

mainhead(0);          
       
          }
 
     });

  
 
    });
  }
  
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
      
      
      await Apify.pushData(data);
    
    });