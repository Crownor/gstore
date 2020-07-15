# coding=utf-8

from guniflask.context import configuration
from guniflask.config import settings
from guniflask.security_config import WebSecurityConfigurer, HttpSecurity, enable_web_security


@configuration
@enable_web_security
class SecurityConfiguration(WebSecurityConfigurer):

    def configure_http(self, http: HttpSecurity):
        cors = settings.get_by_prefix('guniflask.cors')
        if cors:
            http.cors(cors)
