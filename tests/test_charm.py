# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module testing the Legend Engine Operator."""

import json
from unittest import mock

from charms.finos_legend_libs.v0 import legend_operator_base, legend_operator_testing
from ops import testing as ops_testing

import charm


class LegendEngineTestWrapper(charm.LegendEngineServerCharm):
    @classmethod
    def _get_relations_test_data(cls):
        return {
            cls._get_legend_db_relation_name(): {
                "legend-db-connection": json.dumps(
                    {
                        "username": "test_db_user",
                        "password": "test_db_pass",
                        "database": "test_db_name",
                        "uri": "test_db_uri",
                    }
                )
            },
            cls._get_legend_gitlab_relation_name(): {
                "legend-gitlab-connection": json.dumps(
                    {
                        "gitlab_host": "gitlab_test_host",
                        "gitlab_port": 7667,
                        "gitlab_scheme": "https",
                        "client_id": "test_client_id",
                        "client_secret": "test_client_secret",
                        "openid_discovery_url": "test_discovery_url",
                        "gitlab_host_cert_b64": "test_gitlab_cert",
                    }
                )
            },
        }

    def _get_service_configs_clone(self, relation_data):
        return {}


class LegendEngineTestCase(legend_operator_testing.TestBaseFinosCoreServiceLegendCharm):
    @classmethod
    def _set_up_harness(cls):
        harness = ops_testing.Harness(LegendEngineTestWrapper)
        return harness

    def test_get_core_legend_service_configs(self):
        self._test_get_core_legend_service_configs()

    def test_relations_waiting(self):
        self._test_relations_waiting()

    def test_studio_relation_joined(self):
        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

        relator_name = "finos-legend-studio-k8s"
        rel_id = self.harness.add_relation(charm.LEGEND_STUDIO_RELATION_NAME, relator_name)
        relator_unit = "%s/0" % relator_name
        self.harness.add_relation_unit(rel_id, relator_unit)
        self.harness.update_relation_data(rel_id, relator_unit, {})

        rel = self.harness.charm.framework.model.get_relation(
            charm.LEGEND_STUDIO_RELATION_NAME, rel_id
        )
        self.assertEqual(
            rel.data[self.harness.charm.app],
            {"legend-engine-url": self.harness.charm._get_engine_service_url()},
        )

    @mock.patch.object(legend_operator_base, "get_ip_address")
    def test_get_legend_gitlab_redirect_uris(self, mock_get_ip_address):
        self.harness.begin()
        mock_get_ip_address.return_value = "fake_ip"
        actual_uris = self.harness.charm._get_legend_gitlab_redirect_uris()

        expected_url = "http://fake_ip:6060/callback"
        self.assertEqual([expected_url], actual_uris)

    def test_upgrade_charm(self):
        self._test_upgrade_charm()
