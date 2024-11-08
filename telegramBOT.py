import requests
import os
import pytesseract  
from PIL import Image

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.api_url = f'https://api.telegram.org/bot{token}/'
        self.file_api_url = f'https://api.telegram.org/file/bot{token}/'
    
    def send_photo(self, chat_id, photo_path, caption=''):
        url = f'{self.api_url}sendPhoto'
        files = {'photo': open(photo_path, 'rb')}
        data = {'chat_id': chat_id, 'caption': caption}
        response = requests.post(url, files=files, data=data)
        return response.json()

    def send_message(self, chat_id, text):
        url = f'{self.api_url}sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        response = requests.post(url, data=data)
        return response.json()

    def forward_message(self, chat_id, from_chat_id, message_id):
        url = f'{self.api_url}forwardMessage'
        data = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        response = requests.post(url, data=data)
        return response.json()

    def get_file_info(self, file_id):
        response = requests.get(f'{self.api_url}getFile?file_id={file_id}')
        return response.json()

    def download_file(self, file_path, local_path):
        file_url = f'{self.file_api_url}{file_path}'
        response = requests.get(file_url)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as file:
            file.write(response.content)
    
    def handle_updates(self):
        offset = 0
        while True:
            response = requests.get(f'{self.api_url}getUpdates?offset={offset}')
            updates = response.json()['result']
            if updates:
                for update in updates:
                    offset = update['update_id'] + 1
                    if 'message' in update:
                        self.process_message(update['message'])
    
    def process_message(self, message):
        chat_id = message['chat']['id']

        if 'document' in message:
            file_id = message['document']['file_id']
            file_info = self.get_file_info(file_id)
            file_path = file_info['result']['file_path']
            local_document_path = f'documents/{file_path.split("/")[-1]}'
            self.download_file(file_path, local_document_path)

            book_title = self.extract_book_title(local_document_path)
            cover_image_path = self.get_book_cover_path(book_title)

            self.send_photo(chat_id, cover_image_path)
            self.forward_message(chat_id, message['chat']['id'], message['message_id'])
        else:
            self.forward_message(chat_id, message['chat']['id'], message['message_id'])

    def extract_book_title(self, file_path):
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        extracted_title = text.split('\n')[0]
        return extracted_title

    def get_book_cover_path(self, book_title):
        cover_image_path = f'covers/{book_title}.jpg'
        return cover_image_path

if __name__ == "__main__":
    TOKEN = '7645023742:AAEDpQ72WvD4CSDbof6Difaw9mamb5_nroY'
    bot = TelegramBot(TOKEN)
    bot.handle_updates()
