"""Historical native v3/v4 bytes are fixtures, not rewritten current saves."""
import base64
import hashlib
import json
from pathlib import Path
import pytest
from consciousness._native_brain import NativeBrainEngine


@pytest.mark.parametrize('version',[3,4])
def test_historical_raw_layout_load_canonical_save_reload_semantics(tmp_path,version):
    fixture=json.loads((Path(__file__).parent/'fixtures/native_brain_d173280.json').read_text(encoding='utf-8'))
    row=next(row for row in fixture['records'] if row['version']==version)
    data=base64.b64decode(row['data'])
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    old=tmp_path/'historical.native';canonical=tmp_path/'canonical.native'
    old.write_bytes(data)
    a=NativeBrainEngine();a.load_graph(str(old))
    before=(a.diagnostic_stored_nodes(),a.outgoing([0,1,2]),a.temporal_state())
    a.save_graph(str(canonical))
    b=NativeBrainEngine();b.load_graph(str(canonical))
    assert (b.diagnostic_stored_nodes(),b.outgoing([0,1,2]),b.temporal_state())==before
    again=tmp_path/'again.native';b.save_graph(str(again))
    assert canonical.read_bytes()==again.read_bytes()
