"""Small, versioned, pickle-free chunk container for Synthetic Entity artifacts."""
from __future__ import annotations
import hashlib,json,os,struct,tempfile
from pathlib import Path
from typing import Any

HEADER=struct.Struct(">8sHHI")
MAGICS={"brain":b"SEBRAIN1","world":b"SEWORLD1"}

class ContainerError(ValueError):pass

def _bytes(value:Any)->bytes:
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def save_container(path:str|Path,kind:str,sections:dict[str,Any],optional:set[str]|None=None)->None:
    if kind not in MAGICS:raise ContainerError(f"unknown container kind: {kind}")
    optional=optional or set();payloads={name:_bytes(value) for name,value in sections.items()};offset=0;table=[]
    for name,payload in payloads.items():
        table.append({"name":name,"offset":offset,"size":len(payload),"required":name not in optional,"sha256":hashlib.sha256(payload).hexdigest()});offset+=len(payload)
    table_bytes=_bytes(table);target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=target.name+".",suffix=".tmp",dir=target.parent)
    try:
        with os.fdopen(fd,"wb") as stream:
            stream.write(HEADER.pack(MAGICS[kind],1,len(table),len(table_bytes)));stream.write(table_bytes)
            for payload in payloads.values():stream.write(payload)
            stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,target)
    except Exception:
        try:os.unlink(tmp)
        except OSError:pass
        raise

def load_container(path:str|Path,kind:str,known:set[str]|None=None)->dict[str,Any]:
    raw=Path(path).read_bytes()
    if len(raw)<HEADER.size:raise ContainerError("truncated container header")
    magic,version,count,table_size=HEADER.unpack(raw[:HEADER.size])
    if magic!=MAGICS.get(kind):raise ContainerError(f"not a .se{kind} container")
    if version!=1:raise ContainerError(f"unsupported container version: {version}")
    try:table=json.loads(raw[HEADER.size:HEADER.size+table_size]);base=HEADER.size+table_size
    except Exception as exc:raise ContainerError("corrupt section table") from exc
    if len(table)!=count:raise ContainerError("section count mismatch")
    result={}
    for entry in table:
        name=entry["name"]
        if known is not None and name not in known:
            if entry.get("required",True):raise ContainerError(f"unsupported required section: {name}")
            continue
        payload=raw[base+entry["offset"]:base+entry["offset"]+entry["size"]]
        if len(payload)!=entry["size"] or hashlib.sha256(payload).hexdigest()!=entry["sha256"]:raise ContainerError(f"corrupt section: {name}")
        try:result[name]=json.loads(payload)
        except Exception as exc:raise ContainerError(f"invalid JSON section: {name}") from exc
    return result

def inspect_container(path:str|Path)->dict[str,Any]:
    raw=Path(path).read_bytes();magic,version,count,table_size=HEADER.unpack(raw[:HEADER.size])
    table=json.loads(raw[HEADER.size:HEADER.size+table_size]);return {"magic":magic.decode("ascii"),"version":version,"sections":table,"size":len(raw),"section_count":count}
