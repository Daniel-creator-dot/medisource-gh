from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    scope = "auth"


class AuthUserRateThrottle(UserRateThrottle):
    scope = "auth"
