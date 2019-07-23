import time
import datetime
import json
import requests
import threading
from random import randint
from dhooks import Webhook, Embed

def getProxies():
    # Grabs proxies from text file.
    proxy = []
    proxy_txt = open('proxies.txt', 'r')
    for proxies in proxy_txt:
        proxies = proxies.strip('\n')
        proxy.append(proxies)
    proxy_txt.close()
    return proxy
    
def getContent(url):
    # Gets page conent from target website.
    proxy_list = getProxies()
    url_1 = (url + 'products.json')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    condition = True
    while condition == True:
        if len(proxy_list) > 0:
            try:
                x = randint(0 , (len(proxy_list) - 1))
                proxy = proxy_list[x]
                proxy_dict = {'http': ('http://{}'.format(proxy)), 'https': ('https://{}'.format(proxy))}
                webpage = requests.get(url_1, headers=headers, proxies=proxy_dict)
                products = json.loads((webpage.text))['products']
                condition = False
            except:
                print('Error getting orignial products.\n Sleeping 3 minutes...')
                time.sleep(180)
                continue
        else:
            try:
                webpage = requests.get(url_1, headers=headers)
                products = json.loads((webpage.text))['products']
            except:
                print('Error getting original products.\n Sleeping 3 minutes...')
                time.sleep(180)
                continue
    return products

def getProducts(url):
    # Adds all current products to a list.
    products = getContent(url)
    current_products = []
    for product in products: # Loops throught the 'title' handle to grab product names.
        products = (product['handle'])
        current_products.append(products)
    return current_products

def Main(url):
    # Main function. Monitors websites in real time.
    current_products = getProducts(url)
    proxies = getProxies()

    wh_file = open('webhook.txt', 'r')
    wh_link = wh_file.readline().strip()
    wh_file.close()
    
    while True:
        # Grabs a random proxy from proxy list
        try:
            x = randint(0, (len(proxies) - 1))
            proxy = proxies[x]
            proxy_dict = {'http': ('http://{}'.format(proxy)), 'https': ('https://{}'.format(proxy))}
        except:
            print('No proxies available. Using localhost...')
            pass
    
        # Monitors website for new products
        if len(proxies) > 0:
            try:
                url_1 = (url + 'products.json')
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
                webpage = requests.get(url_1, headers=headers, proxies=proxy_dict)
                products = json.loads((webpage.text))['products']
            except:
                print('Proxies banned. Sleeping for 3 minutes...')
                time.sleep(180)

        else:
            try:
                url_1 = (url + 'products.json')
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
                webpage = requests.get(url_1, headers=headers)
                products = json.loads((webpage.text))['products']
            except:
                print('Local host banned. Sleeping for 3 minutes...')
                time.sleep(180)
     
        # Loops throught the 'title' handle to grab product names.
        new_products = []
        for product in products:
            products1 = (product['handle'])                                                                                                                                   
            new_products.append(products1)

        if new_products != current_products:
            new_prod = list(set(new_products) - set(current_products))
            #new_prod = ''.join(new_prod)
            for x in range(len(new_prod)):
                current_products.insert(x, new_prod[x])
            # Product handle
                handle = products[x]['handle']
                link = (str(url) + 'products/{}'.format(handle))
            # Product name
                name = products[x]['title']
            # Grabs product image URL
                image = products[x]['images']
                image = image[x]['src']
            # Grabs ATC Links
                variants = products[x]['variants']
                sizes_list = []
                for x in range(len(variants)):
                    sizes_list.append('Size {}:'.format(variants[x]['title']) + str(url) + 'cart/{}:1'.format(variants[x]['id']))
            # Grabs product price
                price = variants[x]['price']

            # Payload message sent to discord webhook.
                hook = Webhook(wh_link)
                embed = Embed(description='***New product found!***', color=0x1e0f3, timestamp='now')
                image1 = (image)
                image2 = ('https://pbs.twimg.com/profile_images/1122559367046410242/6pzYlpWd_400x400.jpg')
                embed.set_author(name='Shopify Crawler', icon_url=image2)
                embed.add_field(name='Product Name', value=name)
                embed.add_field(name='Price', value=str(price))
                embed.add_field(name='Product Link', value=link)
                embed.add_field(name='ATC Links', value=str(sizes_list))
                embed.set_footer(text='loop', icon_url=image2)
                embed.set_thumbnail(image1)
                try:
                    hook.send(embed=embed)
                    print('{} SENT MESSAGE*$'.format(datetime.datetime.now()))
                except:
                    pass
        
        print('{} Scraping target$* {}'.format(time.strftime('%H:%M:%S'), url))
        time.sleep(30)

print('SScraper 1.0')
choice = input('Enter any key to initialize scraper$* (Press \'Q\' to quit) ')
choice = (choice.lower())
if choice == ('q'):
    exit()
     
# Grab links from text file to initialize threads.
urls = []
shopify_links = open('shopify_links.txt', 'r')
for slinks in shopify_links:
    slinks = slinks.strip('\n')
    urls.append(slinks)

shopify_links.close()

# Initializes threads to monitor multiple websites at once.
for x in range(len(urls)):
    proxy_threads = threading.Thread(target=getProxies, name='getProxy Thread {}'.format(x))
    content_threads = threading.Thread(target=getContent, name='getContent Thread {}'.format(x), args= (urls[x],))
    product_threads = threading.Thread(target=getProducts, name='getProduct Thread {}'.format(x), args= (urls[x],))
    main_threads = threading.Thread(target=Main, name='Main Thread {}'.format(x), args= (urls[x],))
    content_threads.start()
    product_threads.start()
    main_threads.start()
    print('{} initialized'.format(main_threads.name))