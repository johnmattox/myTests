# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
from unicodedata import normalize
import pandas as pd
import sys, os
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

print("----- WebScraping de artigos no site Buscapé! -----")

busca_orig = input('Digite sua busca: ')
#busca_orig = "moto G 5 geração"
busca = normalize('NFKD', busca_orig).encode('ASCII', 'ignore').decode('ASCII')

my_url = 'https://www.buscape.com.br/search/'
for w in busca.split(" "):
    my_url= my_url+w+"-"

print("\nInicializando conexão...")
# Abre conexão e baixa HTML da página
req = Request(url=my_url[:-1]+"?pagina=1",headers=headers)
uClient = urlopen(req)
page_html = uClient.read()
uClient.close()

# Transforma HTML em obejto beautifulsoup
page_soup = soup(page_html, "html.parser")

print("\nBuscando resultados...")
# Pega número da última página da busca
try:
    max_pag = int(page_soup.findAll("ul",{"class":"pagination__list u-li-reset"})[0].findAll("li")[-2].text)
    print("%d páginas de resultados encontradas"%max_pag)
except:
    print("Error: A busca por %s não obteve resultados"%busca_orig)
    sys.exit()
    
def tira_num_do_texto(string):
    num = ""
    for c in string:
        asc = ord(c)
        if c==",":
            num=num+"."
        elif asc>=48 and asc<=57:
            num=num+c
        else:
            pass
    return float(num)

print("\nIniciando Scraping dos dados...\n")
dados_cru = []
for i in range(1,max_pag+1):
    
    # Abre conexão e baixa HTML da página i
    req = Request(url=my_url[:-1]+"?pagina=%d"%i,headers=headers)
    uClient = urlopen(req)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    containers = page_soup.find("div",{"class":"offers-result"}).findAll("div",{"class":"card__item columns small-6 medium-6 large-4"})
    for container in containers:
        nome = container.find("div",{"class":"card--product__name u-truncate-multiple-line"}).text.strip()
        preco = float(container.find("span",{"itemprop":"lowPrice"}).text.replace(".","").replace(",","."))
        if container.find("span",{"class":"bui-price__installment"}) is None:
            vezes = 0
            parcela = 0
            total_parcelado = 0
        else:
            parcela_strut = container.find("span",{"class":"bui-price__installment"}).text.strip().split("R$")
            vezes = tira_num_do_texto(parcela_strut[0])
            parcela = tira_num_do_texto(parcela_strut[1])
            total_parcelado = vezes*parcela
        desconto = 0
        for item in container.span['class']:
            if 'discount' in item:
                desconto = tira_num_do_texto(container.span.text.strip())
                break
        dados_cru = dados_cru + [{'nome':nome,'preço':preco,'em até':vezes,
                                  'parcela':parcela,'total parcelado':total_parcelado,
                                  'desconto':desconto}]
    print("\rPágina %d de %d - %.2f%%"%(i,max_pag,(i*100)/max_pag),end='')
    
dados = pd.DataFrame(dados_cru)
dados = dados[['nome','preço','desconto','em até','parcela','total parcelado']]

nome_csv = "resultados_"
for w in busca.split(" "):
    nome_csv=nome_csv+w+"_"
nome_csv=nome_csv[:-1]+".csv"
print("\n\nSalvando resultados em %s\\%s"%(os.getcwd(),nome_csv))
dados.to_csv(nome_csv,sep=',',index=False,encoding='latin-1')