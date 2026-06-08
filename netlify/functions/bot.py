import json
import requests
import cloudinary
import cloudinary.uploader

# 1. Configure Cloudinary
cloudinary.config(
    cloud_name = "dqo0lzmxz",
    api_key = "491698922393677",
    api_secret = "F3AGusYkyYB8OQbKLTqjylJAE8g",
    secure = True
)

# 2. Telegram Token
BOT_TOKEN = "8774471674:AAHV866bcL71zN0yNTrSSJA1uwc4rBUg9qc"

def handler(event, context):
    if event.get('httpMethod') == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            
            if 'message' in body and ('photo' in body['message'] or 'video' in body['message']):
                message = body['message']
                chat_id = message['chat']['id']
                
                if 'photo' in message:
                    file_id = message['photo'][-1]['file_id']
                    media_type = "photo"
                    resource_type = "image"
                else:
                    file_id = message['video']['file_id']
                    media_type = "video"
                    resource_type = "video"

                # Get file download path from Telegram
                file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                file_info = requests.get(file_info_url).json()
                
                if 'result' in file_info and 'file_path' in file_info['result']:
                    remote_file_path = file_info['result']['file_path']
                    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{remote_file_path}"

                    # Stream to Cloudinary
                    upload_result = cloudinary.uploader.upload(download_url, resource_type=resource_type)
                    cloudinary_url = upload_result.get("secure_url")

                    # Reply to Telegram chat
                    caption_text = f"✅ Done upload to the cloudinary\n🔗 Here is link: {cloudinary_url}"
                    
                    payload = {
                        'chat_id': chat_id,
                        media_type: file_id,
                        'caption': caption_text
                    }
                    
                    telegram_endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/send{media_type.capitalize()}"
                    requests.post(telegram_endpoint, data=payload)
                    
        except Exception as e:
            print(f"Serverless Function Error: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'success'})
    }
