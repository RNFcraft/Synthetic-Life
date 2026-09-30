import json
import base64
import pickle
import subprocess
import sys
from random import Random

import pytest

from persistence import ContainerError, inspect_container
from simulation.snapshot import decode_random_state, encode_random_state
from simulation import Simulation
from simulation.snapshot import save_snapshot


def test_rng_json_round_trip_is_exact():
    source = Random(812)
    source.random()
    payload = encode_random_state(source.getstate())
    assert payload["encoding"] == "python-random-json-v1"
    assert "pickle" not in json.dumps(payload).lower()
    restored = Random()
    restored.setstate(decode_random_state(payload))
    assert [source.random() for _ in range(20)] == [restored.random() for _ in range(20)]


def test_rng_gaussian_cache_round_trip_is_exact():
    source=Random(912)
    source.gauss(0.,1.)
    restored=Random()
    restored.setstate(decode_random_state(encode_random_state(source.getstate())))
    assert [source.gauss(0.,1.) for _ in range(10)]==[restored.gauss(0.,1.) for _ in range(10)]


@pytest.mark.parametrize("payload", ["gASV", {}, {"encoding": "pickle", "state": []}, {"encoding": "python-random-json-v1", "state": [3, [], None]}])
def test_unsafe_or_malformed_rng_payload_fails_closed(payload):
    with pytest.raises(ValueError):
        decode_random_state(payload)


@pytest.mark.parametrize("raw", [b"", b"SEWORLD1", b"SEWORLD1\x00\x01\x00\x01\xff\xff\xff\xff", b"SEWORLD1\x00\x01\x00\x01\x00\x00\x00\x02{}"])
def test_inspect_container_normalizes_corruption(raw, tmp_path):
    path = tmp_path / "bad.seworld"
    path.write_bytes(raw)
    with pytest.raises(ContainerError):
        inspect_container(path)


def test_pickle_payload_is_never_executed_by_normal_snapshot_loader(tmp_path):
    marker=tmp_path / "executed"

    class Evil:
        def __reduce__(self):
            return (marker.write_text, ("unsafe",))

    state=Simulation(99).snapshot_data()
    state["random_state"]=base64.b64encode(pickle.dumps(Evil())).decode("ascii")
    path=tmp_path / "unsafe.json"
    save_snapshot(state,path)
    with pytest.raises(ValueError,match="unsafe or unsupported RNG"):
        Simulation.load(path)
    assert not marker.exists()


def test_persistence_info_cli_reports_corruption_as_container_error(tmp_path):
    path=tmp_path / "truncated.seworld"
    path.write_bytes(b"SEWORLD1")
    result=subprocess.run([sys.executable,"-m","persistence.info",str(path)],capture_output=True,text=True)
    assert result.returncode!=0
    assert "ContainerError: truncated container header" in result.stderr
    assert "struct.error" not in result.stderr
