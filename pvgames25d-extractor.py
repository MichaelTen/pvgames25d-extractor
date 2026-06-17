#!/usr/bin/env python3
"""Extract official PVGames 2.5D zip packs into a clean folder layout."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


RAW_DIR_NAME = "raw-extracted-zips"
CLEAN_DIR_NAME = "PVGAMES25D"


@dataclass(frozen=True)
class PromoteRule:
    raw_path: str
    clean_path: str


PACKS: dict[str, tuple[PromoteRule, ...]] = {
    "Characters Vol 1.zip": (
        PromoteRule("Characters Vol 1", "Characters Vol 1"),
    ),
    "Characters Vol 2.zip": (
        PromoteRule("Characters Vol 2", "Characters Vol 2"),
    ),
    "Characters Vol 3.zip": (
        PromoteRule("Characters Vol 3", "Characters Vol 3"),
    ),
    "Characters WW2.zip": (
        PromoteRule("WW2 Characters", "WW2 Characters"),
    ),
    "ChristmasKrampus.zip": (
        PromoteRule("Krampus_Cosmic", "ChristmasKrampus/Krampus_Cosmic"),
        PromoteRule("Krampus_Eldritch", "ChristmasKrampus/Krampus_Eldritch"),
        PromoteRule("Krampus_Original", "ChristmasKrampus/Krampus_Original"),
    ),
    "Daemonum_Infernum.zip": (
        PromoteRule("Daemonum Infernum", "Daemonum Infernum"),
    ),
    "Medieval Buildings Vol 2.zip": (
        PromoteRule("Medieval Buildings Vol 2", "Medieval Buildings Vol 2"),
    ),
    "Medieval_Buildings_Vol_1.zip": (
        PromoteRule("Medieval Buildings Vol 1", "Medieval Buildings Vol 1"),
    ),
    "PVGames_ApexPredators.zip": (
        PromoteRule("Apex_Hunter", "PVGames_ApexPredators/Apex_Hunter"),
        PromoteRule("Apex_Predator", "PVGames_ApexPredators/Apex_Predator"),
        PromoteRule("Apex_Stalker", "PVGames_ApexPredators/Apex_Stalker"),
    ),
    "PVGames_Infernus_Free.zip": (
        PromoteRule("Infernus_Tiles", "Infernus_Tiles"),
    ),
    "PVG_NaturePackVol1.zip": (
        PromoteRule("Nature Pack Vol 1", "Nature Pack Vol 1"),
    ),
    "PVG_ScorchingSands.zip": (
        PromoteRule("Scorching Sands", "Scorching Sands"),
    ),
    "PVG_SnowandIce.zip": (
        PromoteRule("Snow and Ice", "Snow and Ice"),
    ),
    "PVG_WW2Tiles_Vol1.zip": (
        PromoteRule("WW2_Tiles_Vol1", "WW2_Tiles_Vol1"),
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract PVGames 2.5D zip files beside this script into "
            f"{RAW_DIR_NAME}, then move the useful asset folders into "
            f"{CLEAN_DIR_NAME}."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned extraction and move operations without changing files.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help=(
            "Copy clean asset folders instead of moving them. By default, asset "
            f"folders are moved out of {RAW_DIR_NAME}, leaving readme/reference "
            "files there."
        ),
    )
    return parser.parse_args()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def print_error(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def fail(message: str) -> None:
    print_error(message)
    raise SystemExit(1)


def relative_display(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def verify_zip_set(base_dir: Path) -> None:
    expected = set(PACKS)
    actual = {
        path.name
        for path in base_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".zip"
    }

    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)

    if missing:
        print_error("Missing required zip file(s):")
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        print(
            "Move the required official PVGames zip files into the same folder "
            "as this script, then run it again.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if unknown:
        print_error("Found unrecognized zip file(s):")
        for name in unknown:
            print(f"  - {name}", file=sys.stderr)
        print(
            "Move unrelated or renamed zip files out of this folder before running "
            "the extractor. This script only handles the exact pack names listed "
            "in README.md.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def verify_output_folders_absent(base_dir: Path) -> None:
    conflicts = [
        path
        for path in (base_dir / RAW_DIR_NAME, base_dir / CLEAN_DIR_NAME)
        if path.exists()
    ]
    if not conflicts:
        return

    print_warning("Output folder(s) already exist:")
    for path in conflicts:
        print(f"  - {relative_display(path, base_dir)}", file=sys.stderr)
    print(
        "Move or rename the existing folder(s), then run this script again. "
        "Nothing will be overwritten.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def normalized_relative_key(path: Path, base: Path) -> tuple[str, ...]:
    return tuple(part.casefold() for part in path.relative_to(base).parts)


def normalized_clean_key(clean_path: str) -> tuple[str, ...]:
    return tuple(part.casefold() for part in PurePosixPath(clean_path).parts)


def path_key_contains(parent: tuple[str, ...], child: tuple[str, ...]) -> bool:
    return len(parent) < len(child) and child[: len(parent)] == parent


def verify_clean_paths_unique() -> None:
    seen: dict[tuple[str, ...], str] = {}
    conflicts: list[str] = []

    for zip_name, rules in PACKS.items():
        for rule in rules:
            key = normalized_clean_key(rule.clean_path)
            label = f"{zip_name}: {rule.clean_path}"

            if key in seen:
                conflicts.append(f"{label} conflicts with {seen[key]}")
                continue

            for seen_key, seen_label in seen.items():
                if path_key_contains(seen_key, key) or path_key_contains(key, seen_key):
                    conflicts.append(f"{label} overlaps with {seen_label}")

            seen[key] = label

    if conflicts:
        print_error("Two or more asset rules would land in the same cleaned path:")
        for conflict in conflicts:
            print(f"  - {conflict}", file=sys.stderr)
        print("Nothing was extracted or moved.", file=sys.stderr)
        raise SystemExit(1)


def safe_member_path(destination: Path, member_name: str) -> Path:
    normalized_name = member_name.replace("\\", "/")
    pure_path = PurePosixPath(normalized_name)

    if pure_path.is_absolute():
        fail(f"Refusing to extract absolute zip path: {member_name}")

    clean_parts: list[str] = []
    for part in pure_path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            fail(f"Refusing to extract path traversal entry: {member_name}")
        if ":" in part:
            fail(f"Refusing to extract unsafe zip path: {member_name}")
        clean_parts.append(part)

    if not clean_parts:
        fail(f"Refusing to extract empty zip path: {member_name}")

    target = destination.joinpath(*clean_parts)
    resolved_destination = destination.resolve(strict=False)
    resolved_target = target.resolve(strict=False)
    try:
        resolved_target.relative_to(resolved_destination)
    except ValueError:
        fail(f"Refusing to extract outside destination: {member_name}")

    return target


def zip_entry_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_ISLNK(mode)


def apply_zip_timestamp(target: Path, info: zipfile.ZipInfo) -> None:
    try:
        modified_time = time.mktime(info.date_time + (0, 0, -1))
        os.utime(target, (modified_time, modified_time))
    except (OverflowError, OSError, ValueError):
        pass


def extract_zip(zip_path: Path, destination: Path, dry_run: bool) -> None:
    print(f"Extracting {zip_path.name} -> {destination.name}")
    if dry_run:
        return

    destination.mkdir(parents=True, exist_ok=False)

    seen_targets: dict[tuple[str, ...], str] = {}

    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if zip_entry_is_symlink(info):
                fail(f"Refusing to extract symlink entry from {zip_path.name}: {info.filename}")

            target = safe_member_path(destination, info.filename)
            target_key = normalized_relative_key(target, destination)
            if info.is_dir():
                existing_kind = seen_targets.get(target_key)
                if existing_kind == "file":
                    fail(
                        "Zip entry path conflict in "
                        f"{zip_path.name}: {info.filename}"
                    )
                seen_targets[target_key] = "dir"
                if target.exists() and not target.is_dir():
                    fail(
                        f"Refusing to overwrite existing non-folder path: {target}"
                    )
                target.mkdir(parents=True, exist_ok=True)
                continue

            if target_key in seen_targets or target.exists():
                fail(
                    "Zip entry path conflict or existing extraction path in "
                    f"{zip_path.name}: {info.filename}"
                )
            seen_targets[target_key] = "file"
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
            apply_zip_timestamp(target, info)


def extract_all_zips(base_dir: Path, raw_dir: Path, dry_run: bool) -> None:
    if not dry_run:
        raw_dir.mkdir(parents=True, exist_ok=False)

    for zip_name in PACKS:
        zip_path = base_dir / zip_name
        destination = raw_dir / zip_path.stem
        extract_zip(zip_path, destination, dry_run)


def find_promotion_conflicts(
    raw_dir: Path,
    clean_dir: Path,
    check_sources: bool,
) -> list[str]:
    conflicts: list[str] = []
    for zip_name, rules in PACKS.items():
        raw_pack_dir = raw_dir / Path(zip_name).stem
        for rule in rules:
            source = raw_pack_dir / rule.raw_path
            destination = clean_dir / rule.clean_path
            if check_sources and not source.exists():
                conflicts.append(
                    f"Missing expected raw asset path: {source}"
                )
            if destination.exists():
                conflicts.append(
                    "Clean destination already exists and will not be overwritten: "
                    f"{destination}"
                )
    return conflicts


def copy_or_move(source: Path, destination: Path, copy_mode: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if copy_mode:
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    else:
        shutil.move(str(source), str(destination))


def promote_assets(raw_dir: Path, clean_dir: Path, copy_mode: bool, dry_run: bool) -> None:
    conflicts = find_promotion_conflicts(raw_dir, clean_dir, check_sources=not dry_run)
    if conflicts:
        print_error("Cannot create the clean folder because of these conflict(s):")
        for conflict in conflicts:
            print(f"  - {conflict}", file=sys.stderr)
        print(
            "Move or rename existing folders/files with the same names, then run "
            "the script again. Nothing was overwritten.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if not dry_run:
        clean_dir.mkdir(parents=True, exist_ok=False)

    action = "Copying" if copy_mode else "Moving"
    for zip_name, rules in PACKS.items():
        raw_pack_dir = raw_dir / Path(zip_name).stem
        for rule in rules:
            source = raw_pack_dir / rule.raw_path
            destination = clean_dir / rule.clean_path
            print(f"{action} {source} -> {destination}")
            if not dry_run:
                copy_or_move(source, destination, copy_mode)


def main() -> int:
    args = parse_args()
    base_dir = script_dir()
    raw_dir = base_dir / RAW_DIR_NAME
    clean_dir = base_dir / CLEAN_DIR_NAME

    print("PVGames 2.5D extractor")
    print(f"Working folder: {base_dir}")
    print(
        "Use only with PVGames assets you legally obtained from the official "
        "itch.io asset store."
    )

    verify_zip_set(base_dir)
    verify_clean_paths_unique()
    verify_output_folders_absent(base_dir)
    extract_all_zips(base_dir, raw_dir, args.dry_run)
    promote_assets(raw_dir, clean_dir, args.copy, args.dry_run)

    if args.dry_run:
        print("Dry run complete. No files were changed.")
    else:
        print(f"Done. Clean assets are in {clean_dir}")
        print(f"Leftover readme/reference files remain in {raw_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
