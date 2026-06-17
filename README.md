# PVGames 2.5D Extractor - pvgames25d-extractor
This is a python script for organizing legally obtained PVGames 2.5D asset zip files into a clean `PVGAMES25D` folder while preserving raw extracted contents separately.

# PVGames 2.5D Extractor

This script, `pvgames25d-extractor.py`, is a Python script that extracts the official PVGames 2.5D zip packs into a cleaner folder layout.

Run it from the folder containing the legally obtained PVGames zip files. The script is intended to be placed in that same folder. It only checks for `.zip` files directly beside the script and does not search recursively.

When run, it creates:

- `raw-extracted-zips/`: a raw staging folder, with one subfolder per zip file.
- `PVGAMES25D/`: the cleaned asset folder structure.

The script first extracts every zip into `raw-extracted-zips/`. It then moves only the useful asset folders into `PVGAMES25D/`, leaving readme/reference documents and other unpromoted files in `raw-extracted-zips/`.

## Legal Use

Only run this script with PVGames assets you have legally obtained from the official PVGames itch.io asset store. This script does not grant any license to the assets and does not include any PVGames files.

## Required Files

Put `pvgames25d-extractor.py` in the same folder as these zip files:

- `Characters Vol 1.zip`
- `Characters Vol 2.zip`
- `Characters Vol 3.zip`
- `Characters WW2.zip`
- `ChristmasKrampus.zip`
- `Daemonum_Infernum.zip`
- `Medieval Buildings Vol 2.zip`
- `Medieval_Buildings_Vol_1.zip`
- `PVGames_ApexPredators.zip`
- `PVGames_Infernus_Free.zip`
- `PVG_NaturePackVol1.zip`
- `PVG_ScorchingSands.zip`
- `PVG_SnowandIce.zip`
- `PVG_WW2Tiles_Vol1.zip`

Do not place unrelated zip files in the same folder when running the script. The script checks only the folder containing the script, requires exact zip names, and stops if required files are missing or unknown zip files are present.

## What It Changes

Running the script creates new folders beside the script:

- `raw-extracted-zips/Characters Vol 1/`
- `raw-extracted-zips/Characters Vol 2/`
- `raw-extracted-zips/Characters Vol 3/`
- `raw-extracted-zips/Characters WW2/`
- `raw-extracted-zips/ChristmasKrampus/`
- `raw-extracted-zips/Daemonum_Infernum/`
- `raw-extracted-zips/Medieval Buildings Vol 2/`
- `raw-extracted-zips/Medieval_Buildings_Vol_1/`
- `raw-extracted-zips/PVGames_ApexPredators/`
- `raw-extracted-zips/PVGames_Infernus_Free/`
- `raw-extracted-zips/PVG_NaturePackVol1/`
- `raw-extracted-zips/PVG_ScorchingSands/`
- `raw-extracted-zips/PVG_SnowandIce/`
- `raw-extracted-zips/PVG_WW2Tiles_Vol1/`
- `PVGAMES25D/`

The clean `PVGAMES25D/` folder is organized as:

- `Characters Vol 1/`
- `Characters Vol 2/`
- `Characters Vol 3/`
- `ChristmasKrampus/`
- `Daemonum Infernum/`
- `Infernus_Tiles/`
- `Medieval Buildings Vol 1/`
- `Medieval Buildings Vol 2/`
- `Nature Pack Vol 1/`
- `PVGames_ApexPredators/`
- `Scorching Sands/`
- `Snow and Ice/`
- `WW2 Characters/`
- `WW2_Tiles_Vol1/`

By default, the asset folders are moved from `raw-extracted-zips/` into `PVGAMES25D/`. Use `--copy` if you want the raw staging folder to keep a full copy of the asset folders too.

## Overwrite Safety

The script will not overwrite existing folders or files.

If `PVGAMES25D/` or `raw-extracted-zips/` already exists, the script stops and prints a warning. Move, rename, or remove the existing folder first, then run the script again.

If any clean destination folder already exists, the script stops and prints a warning. Move or rename the conflicting folder before running again.

If two asset folders would land at the same cleaned path, or one cleaned destination would overlap another, the script stops and reports the conflict before extraction.

## Usage

From the folder containing the script and zip files:

```powershell
python .\pvgames25d-extractor.py
```

To preview what it would do without changing files:

```powershell
python .\pvgames25d-extractor.py --dry-run
```

To copy asset folders into `PVGAMES25D/` instead of moving them:

```powershell
python .\pvgames25d-extractor.py --copy
```

## Notes

- Python 3 is required.
- The script uses only Python standard library modules.
- The script should be run from a folder containing only this script and the required PVGames zip files.
- Source zip files are not deleted or modified.
