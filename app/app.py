import requests
from bs4 import BeautifulSoup
import schedule
import time
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
RECIPIENT_PHONE_NUMBER = os.getenv('RECIPIENT_PHONE_NUMBER')


client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
should_request_new_url = [False] 



def scrape_price(url, old_price, retry_count=0):
	response = requests.get(url)
	if response.status_code != 200:
		if retry_count < 3:
			time.sleep(10)
			return scrape_price(url, old_price, retry_count + 1)
		else:
			handle_error(f"Échec définitif après plusieurs tentatives : {response.status_code}")
			return

	soup = BeautifulSoup(response.content, 'lxml')
	price_element = soup.find('button', {'class': "sc-168a3b5-5 dHyqgD"})
	product_name_element = soup.find('h1', {'class': "sc-12fcbcc6-0 kHeaGZ"})

	if price_element is None or product_name_element is None:
		handle_error(f"Le produit {product_name_element.text if product_name_element else 'inconnu'} n'a pas de prix ou n'est plus disponible")
		return

	price = parse_price(price_element.text)
	product_name = product_name_element.text
	if price < old_price[0]:
		send_price_drop_notification(product_name, old_price[0], price)
		old_price[0] = price
	else:
		old_price[0] = price
		print('Ancien prix =', old_price[0])
		print('Prix non en baisse')

def handle_error(message):
	print(message)
	send_whatsapp(f'Digibot :\n\n❗️ {message} ❗️')
	should_request_new_url[0] = True 

def send_price_drop_notification(product_name, old_price, new_price):
	send_whatsapp(f'Digibot :\n\n🎉🎊 Le prix de *{product_name}* baisse! 🎊🎉\nIl passe de {old_price}.- CHF a {new_price}.- CHF')


def parse_price(price_string):
	print(f'\nPrix actuel = {price_string}')
	cleaned_price = price_string.replace('.–', '').replace('CHF', '').strip()
	return float(cleaned_price.replace('\'', '').replace(',', '.'))

def send_whatsapp(message):
	message = client.messages.create(
		body=message,
		from_=TWILIO_PHONE_NUMBER,
		to=RECIPIENT_PHONE_NUMBER
	)
	print(f'\nSMS sent: {message.sid}')

def main():
	while True:
		url = input("Entrez l'URL du produit : ")
		interval = int(input("Entrez l'intervalle de temps en minutes avant de rechercher de nouveau : "))
		
		old_price = [(0)]

		schedule.clear()
		schedule.every(interval).seconds.do(lambda: scrape_price(url, old_price))
		
		try:
			while True:
				schedule.run_pending()
				time.sleep(1)
				if should_request_new_url[0]:
					should_request_new_url[0] = False
					print("Une erreur nécessitant une nouvelle URL a été rencontrée.")
					break
		except KeyboardInterrupt:
			print("Arrêté par l'utilisateur.")
			break


if __name__ == "__main__":
	main()