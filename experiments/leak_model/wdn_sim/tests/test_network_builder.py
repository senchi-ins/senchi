"""Network builder tests."""
import wntr  # type: ignore

from src.network.builder import build_network_from_profile


def test_builder_outputs_network():
    wn = build_network_from_profile("modern_pex_small")
    assert isinstance(wn, wntr.network.WaterNetworkModel)
    # ensure key junctions exist
    for node in ["Municipal", "Manifold", "Kitchen"]:
        assert node in wn.node_name_list
