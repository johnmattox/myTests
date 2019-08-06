from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card'

# Abre c onexão e baixa HTML da página
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

# Transforma HTML em obejto beautifulsoup
page_soup = soup(page_html, "html.parser")
# Agora é possível navegar no HTML da página
# por exemplo page_soup.h1 me dá o header dela

# Usando "inspect" no chrome, percebemos que os itens que
# queremos raspar estão dentro de "divs" da classe "item-container".
# usamos isso na função findAll do objeto soup
containers = page_soup.findAll("div",{"class":"item-container"})

# Para cada container, vemos que há uma imagem com o nome da marca da placa,
# pode haver um rating, o nome da placa, pode haver um preço, um frete...

container = containers[0]
# A marca, extraida da imagem com logo da marca, pode ser obtida assim:
marca = container.findAll("div",{"class":"item-branding"})[0].a.img["title"]

# Fechando o loop e pegando outras informações:

for container in containers:
	# pega a marca, que é o campo 'title' do objeto img da tag a da div classe 'item-branding':
	marca = container.findAll("div",{"class":"item-branding"})[0].a.img["title"]
	# pega o nome, que é o texto da tag a classe 'item-tite' (não é um campo):
	nome = container.findAll("a",{"class":"item-title"})[0].text
	# pega o frete (e já limpa o texto usando strip):
	frete = container.findAll("li",{"class":"price-ship"})[0].text.strip()
	
	print("Placa {} da marca {} possui frete: {}".format(nome,marca,frete))
