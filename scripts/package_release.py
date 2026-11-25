"""Package only this documentation repository. Does not upload or initialize Git."""
from __future__ import annotations
import argparse
import hashlib
import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.git','.venv','__pycache__','.checks','dist'}
ALLOWED_DIRS={'docs','api','data','examples','schemas','scripts','tests','templates','references','.github'}

def source_files(root):
    root=root.resolve()
    result=[]
    for current,dirs,names in os.walk(root,followlinks=False):
        current=Path(current)
        for name in list(dirs):
            path=current/name
            if name in EXCLUDE or path.is_symlink():dirs.remove(name)
            elif current==root and name not in ALLOWED_DIRS:
                raise ValueError(f'Unexpected root directory: {name}; review before packaging')
        for name in names:
            p=current/name
            if p.is_symlink():raise ValueError(f'Symlink excluded from release: {p.name}')
            if p.suffix in {'.zip','.pyc','.log'} or p.name.endswith('.zip.sha256'):continue
            if p.name in {'.env','secrets.json','ACCESS.txt'} or p.suffix in {'.pem','.key','.pfx','.p12'}:
                raise ValueError(f'Private file excluded from release: {p.name}')
            result.append(p)
    return sorted(result)

def package(root,output):
    selected=source_files(root)
    output=output.resolve()
    output.parent.mkdir(parents=True,exist_ok=True)
    prefix='foreign-trade-system-docs'
    with ZipFile(output,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in selected:
            z.write(p,f'{prefix}/{p.relative_to(root).as_posix()}')
    with ZipFile(output) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(selected)
        for p in selected:
            entry=f'{prefix}/{p.relative_to(root).as_posix()}'
            assert z.read(entry)==p.read_bytes()
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name(output.name+'.sha256').write_text(f'{digest}  {output.name}\n',encoding='utf-8')
    return {'files':len(selected),'zip_bytes':output.stat().st_size,'sha256':digest}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'dist'/'foreign-trade-system-docs-0.1.0.zip')
    args=parser.parse_args()
    import json
    print(json.dumps(package(ROOT,args.output),indent=2))

if __name__=='__main__':main()
