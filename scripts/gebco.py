"""Minimal loader for the GEBCO 2026 GeoTIFF (uncompressed int16, WGS84 lat/lon).

Reads the TIFF tag directory directly so no GDAL/rasterio is needed, then exposes
the grid as a numpy memmap plus helpers for sub-setting by lat/lon.
"""
import os
import struct
from pathlib import Path

import numpy as np

# The GEBCO 2026 GeoTIFF subset (62.76-94.68 E, 35.67 S-33.94 N) from https://download.gebco.net/.
# Set GEBCO_TIF, or keep the unzipped download folder (GEBCO_*) next to this project folder.
_PROJECT = Path(__file__).resolve().parents[1]
_FOUND = sorted(_PROJECT.parent.glob("GEBCO_*/gebco_2026_*_geotiff.tif")) + sorted(_PROJECT.glob("gebco/*.tif"))
TIFF_PATH = Path(os.environ.get("GEBCO_TIF", _FOUND[0] if _FOUND else _PROJECT / "gebco" / "gebco_2026_geotiff.tif"))

# Geotransform from the .aux.xml shipped with the grid
WEST = 62.7625
NORTH = 33.941666666666666
CELL = 1.0 / 240.0  # 15 arc-seconds
NODATA = -32767

TAG_WIDTH, TAG_HEIGHT, TAG_BITS, TAG_COMPRESSION = 256, 257, 258, 259
TAG_STRIP_OFFSETS, TAG_ROWS_PER_STRIP, TAG_STRIP_BYTES = 273, 278, 279
TAG_TILE_WIDTH, TAG_TILE_OFFSETS, TAG_SAMPLE_FORMAT = 322, 324, 339
TYPE_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 16: 8}


def _read_ifd(path: Path) -> dict:
    with open(path, "rb") as handle:
        header = handle.read(16)
        endian = "<" if header[:2] == b"II" else ">"
        magic = struct.unpack(endian + "H", header[2:4])[0]
        if magic == 42:
            ifd_offset = struct.unpack(endian + "I", header[4:8])[0]
            handle.seek(ifd_offset)
            count = struct.unpack(endian + "H", handle.read(2))[0]
            entry_fmt, entry_size, inline = endian + "HHII", 12, 4
        elif magic == 43:  # BigTIFF
            ifd_offset = struct.unpack(endian + "Q", header[8:16])[0]
            handle.seek(ifd_offset)
            count = struct.unpack(endian + "Q", handle.read(8))[0]
            entry_fmt, entry_size, inline = endian + "HHQQ", 20, 8
        else:
            raise ValueError("Not a TIFF file")
        tags = {}
        raw_entries = handle.read(count * entry_size)
        for index in range(count):
            tag, typ, n, value = struct.unpack(entry_fmt, raw_entries[index * entry_size:(index + 1) * entry_size])
            size = TYPE_SIZES.get(typ, 1) * n
            code = {3: "H", 4: "I", 16: "Q", 1: "B", 2: "c", 5: "II"}.get(typ, "B")
            if size <= inline:
                raw = raw_entries[index * entry_size + entry_size - inline:index * entry_size + entry_size][:size]
            else:
                handle.seek(value)
                raw = handle.read(size)
            if typ in (3, 4, 16):
                tags[tag] = list(struct.unpack(endian + code * n, raw))
            else:
                tags[tag] = raw
        tags["_endian"] = endian
        return tags


def load_grid() -> np.ndarray:
    """Return the full grid as a read-only (rows, cols) int16 memmap, north-up."""
    tags = _read_ifd(TIFF_PATH)
    width, height = tags[TAG_WIDTH][0], tags[TAG_HEIGHT][0]
    if tags.get(TAG_COMPRESSION, [1])[0] != 1:
        raise ValueError("Compressed TIFF not supported by this loader")
    if TAG_TILE_WIDTH in tags:
        raise ValueError("Tiled TIFF not supported by this loader")
    offsets = tags[TAG_STRIP_OFFSETS]
    byte_counts = tags[TAG_STRIP_BYTES]
    expected_next = offsets[0]
    for offset, nbytes in zip(offsets, byte_counts):
        if offset != expected_next:
            raise ValueError("Strips are not contiguous")
        expected_next = offset + nbytes
    dtype = np.dtype(tags["_endian"] + "i2")
    return np.memmap(TIFF_PATH, dtype=dtype, mode="r", offset=offsets[0], shape=(height, width))


def window(grid: np.ndarray, south: float, north: float, west: float, east: float):
    """Cut a lat/lon window. Returns (array float32 with NaN nodata, lats, lons)."""
    row0 = int(np.floor((NORTH - north) / CELL))
    row1 = int(np.ceil((NORTH - south) / CELL))
    col0 = int(np.floor((west - WEST) / CELL))
    col1 = int(np.ceil((east - WEST) / CELL))
    row0, col0 = max(row0, 0), max(col0, 0)
    row1, col1 = min(row1, grid.shape[0]), min(col1, grid.shape[1])
    sub = np.array(grid[row0:row1, col0:col1], dtype=np.float32)
    sub[sub == NODATA] = np.nan
    lats = NORTH - (np.arange(row0, row1) + 0.5) * CELL
    lons = WEST + (np.arange(col0, col1) + 0.5) * CELL
    return sub, lats, lons


def inside(grid: np.ndarray, lat: float, lon: float) -> bool:
    row = int((NORTH - lat) / CELL)
    col = int((lon - WEST) / CELL)
    return 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]


def sample(grid: np.ndarray, lat: float, lon: float) -> float:
    """Elevation at a point; NaN outside the subset (negative indices would silently wrap round)."""
    if not inside(grid, lat, lon):
        return float("nan")
    row = int((NORTH - lat) / CELL)
    col = int((lon - WEST) / CELL)
    return float(grid[row, col])


if __name__ == "__main__":
    g = load_grid()
    print("grid", g.shape, g.dtype)
    for name, lat, lon in [("Adam's Peak", 6.8096, 80.4994), ("Rameswaram", 9.288, 79.313),
                           ("Ayodhya", 26.795, 82.194), ("Equator/Ujjain meridian", 0.0, 75.77),
                           ("Mahendragiri TN", 8.388, 77.522)]:
        print(f"{name:28s} {lat:8.4f} {lon:8.4f} elev={sample(g, lat, lon):7.0f} m")
