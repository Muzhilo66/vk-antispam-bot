from flask import Flask, request
import requests

app = Flask(__name__)

VK_SECRET = 'your_vk_secret'
CONFIRMATION_TOKEN = 'your_confirmation_token'
ACCESS_TOKEN = 'your_group_access_token'
GROUP_ID = 'your_group_id'

blacklist = {
    'оскорбления': [
        'тупой', 'уебан', 'мразь', 'долбоёб', 'идиот', 'дебил', 'чмо', 'пидор', 'шлюха',
        'ублюдок', 'петух', 'гандон', 'хохол', 'кацап', 'петух', 'пидар', 'ебанат'
    ],
    'реклама/спам': [
        'подпишись', 'добавляйся', 'зайди в паблик', 'подписывайся', 'инстаграм', 'ссылка в био',
        'прямо сейчас', 'бесплатно', 'жми сюда', 'акция', 'казино', '1xбет', 'ставки',
        'вулкан', 'азино', '777', 'mefedron', 'mdma', 'купи закладку', 'работа 18+',
        'хайп проект', 'заработок без вложений'
    ],
    'нацизм и политика': [
        'загнивающий запад', 'тупой совок', 'совок сдох', 'русня', 'рашка', 'путин хуйло',
        'сталин убийца', 'советская мразь', 'деды воевали зря', 'зомби россияне', 'слава украине',
        'heil hitler', 'жиды', 'евреи у власти', 'план даллеса', 'сатанисты в кремле', 'сатанинский режим'
    ],
    'мат': [
        'нахуй', 'пиздец', 'ебать', 'хуесос', 'хуй', 'блядь', 'ёбаный', 'сука', 'еблан'
    ]
}

all_blacklisted_keywords = set()
for category in blacklist.values():
    all_blacklisted_keywords.update(category)

def vk_api(method, params):
    params['access_token'] = ACCESS_TOKEN
    params['v'] = '5.199'
    return requests.post(f'https://api.vk.com/method/{method}', data=params).json()

@app.route('/vk-callback', methods=['POST'])
def vk_callback():
    data = request.get_json()

    if data.get('type') == 'confirmation':
        return CONFIRMATION_TOKEN

    if data.get('secret') != VK_SECRET:
        return 'invalid secret', 403

    if data.get('type') == 'message_new':
        message = data['object']['message']
        text = message.get('text', '').lower()
        user_id = message.get('from_id')
        if any(word in text for word in all_blacklisted_keywords):
            vk_api('groups.ban', {'group_id': GROUP_ID, 'owner_id': user_id})

    elif data.get('type') == 'wall_reply_new':
        comment = data['object']
        text = comment.get('text', '').lower()
        user_id = comment.get('from_id')
        comment_id = comment.get('id')
        if any(word in text for word in all_blacklisted_keywords):
            vk_api('wall.deleteComment', {'owner_id': f"-{GROUP_ID}", 'comment_id': comment_id})
            vk_api('groups.ban', {'group_id': GROUP_ID, 'owner_id': user_id})

    return 'ok'

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

