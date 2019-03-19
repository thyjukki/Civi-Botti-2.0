class InvalidAuthKey(Exception):
    """Invalid authentication key"""
    pass


class GameNoLongerExist(Exception):
    """Game does not exist anymore"""
    pass


class GameNoSubscriptions(Exception):
    """Game does not have any subscriptions"""
    pass
