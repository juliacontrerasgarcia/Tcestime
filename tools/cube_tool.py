
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# ------------------------------------------------------------
# File        : cube_tool.py
# Author      : Nicolas F. Barrera
# Affiliation : Laboratoire de Chimie Theorique - Sorbonne Universite
# Date        : 10/10/2025
# Description : One-file utility to read, manipulate, and write Gaussian .cube files. 
# ------------------------------------------------------------

Commands:
  info <cube>                         Show header and data shape.
  to-npy <cube> [--out path.npy]      Convert volumetric data to .npy.
  copy <in.cube> <out.cube> [--dataset N]
  modify <in.cube> <out.cube> [options]
  elf-rescale <in.cube> <out.cube>    Apply: d_m = sqrt(1/v - 1); d_ok = 2^(2/3)*d_m; ELF_ok = 1/(1 + d_ok^2)

Modify options (can be combined):
  --dataset N                 Select dataset if input has several.
  --scale S                   Multiply by constant S.
  --add A                     Add constant A.
  --clip MIN MAX              Clip values into [MIN, MAX].
  --expr "EXPR"               NumPy expression using variables:
                               v  : data array (nx,ny,nz)
                               i,j,k : index grids
                               X,Y,Z : Cartesian coordinates of voxel centers
                              Also exposes np and common funcs: where, sqrt, abs, exp, log,
                              maximum, minimum, sin, cos, tan.
  --other other.cube          Load a second cube (as v2) and combine via --expr (requires same grid).
  --other-dataset N           Select dataset from other cube.

Notes:
- Supports D/d exponents, Angstrom vs Bohr via sign of natoms, multi-dataset cubes concatenated.
- Data is reshaped with order='F' (x varies fastest), as per cube standard.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass
from typing import List, Tuple, Iterator, Optional
import numpy as np


BOHR2ANG = 0.529177210903
ANG2BOHR = 1.0 / BOHR2ANG

def _to_float(s: str) -> float:
    return float(s.replace('D', 'E').replace('d', 'e'))

@dataclass
class Atom:
    Z: int
    charge: float
    xyz: Tuple[float, float, float]

@dataclass
class Cube:
    comment1: str
    comment2: str
    natoms: int
    origin: Tuple[float, float, float]
    nx: int; vx: Tuple[float, float, float]
    ny: int; vy: Tuple[float, float, float]
    nz: int; vz: Tuple[float, float, float]
    atoms: List[Atom]
    data: np.ndarray
    units: str

    @property
    def grid_shape(self) -> Tuple[int,int,int]:
        return (self.nx, self.ny, self.nz)

    def voxel_matrix(self) -> np.ndarray:
        return np.array([self.vx, self.vy, self.vz], dtype=float)

    def cell_matrix(self) -> np.ndarray:
        V = self.voxel_matrix()
        factors = np.array([self.nx, self.ny, self.nz], dtype=float)[:, None]
        return V * factors

def _read_header(lines: List[str], idx: int = 0) -> Tuple[Cube, int]:
    c1 = lines[idx].rstrip('\n'); idx += 1
    c2 = lines[idx].rstrip('\n'); idx += 1

    t = lines[idx].split(); idx += 1
    if len(t) < 4:
        raise ValueError("Malformed cube line 3 (natoms + origin).")
    natoms = int(t[0])
    origin = tuple(_to_float(x) for x in t[1:4])

    def parse_axis(line: str) -> Tuple[int, Tuple[float,float,float]]:
        s = line.split()
        if len(s) < 4:
            raise ValueError("Malformed cube grid/voxel line.")
        n = int(s[0])
        v = tuple(_to_float(x) for x in s[1:4])
        return n, v

    nx, vx = parse_axis(lines[idx]); idx += 1
    ny, vy = parse_axis(lines[idx]); idx += 1
    nz, vz = parse_axis(lines[idx]); idx += 1

    atoms: List[Atom] = []
    for _ in range(abs(natoms)):
        s = lines[idx].split(); idx += 1
        if len(s) < 5:
            raise ValueError("Malformed cube atom line.")
        Z = int(round(float(s[0])))
        q = _to_float(s[1])
        x, y, z = (_to_float(s[2]), _to_float(s[3]), _to_float(s[4]))
        atoms.append(Atom(Z, q, (x, y, z)))

    units = 'angstrom' if natoms > 0 else 'bohr'
    cube = Cube(
        comment1=c1, comment2=c2, natoms=natoms, origin=origin,
        nx=abs(nx), vx=vx, ny=abs(ny), vy=vy, nz=abs(nz), vz=vz,
        atoms=atoms, data=np.empty((0,)), units=units
    )
    return cube, idx

def _iter_values(lines: List[str], idx: int) -> Iterator[float]:
    for k in range(idx, len(lines)):
        line = lines[k].strip()
        if not line:
            continue
        for token in line.split():
            yield _to_float(token)

