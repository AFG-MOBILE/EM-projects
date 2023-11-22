import ebay
import bestbuy

def buscarProdutos():
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    url = 'https://www.ebay.com/sch/i.html?_nkw=apple+watch+ultra+2+refurbished&_sacat=0&LH_BIN=1&LH_ItemCondition=3000&_fss=1&LH_SellerWithStore=1&_sop=16&_dmd=1&_ipg=240'

    produtos = ebay.scrape_ebay_titles_prices(url, user_agent)
    print("Produtos")
    print(produtos)
    # produtos = bestbuy.buscar_produtos_bestbuy()
    
