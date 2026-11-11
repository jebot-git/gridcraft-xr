#!/usr/bin/python3
"""Build this fork's engine and its DomeD frontend from an immutable shared base."""
import argparse
import json
import os
from pathlib import Path
import subprocess

native=Path(__file__).resolve().parent
repository=native.parents[1]
lock=json.loads((native/'base.lock.json').read_text())
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--domed-source',type=Path,required=True,help='Canonical DomeD checkout with native GPU/menu/BDF headers')
parser.add_argument('--toolkit',type=Path,help='Installed DomeD-patched FLTK 1.4.5 CMake prefix')
parser.add_argument('--base-source',type=Path,help='Already checked-out shared base at the locked revision')
parser.add_argument('--engine-dir',type=Path,help='Reuse prebuilt headless engines from this directory')
parser.add_argument('--build',type=Path,default=native/'_build')
parser.add_argument('--jobs',type=int,default=4)
args=parser.parse_args()
if not 1<=args.jobs<=32:parser.error('jobs must be 1–32')
args.domed_source=args.domed_source.resolve()
if not (args.domed_source/'native/gpu-window.h').is_file():parser.error('domed-source lacks the canonical native integration')
def run(command,**kwargs):subprocess.run([str(value) for value in command],check=True,**kwargs)
base=args.base_source.resolve() if args.base_source else native/'_deps/dome-craft-base'
if not base.exists():
    base.parent.mkdir(parents=True,exist_ok=True)
    run(['git','clone','--filter=blob:none','--no-checkout',lock['repository'],base])
    run(['git','-C',base,'fetch','--depth','1','origin',lock['revision']])
    run(['git','-C',base,'checkout','--detach',lock['revision']])
actual=subprocess.check_output(['git','-C',str(base),'rev-parse','HEAD'],text=True).strip()
if actual!=lock['revision']:raise SystemExit('Shared base revision differs from base.lock.json; use a separate checkout')
if subprocess.check_output(['git','-C',str(base),'status','--porcelain','--untracked-files=no'],text=True).strip():raise SystemExit('Shared base has tracked changes; refusing an unrecorded build')
project=lock['application'];build=args.build.resolve();build.mkdir(parents=True,exist_ok=True)
engines=args.engine_dir.resolve() if args.engine_dir else build/'engine-target/release'
if not args.engine_dir:
    environment={**os.environ,'DOME_OFFICE_COMMON':str(base/'bitmap'),'CARGO_TARGET_DIR':str(build/'engine-target'),'CARGO_BUILD_JOBS':str(args.jobs)}
    run(['cargo','build','--manifest-path',repository/'Cargo.toml','--locked','--release','-p',project+'-cli',*lock['cargo_args']],env=environment)
if not (engines/(project+'-cli')).is_file():raise SystemExit('Required engine is missing: '+str(engines/(project+'-cli')))
command=['cmake','-S',base,'-B',build/'native','-DCMAKE_BUILD_TYPE=Release','-DBUILD_TESTING=OFF','-DDOME_OFFICE_BUILD_LEGACY_FIXTURES=OFF','-DARTCRAFT_DOMED_SOURCE='+str(args.domed_source),'-DDOME_CRAFT_ENGINE_DIR='+str(engines)]
if args.toolkit:command+=['-DCMAKE_PREFIX_PATH='+str(args.toolkit.resolve())]
run(command)
run(['cmake','--build',build/'native','--target',project+'-domed-native','-j',args.jobs])
# The local launcher forwards argument boundaries and delegates realm selection.
launcher=build/(project+'-domed')
program=[str(build/'native'/(project+'-domed-native')),'--engine',str(engines/(project+'-cli')),'--registry',str(base/'upstream.lock.json')]
launcher.write_text(chr(10).join(['#!/usr/bin/python3','import os,shutil,sys','command='+repr(program)+'+sys.argv[1:]','helper=shutil.which("dome-link")','if helper:os.execv(helper,[helper,"--",*command])','os.execv(command[0],command)'])+chr(10))
launcher.chmod(0o755)
print(launcher)