def _read_data(lines: List[str], idx: int, nx: int, ny: int, nz: int) -> Tuple[np.ndarray, int]:
    total = nx * ny * nz
    data = np.empty(total, dtype=float)
    it = _iter_values(lines, idx)
    for i in range(total):
        try:
            data[i] = next(it)
        except StopIteration:
            raise ValueError("Unexpected end of file while reading cube data.")
    consumed = 0
    k = idx
    while consumed < total and k < len(lines):
        n_in_line = len(lines[k].split())
        consumed += n_in_line
        k += 1
    arr = data.reshape((nx, ny, nz), order='F')
    return arr, k

def read_cube(path: str, allow_multi: bool = True) -> Cube:
    with open(path, 'r') as f:
        lines = f.readlines()
    cube, idx = _read_header(lines, 0)
    nx, ny, nz = cube.nx, cube.ny, cube.nz
    first, idx_after = _read_data(lines, idx, nx, ny, nz)

    if allow_multi:
        remaining_vals = sum(len(line.split()) for line in lines[idx_after:])
        if remaining_vals >= nx*ny*nz:
            datasets = [first]
            cur = idx_after
            while True:
                tokens_left = sum(len(line.split()) for line in lines[cur:])
                if tokens_left < nx*ny*nz:
                    break
                nxt, cur = _read_data(lines, cur, nx, ny, nz)
                datasets.append(nxt)
            data = np.stack(datasets, axis=0)
        else:
            data = first
    else:
        data = first
    cube.data = data
    return cube

def write_cube(path: str, cube: Cube, dataset: int = 0, wrap: int = 6) -> None:
    units_flag = cube.natoms if cube.units == 'angstrom' else -abs(cube.natoms)
    with open(path, 'w') as f:
        f.write(f"{cube.comment1}\n")
        f.write(f"{cube.comment2}\n")
        f.write(f"{units_flag:5d} {cube.origin[0]: .10f} {cube.origin[1]: .10f} {cube.origin[2]: .10f}\n")
        f.write(f"{cube.nx:5d} {cube.vx[0]: .10f} {cube.vx[1]: .10f} {cube.vx[2]: .10f}\n")
        f.write(f"{cube.ny:5d} {cube.vy[0]: .10f} {cube.vy[1]: .10f} {cube.vy[2]: .10f}\n")
        f.write(f"{cube.nz:5d} {cube.vz[0]: .10f} {cube.vz[1]: .10f} {cube.vz[2]: .10f}\n")
        for at in cube.atoms:
            f.write(f"{at.Z:5d} {at.charge: .6f} {at.xyz[0]: .10f} {at.xyz[1]: .10f} {at.xyz[2]: .10f}\n")
        arr = cube.data[dataset] if cube.data.ndim == 4 else cube.data
        flat = np.asarray(arr, dtype=float).reshape(-1, order='F')
        for i in range(0, flat.size, wrap):
            chunk = flat[i:i+wrap]
            f.write(" ".join(f"{v: .5E}" for v in chunk) + "\n")

def print_info(cube: Cube, file: Optional[str] = None) -> None:
    p = print
    p(f"File  : {file or '<in-memory>'}")
    p(f"Title : {cube.comment1}")
    p(f"Notes : {cube.comment2}")
    p(f"Units : {cube.units}")
    p(f"natoms: {abs(cube.natoms)}")
    p(f"origin: {cube.origin}")
    p(f"nx,ny,nz: {cube.nx}, {cube.ny}, {cube.nz}")
    p(f"vx: {cube.vx}")
    p(f"vy: {cube.vy}")
    p(f"vz: {cube.vz}")
    p("atoms:")
    for i, at in enumerate(cube.atoms, 1):
        p(f"  #{i:3d}: Z={at.Z:3d} q={at.charge: .4f} xyz={at.xyz}")
    p(f"data shape: {cube.data.shape}")

def _build_grids(cube: Cube):
    nx, ny, nz = cube.nx, cube.ny, cube.nz
    i = np.arange(nx)[:,None,None]
    j = np.arange(ny)[None,:,None]
    k = np.arange(nz)[None,None,:]
    origin = np.array(cube.origin, float)
    vx = np.array(cube.vx, float)[:,None,None]
    vy = np.array(cube.vy, float)[:,None,None]
    vz = np.array(cube.vz, float)[:,None,None]
    X = origin[0] + (i*vx[0] + j*vy[0] + k*vz[0])
    Y = origin[1] + (i*vx[1] + j*vy[1] + k*vz[1])
    Z = origin[2] + (i*vx[2] + j*vy[2] + k*vz[2])
    return i, j, k, X, Y, Z

