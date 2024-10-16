#  Copyright 2016-2024. Couchbase, Inc.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
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

from datetime import timedelta
from typing import Dict

import pytest

from couchbase_columnar.credential import Credential
from couchbase_columnar.deserializer import DefaultJsonDeserializer
from couchbase_columnar.options import (ClusterOptions,
                                        IpProtocol,
                                        SecurityOptions,
                                        TimeoutOptions)
from couchbase_columnar.protocol.core.client_adapter import _ClientAdapter
from tests.columnar_config import CONFIG_FILE


class ClusterOptionsTestSuite:
    # TODO: Do we keep thsees?
    # disable_mozilla_ca_certificates: Optional[bool]
    # enable_dns_srv: Optional[bool] - removed w/ PYCO-
    # enable_metrics: Optional[bool]
    # enable_tracing: Optional[bool]
    # logging_meter_emit_interval: Optional[timedelta]
    # log_redaction: Optional[bool]
    # tracing_options: Optional[TracingOptionsBase]

    TEST_MANIFEST = [
        'test_options',
        'test_options_kwargs',
        'test_options_deserializer',
        'test_options_deserializer_kwargs',
        'test_security_options',
        'test_security_options_kwargs',
        'test_timeout_options',
        'test_timeout_options_kwargs',
    ]

    @pytest.mark.parametrize('opts, expected_opts',
                             [({'allow_unknown_qstr_options': True},
                               {}),
                              ({'config_poll_floor': timedelta(seconds=5)},
                               {'config_poll_floor': 5000000}),
                              ({'config_poll_interval': timedelta(seconds=5)},
                               {'config_poll_interval': 5000000}),
                              ({'dns_nameserver': '127.0.0.1'},
                               {'dns_nameserver': '127.0.0.1'}),
                              ({'dns_port': 1053},
                               {'dns_port': 1053}),
                              ({'dump_configuration': True},
                               {'dump_configuration': True}),
                              ({'enable_clustermap_notification': False},
                               {'enable_clustermap_notification': False}),
                              ({'ip_protocol': IpProtocol.ForceIPv6},
                               {'use_ip_protocol': IpProtocol.ForceIPv6.value}),
                              ({'network': 'external'},
                               {'network': 'external'}),
                              ({'config_poll_interval': timedelta(seconds=5),
                                'dns_nameserver': '127.0.0.1',
                                'dns_port': 1053,
                                'dump_configuration': True,
                                'ip_protocol': IpProtocol.ForceIPv6,
                                'network': 'external'},
                               {'config_poll_interval': 5000000,
                                'dns_nameserver': '127.0.0.1',
                                'dns_port': 1053,
                                'dump_configuration': True,
                                'use_ip_protocol': IpProtocol.ForceIPv6.value,
                                'network': 'external'}),
                              ])
    def test_options(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost', cred, ClusterOptions(**opts))
        # pop user_agent as that is additive
        client.connection_details.cluster_options.pop('user_agent_extra', None)
        assert expected_opts == client.connection_details.cluster_options

    @pytest.mark.parametrize('opts, expected_opts',
                             [({}, {}),
                              ({'allow_unknown_qstr_options': True},
                               {}),
                              ({'config_poll_floor': timedelta(seconds=5)},
                               {'config_poll_floor': 5000000}),
                              ({'config_poll_interval': timedelta(seconds=5)},
                               {'config_poll_interval': 5000000}),
                              ({'dns_nameserver': '127.0.0.1'},
                               {'dns_nameserver': '127.0.0.1'}),
                              ({'dns_port': 1053},
                               {'dns_port': 1053}),
                              ({'dump_configuration': True},
                               {'dump_configuration': True}),
                              ({'enable_clustermap_notification': False},
                               {'enable_clustermap_notification': False}),
                              ({'ip_protocol': IpProtocol.ForceIPv6},
                               {'use_ip_protocol': IpProtocol.ForceIPv6.value}),
                              ({'network': 'external'},
                               {'network': 'external'}),
                              ({'config_poll_interval': timedelta(seconds=5),
                                'dns_nameserver': '127.0.0.1',
                                'dns_port': 1053,
                                'dump_configuration': True,
                                'ip_protocol': IpProtocol.ForceIPv6,
                                'network': 'external'},
                               {'config_poll_interval': 5000000,
                                'dns_nameserver': '127.0.0.1',
                                'dns_port': 1053,
                                'dump_configuration': True,
                                'use_ip_protocol': IpProtocol.ForceIPv6.value,
                                'network': 'external'}),
                              ])
    def test_options_kwargs(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost', cred, **opts)
        # pop user_agent as that is additive
        client.connection_details.cluster_options.pop('user_agent_extra', None)
        assert expected_opts == client.connection_details.cluster_options

    def test_options_deserializer(self) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        default_deserializer = DefaultJsonDeserializer()
        client = _ClientAdapter('couchbases://localhost', cred, ClusterOptions(deserializer=default_deserializer))
        assert default_deserializer == client.connection_details.default_deserializer

    def test_options_deserializer_kwargs(self) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        default_deserializer = DefaultJsonDeserializer()
        client = _ClientAdapter('couchbases://localhost', cred, **{'deserializer': default_deserializer})
        assert default_deserializer == client.connection_details.default_deserializer

    @pytest.mark.parametrize('opts, expected_opts',
                             [({}, None),
                              ({'trust_only_capella': True},
                               {'trust_only_capella': True}),
                              ({'trust_only_pem_file': CONFIG_FILE},
                               {'trust_only_pem_file': CONFIG_FILE}),
                              ({'trust_only_pem_str': 'BEGIN CERTIFICATIE...'},
                               {'trust_only_pem_str': 'BEGIN CERTIFICATIE...'}),
                              ({'trust_only_certificates': ['BEGIN CERTIFICATIE...', 'BEGIN CERTIFICATIE...']},
                               {'trust_only_certificates': ['BEGIN CERTIFICATIE...', 'BEGIN CERTIFICATIE...']}),
                              ({'verify_server_certificate': False},
                               {'verify_server_certificate': False}),
                              ({'cipher_suites': ['TLS_AES_256_GCM_SHA384',
                                                  'TLS_CHACHA20_POLY1305_SHA256',
                                                  'TLS_AES_128_GCM_SHA256']},
                               {'cipher_suites': ['TLS_AES_256_GCM_SHA384',
                                                  'TLS_CHACHA20_POLY1305_SHA256',
                                                  'TLS_AES_128_GCM_SHA256']}),
                              ])
    def test_security_options(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost',
                                cred,
                                ClusterOptions(security_options=SecurityOptions(**opts)))
        assert expected_opts == client.connection_details.cluster_options.get('security_options')

    @pytest.mark.parametrize('opts, expected_opts',
                             [({}, None),
                              ({'trust_only_capella': True},
                               {'trust_only_capella': True}),
                              ({'trust_only_pem_file': CONFIG_FILE},
                               {'trust_only_pem_file': CONFIG_FILE}),
                              ({'trust_only_pem_str': 'BEGIN CERTIFICATIE...'},
                               {'trust_only_pem_str': 'BEGIN CERTIFICATIE...'}),
                              ({'trust_only_certificates': ['BEGIN CERTIFICATIE...', 'BEGIN CERTIFICATIE...']},
                               {'trust_only_certificates': ['BEGIN CERTIFICATIE...', 'BEGIN CERTIFICATIE...']}),
                              ({'verify_server_certificate': False},
                               {'verify_server_certificate': False}),
                              ({'cipher_suites': ['TLS_AES_256_GCM_SHA384',
                                                  'TLS_CHACHA20_POLY1305_SHA256',
                                                  'TLS_AES_128_GCM_SHA256']},
                               {'cipher_suites': ['TLS_AES_256_GCM_SHA384',
                                                  'TLS_CHACHA20_POLY1305_SHA256',
                                                  'TLS_AES_128_GCM_SHA256']}),
                              ])
    def test_security_options_kwargs(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost', cred, **opts)
        assert expected_opts == client.connection_details.cluster_options.get('security_options')

    @pytest.mark.parametrize('opts, expected_opts',
                             [({}, None),
                              ({'connect_timeout': timedelta(seconds=30)},
                               {'bootstrap_timeout': 30000000}),
                              ({'dispatch_timeout': timedelta(seconds=30)},
                               {'dispatch_timeout': 30000000}),
                              ({'dns_srv_timeout': timedelta(seconds=30)},
                               {'dns_srv_timeout': 30000000}),
                              ({'management_timeout': timedelta(seconds=30)},
                               {'management_timeout': 30000000}),
                              ({'query_timeout': timedelta(seconds=30)},
                               {'analytics_timeout': 30000000}),
                              ({'resolve_timeout': timedelta(seconds=30)},
                               {'resolve_timeout': 30000000}),
                              ({'socket_connect_timeout': timedelta(seconds=30)},
                               {'connect_timeout': 30000000}),
                              ({'connect_timeout': timedelta(seconds=60),
                                'dispatch_timeout': timedelta(seconds=5),
                                'query_timeout': timedelta(seconds=30)},
                               {'bootstrap_timeout': 60000000,
                               'dispatch_timeout': 5000000,
                                'analytics_timeout': 30000000}),
                              ])
    def test_timeout_options(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost',
                                cred,
                                ClusterOptions(timeout_options=TimeoutOptions(**opts)))
        assert expected_opts == client.connection_details.cluster_options.get('timeout_options')

    @pytest.mark.parametrize('opts, expected_opts',
                             [({'connect_timeout': timedelta(seconds=30)},
                               {'bootstrap_timeout': 30000000}),
                              ({'dispatch_timeout': timedelta(seconds=30)},
                               {'dispatch_timeout': 30000000}),
                              ({'dns_srv_timeout': timedelta(seconds=30)},
                               {'dns_srv_timeout': 30000000}),
                              ({'management_timeout': timedelta(seconds=30)},
                               {'management_timeout': 30000000}),
                              ({'query_timeout': timedelta(seconds=30)},
                               {'analytics_timeout': 30000000}),
                              ({'resolve_timeout': timedelta(seconds=30)},
                               {'resolve_timeout': 30000000}),
                              ({'socket_connect_timeout': timedelta(seconds=30)},
                               {'connect_timeout': 30000000}),
                              ({'connect_timeout': timedelta(seconds=60),
                                'dispatch_timeout': timedelta(seconds=5),
                                'query_timeout': timedelta(seconds=30)},
                               {'bootstrap_timeout': 60000000,
                               'dispatch_timeout': 5000000,
                                'analytics_timeout': 30000000}),
                              ])
    def test_timeout_options_kwargs(self, opts: Dict[str, object], expected_opts: Dict[str, object]) -> None:
        cred = Credential.from_username_and_password('Administrator', 'password')
        client = _ClientAdapter('couchbases://localhost', cred, **opts)
        assert expected_opts == client.connection_details.cluster_options.get('timeout_options')


class ClusterOptionsTests(ClusterOptionsTestSuite):

    @pytest.fixture(scope='class', autouse=True)
    def validate_test_manifest(self) -> None:
        def valid_test_method(meth: str) -> bool:
            attr = getattr(ClusterOptionsTests, meth)
            return callable(attr) and not meth.startswith('__') and meth.startswith('test')
        method_list = [meth for meth in dir(ClusterOptionsTests) if valid_test_method(meth)]
        test_list = set(ClusterOptionsTestSuite.TEST_MANIFEST).symmetric_difference(method_list)
        if test_list:
            pytest.fail(f'Test manifest invalid.  Missing/extra tests: {test_list}.')
