#  Copyright 2016-2024. Couchbase, Inc.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License")
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from typing import Callable, Dict

from couchbase_columnar.common.exceptions import InvalidArgumentException


class Credential:
    def __init__(self, **kwargs: str) -> None:
        username = kwargs.pop('username', None)
        password = kwargs.pop('password', None)

        if username is None:
            raise InvalidArgumentException('Must provide a username.')
        if not isinstance(username, str):
            raise InvalidArgumentException('The username must be a str.')

        if password is None:
            raise InvalidArgumentException('Must provide a password.')
        if not isinstance(password, str):
            raise InvalidArgumentException('The password must be a str.')

        self._username = username
        self._password = password

    def asdict(self) -> Dict[str, str]:
        return {
            'username': self._username,
            'password': self._password
        }

    @classmethod
    def from_username_and_password(cls, username: str, password: str) -> Credential:
        return Credential(username=username, password=password)

    @classmethod
    def from_callable(cls, callback: Callable[[], Credential]) -> Credential:
        return Credential(**callback().asdict())
