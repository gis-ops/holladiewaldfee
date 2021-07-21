import os.path
import sys
from datetime import datetime
import time
import random
import json
import warnings
from qgis.core import QgsNetworkAccessManager, QgsNetworkReplyContent
from qgis.PyQt.QtCore import QUrl, QJsonDocument
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply

current_dir = os.path.dirname(os.path.abspath(__file__))
rp_path = os.path.join(current_dir, "../third_party", "routing-py")
sys.path.append(rp_path)

from routingpy.client_base import BaseClient, DEFAULT, _RETRIABLE_STATUSES
from routingpy.utils import get_ordinal
from routingpy import exceptions


class QClient(BaseClient):

    def __init__(
        self,
        base_url,
        user_agent=None,
        timeout=DEFAULT,
        retry_timeout=None,
        retry_over_query_limit=None,
        skip_api_error=None,
        **kwargs
    ):
        self.nam = QgsNetworkAccessManager()

        super(QClient, self).__init__(
            base_url,
            user_agent=user_agent,
            timeout=timeout,
            retry_timeout=retry_timeout,
            retry_over_query_limit=retry_over_query_limit,
            skip_api_error=skip_api_error,
            **kwargs
        )
        self.kwargs = kwargs or {}
        try:
            self.headers.update(self.kwargs["headers"])
        except KeyError:
            pass

        self.kwargs["headers"] = self.headers
        self.kwargs["timeout"] = self.timeout

    def _request(
        self,
        url,
        get_params={},
        post_params=None,
        first_request_time=None,
        retry_counter=0,
        dry_run=None,
    ):
        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise exceptions.Timeout()

        if retry_counter > 0:
            # 0.5 * (1.5 ^ i) is an increased sleep time of 1.5x per iteration,
            # starting at 0.5s when retry_counter=1. The first retry will occur
            # at 1, so subtract that first.
            delay_seconds = 1.5 ** (retry_counter - 1)
            # Jitter this value by 50% and pause.
            time.sleep(delay_seconds * (random.random() + 0.5))

        authed_url = self._generate_auth_url(url, get_params)
        # final_requests_kwargs = self.kwargs
        url_object = QUrl(self.base_url + authed_url)

        # Determine GET/POST
        requests_method = self.nam.blockingGet
        if post_params is not None:
            requests_method = self.nam.blockingPost
            # if final_requests_kwargs["headers"]["Content-Type"] == "application/json":
            #     final_requests_kwargs["json"] = post_params
            # else:
            #     # Send as x-www-form-urlencoded key-value pair string (e.g. Mapbox API)
            #     final_requests_kwargs["data"] = post_params

        # Only print URL and parameters for dry_run
        if dry_run:
            print(
                "url:\n{}\nParameters:\n{}\nMethod:\n{}".format(
                    self.base_url + authed_url, json.dumps(post_params, indent=2),
                    str(requests_method)
                )
            )
            print(QJsonDocument(post_params).toJson())
            return

        body = QJsonDocument.fromJson(json.dumps(post_params).encode())
        request = QNetworkRequest(url_object)
        request.setHeader(QNetworkRequest.ContentTypeHeader, self.kwargs["headers"]["Content-Type"])

        start = time.time()
        response: QgsNetworkReplyContent = requests_method(request, body.toJson())

        self.response_time = time.time() - start
        self._req = response.request()
        error_code = response.error()

        if error_code is not QNetworkReply.NoError:
            if error_code == QNetworkReply.TimeoutError:
                raise exceptions.Timeout("Request timed out.")

            tried = retry_counter + 1

            if error_code in _RETRIABLE_STATUSES:
                warnings.warn(
                    "Server down.\nRetrying for the {}{} time.".format(tried, get_ordinal(tried)),
                    UserWarning,
                )

                return self._request(url, get_params, post_params, first_request_time, retry_counter + 1)

        try:
            result = self._get_body(response)
            return result
        except exceptions.RouterApiError:
            if self.skip_api_error:
                warnings.warn(
                    "Router {} returned an API error with "
                    "the following message:\n{}".format(self.__class__.__name__, response.content())
                )
                return
            raise

    @property
    def req(self):
        """Holds the :class:`requests.PreparedRequest` property for the last request."""
        return self._req

    @staticmethod
    def _get_body(response):
        status_code = response.attribute(QNetworkRequest.HttpStatusCodeAttribute)

        try:
            body = json.loads(bytes(response.content()))
        except json.decoder.JSONDecodeError:
            raise exceptions.JSONParseError("Can't decode JSON response:{}".format(response.content()))

        if status_code == 429:
            raise exceptions.OverQueryLimit(status_code, body)

        if 400 <= status_code < 500:
            raise exceptions.RouterApiError(status_code, body)

        if 500 <= status_code:
            raise exceptions.RouterServerError(status_code, body)

        if status_code != 200:
            raise exceptions.RouterError(status_code, body)

        return body


