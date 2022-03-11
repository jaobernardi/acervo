import pyding
from lib import tweet_utils

@pyding.on("direct_message")
def direct_message_handler(event, message, meta, sender_id, user, data):
    tweet_utils.send_dms(sender_id, text="🔮 — Sua mensagem foi recebida mas não há nenhum serviço disponível para processá-la.")
