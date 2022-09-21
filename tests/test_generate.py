from pathlib import Path

import pytest
import yaml
from prefect.utilities.importtools import import_object

TEST_DIR = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def processed_schema():
    path = TEST_DIR / "mock_schema.yaml"
    with open(path, "r") as f:
        mock_schema = yaml.safe_load(f)

    generate_path = TEST_DIR / ".." / "scripts" / "generate.py"
    preprocess_fn = import_object(f"{generate_path}:preprocess_fn")
    processed_schema = preprocess_fn(mock_schema)
    return processed_schema


class TestPreprocessFn:
    def test_node_type_id(self, processed_schema):
        new_cluster = processed_schema["components"]["schemas"]["NewCluster"]
        node_type_id = new_cluster["properties"]["node_type_id"]
        node_type_id_description = node_type_id["description"]
        # description should be updated
        assert node_type_id_description.endswith("`instance_pool_id` is specified.")
        # node_type_id should be deleted from required
        assert new_cluster["required"] == ["spark_version"]

    def test_force_required_into_list(self, processed_schema):
        new_cluster = processed_schema["components"]["schemas"]["GitSource"]
        git_provider = new_cluster["properties"]["git_provider"]
        assert git_provider["required"] == [True]

    def test_items_to_have_type(self, processed_schema):
        new_cluster = processed_schema["components"]["schemas"]["GitSource"]
        totally_made_up = new_cluster["properties"]["totally_made_up"]
        assert totally_made_up["items"] == {"type": "imagination"}
