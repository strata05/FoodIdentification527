from cachetools import cached, LRUCache
from loguru import logger

from dao.user_dao import find_user_by_id


user_cache = LRUCache(maxsize=1000)

def get_user(user_id: str):
    """

    :param user_id:
    :return:
    """
    if user_id in user_cache:
        return user_cache[user_id]

    logger.info(f'get user from db: {user_id}')
    user = find_user_by_id(user_id)
    print("user", user)
    if user is None:
        return None

    user_cache[user_id] = user
    return user