def _check_compat(a: Cube, b: Cube):
    ok = (a.nx==b.nx and a.ny==b.ny and a.nz==b.nz and
          np.allclose(a.origin, b.origin) and
          np.allclose(a.vx, b.vx) and
          np.allclose(a.vy, b.vy) and
          np.allclose(a.vz, b.vz))
    if not ok:
        raise ValueError("Cube headers not compatible (grid or geometry differ).")

def cube_to_numpy(path_in: str, path_out: Optional[str] = None) -> str:
    cube = read_cube(path_in)
    base = os.path.splitext(path_in)[0]
    out = path_out or (base + ".npy")
    np.save(out, cube.data)
    return out

def _cmd_info(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool info")
    ap.add_argument("cube")
    args = ap.parse_args(argv)
    c = read_cube(args.cube)
    print_info(c, file=args.cube)
    return 0

def _cmd_to_npy(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool to-npy")
    ap.add_argument("cube")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    out = cube_to_numpy(args.cube, args.out)
    print(out)
    return 0

def _cmd_copy(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool copy")
    ap.add_argument("cube_in")
    ap.add_argument("cube_out")
    ap.add_argument("--dataset", type=int, default=0)
    args = ap.parse_args(argv)
    c = read_cube(args.cube_in)
    write_cube(args.cube_out, c, dataset=args.dataset)
    print(f"Wrote: {args.cube_out}")
    return 0

def _cmd_modify(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool modify")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--dataset", type=int, default=0)
    ap.add_argument("--scale", type=float)
    ap.add_argument("--add", type=float)
    ap.add_argument("--clip", nargs=2, type=float, metavar=("MIN","MAX"))
    ap.add_argument("--expr", type=str)
    ap.add_argument("--other", type=str)
    ap.add_argument("--other-dataset", type=int, default=0)
    args = ap.parse_args(argv)

    c = read_cube(args.input)
    v = c.data[args.dataset] if c.data.ndim==4 else c.data

    if args.scale is not None:
        v = v * args.scale
    if args.add is not None:
        v = v + args.add
    if args.clip is not None:
        v = np.clip(v, args.clip[0], args.clip[1])

    if args.other:
        c2 = read_cube(args.other)
        _check_compat(c, c2)
        v2 = c2.data[args.other_dataset] if c2.data.ndim==4 else c2.data
    else:
        v2 = None

    if args.expr:
        i,j,k,X,Y,Z = _build_grids(c)
        ns = {"np": np, "v": v, "i": i, "j": j, "k": k, "X": X, "Y": Y, "Z": Z,
              "where": np.where, "sqrt": np.sqrt, "abs": np.abs, "exp": np.exp, "log": np.log,
              "maximum": np.maximum, "minimum": np.minimum, "sin": np.sin, "cos": np.cos, "tan": np.tan}
        if v2 is not None:
            ns["v2"] = v2
        v = eval(args.expr, {"__builtins__": {}}, ns)
        if not isinstance(v, np.ndarray):
            v = np.array(v, dtype=float)
        if v.shape != (c.nx, c.ny, c.nz):
            raise ValueError(f"Expression result has wrong shape {v.shape}, expected {(c.nx,c.ny,c.nz)}")

    c.data = v
    write_cube(args.output, c)
    print(f"Wrote: {args.output}")
    return 0

def _cmd_elf_rescale(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool elf-rescale",
        description="Apply d_m = sqrt(1/v - 1); d_ok = 2^(2/3)*d_m; ELF_ok = 1/(1 + d_ok^2)")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--dataset", type=int, default=0)
    ap.add_argument("--eps", type=float, default=1e-12, help="Small epsilon to avoid division by zero (default 1e-12)")
    args = ap.parse_args(argv)

    c = read_cube(args.input)
    v = c.data[args.dataset] if c.data.ndim==4 else c.data
    v = np.clip(v, args.eps, None)  # ensure >0
    # Compute with stable form: ELF_ok = 1 / (1 + 2^(4/3) * (1/v - 1))
    factor = 2.0**(4.0/3.0)
    elf_ok = 1.0 / (1.0 + factor * (1.0/v - 1.0))
    c.data = elf_ok
    write_cube(args.output, c)
    print(f"Wrote: {args.output}")
    return 0

def _cli(argv: List[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="cube_tool", description="One-file tool to read/modify/write .cube files.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info")
    sub.add_parser("to-npy")
    sub.add_parser("copy")
    sub.add_parser("modify")
    sub.add_parser("elf-rescale")

    ns, rest = ap.parse_known_args(argv)
    if ns.cmd == "info":
        return _cmd_info(rest)
    if ns.cmd == "to-npy":
        return _cmd_to_npy(rest)
    if ns.cmd == "copy":
        return _cmd_copy(rest)
    if ns.cmd == "modify":
        return _cmd_modify(rest)
    if ns.cmd == "elf-rescale":
        return _cmd_elf_rescale(rest)
    return 1

if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
