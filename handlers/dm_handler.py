import logging
import pyding
from lib import tweet_utils, config, archive_utils, database
from datetime import date, datetime

@pyding.on("direct_message")
def direct_message_handler(event, message, meta, sender_id, user, quick_reply, data):
    if sender_id == config.get_id():
        return

    logging.info(f"[{user['screen_name']}] :: {message}")
    if quick_reply:
        match quick_reply['metadata'].split(":"):
            case ["requests", "approved", uuid]:
                success = archive_utils.accept_inclusion_entry(uuid)
                if success:
                    now = datetime.now().strftime("%H horas e %M minuto(s)")
                    tweet_utils.send_dms(config.get_admin(), text=f"🔮 — A solicitação de identificador único “{uuid}” foi aprovada às {now}.")
                else:
                    request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                    tweet_utils.send_dms(sender_id, text=f"⛔️ — A solicitação de identificador único “{uuid}” está com o status de Aprovada, portanto não pode ser processada novamente.")

                
            case ['requests', 'reject', uuid]:
                database.edit_request(uuid, "Rejeitada")
                request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                now = datetime.now().strftime("%H horas e %M minuto(s)")
                tweet_utils.send_dms(config.get_admin(), text=f"🔮 — A solicitação de identificador único “{uuid}” foi rejeitada às {now}.")
                tweet_utils.send_dms(user_id, text=f"📛 — A sua solicitação foi rejeitada pela moderação.\nhttps://twitter.com/{user_id}/status/{tweet_id}")
        
            case ['requests', 'see', uuid]:
                request_uuid, request_status, tweet_id, user_id, *extra = database.get_request(uuid)[0]
                tweet_utils.send_dms(sender_id, text=f"🔮 — A solicitação de identificador único “{uuid}” está com o status de: {request_status}")
    
    if message.lower() == "qual a situação dos meus pedidos?":
        requests = database.get_request(user_id=sender_id)
        if requests:
            tweet_utils.send_dms(sender_id, text=f"🔮 — Você tem os seguintes pedidos:")
            for request in requests:
                request_uuid, request_status, tweet_id, user_id, tweet_text, tweet_media, tweet_meta, timestamp = request
                tweet_utils.send_dms(sender_id, text=f"🔮 — Pedido número {request_uuid}\nSituação: {request_status}\nhttps://twitter.com/{user['screen_name']}/status/{tweet_id}")
        else:
            tweet_utils.send_dms(sender_id, text=f"🔮 — Você não tem pedidos registrados.")
    