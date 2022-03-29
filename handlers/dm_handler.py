import logging
from time import sleep
import pyding
from urllib.parse import urlparse
from lib import tweet_utils, config, archive_utils, database, auth
from datetime import date, datetime


user_data = {}


@pyding.on("direct_message")
def direct_message_handler(event, message, meta, sender_id, user, quick_reply, data):
    if sender_id == config.get_id():
        return   

    logging.info(f"[{user['screen_name']}] :: {message}")

    for url in meta['urls']:
        message = message.replace(url['url'], '', 1)
        parsed_url = urlparse(url['expanded_url'])
        if parsed_url.netloc == "twitter.com":
            match parsed_url.path.split("/"):
                case ["", tweet_author, "status", id]:
                    if int(sender_id) in config.get_admin():
                        category, description, text, flags = archive_utils.parse_title(message)
                        archived = archive_utils.archive_media(None, int(sender_id), id, category, description, flags)
                        tweet_utils.send_dms(sender_id, text=f"🔮 — Esta mídia foi incluída no acervo sob a categoria '{category}'. https://twitter.com/arquivodojao/status/{archived.data['id']}")

 
    if sender_id in user_data and 'editing_request' in user_data[sender_id] and user_data[sender_id]['editing_request']:
        user_data[sender_id]['editing_request'] = False
        success = archive_utils.accept_inclusion_entry(user_data[sender_id]['uuid'], message)
        if success:
            now = datetime.now().strftime("%H horas e %M minuto(s)")
            tweet_utils.send_dms(config.get_admin(), text=f"🔮 — A solicitação de identificador único “{user_data[sender_id]['uuid']}” foi aprovada às {now}.")
        else:
            request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(user_data[sender_id]['uuid'])[0]
            tweet_utils.send_dms(sender_id, text=f"⛔️ — A solicitação de identificador único “{user_data[sender_id]['uuid']}” está com o status de {request_status}, portanto não pode ser processada novamente.")
        

    elif quick_reply:
        match quick_reply['metadata'].split(":"):
            case ["requests", "approved", "edit", uuid]:
                user_data[sender_id] = {"editing_request": True, "uuid": uuid}
                tweet_utils.send_dms(sender_id, text=f"📥 — Envie o novo título. (O pedido será processado e será dado como aceito)")

            case ["requests", "approved", uuid]:
                success = archive_utils.accept_inclusion_entry(uuid)
                if success:
                    now = datetime.now().strftime("%H horas e %M minuto(s)")
                    tweet_utils.send_dms(config.get_admin(), text=f"🔮 — A solicitação de identificador único “{uuid}” foi aprovada às {now}.")
                else:
                    request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                    tweet_utils.send_dms(sender_id, text=f"⛔️ — A solicitação de identificador único “{uuid}” está com o status de {request_status}, portanto não pode ser processada novamente.")
                
            case ['requests', 'reject', uuid]:
                database.edit_request(uuid, "Rejeitada")
                request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                now = datetime.now().strftime("%H horas e %M minuto(s)")
                tweet_utils.send_dms(config.get_admin(), text=f"🔮 — A solicitação de identificador único “{uuid}” foi rejeitada às {now}.")
        
            case ['requests', 'see', uuid]:
                request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                tweet_utils.send_dms(sender_id, text=f"🔮 — A solicitação de identificador único “{uuid}” está com o status de: {request_status}")
    
    elif message.lower() == "qual a situação dos meus pedidos?":
        requests = database.get_request(user_id=sender_id)
        if requests:
            tweet_utils.send_dms(sender_id, text=f"🔮 — Você tem os seguintes pedidos:")
            for request in requests:
                request_uuid, request_status, tweet_id, user_id, tweet_text, tweet_media, tweet_meta, timestamp = request
                tweet_utils.send_dms(sender_id, text=f"🔮 — Pedido número {request_uuid}\nSituação: {request_status}\nhttps://twitter.com/{user['screen_name']}/status/{tweet_id}")
        else:
            tweet_utils.send_dms(sender_id, text=f"🔮 — Você não tem pedidos registrados.")
    