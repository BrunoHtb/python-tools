import os
import fiona
import struct
import configparser
import gc
from psd_tools import PSDImage
from shapely.geometry import Polygon, mapping

CLOSED_LEN   = 0
OPEN_LEN     = 3
CLOSED_LINK  = 1
CLOSED_ULINK = 2
OPEN_LINK    = 4
OPEN_ULINK   = 5
KNOTS = {CLOSED_LINK, CLOSED_ULINK, OPEN_LINK, OPEN_ULINK}

def read_world_file(tfw_path):
    with open(tfw_path, "r") as f:
        lines = [float(x.strip()) for x in f.readlines()]
    a, d, b, e, c, f_ = lines 
    return a, d, b, e, c, f_

def pixel_to_geo(x_px, y_px, a, d, b, e, c, f_):
    x_geo = c + x_px * a + y_px * b
    y_geo = f_ + x_px * d + y_px * e
    return (x_geo, y_geo)

def _fix_to_unit(b4):
    return struct.unpack(">l", b4)[0] / 65536.0

def _unit_to_px(u, dim):
    return (u / 256.0) * dim

def _cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    return (
        mt**3 * p0[0] + 3*mt**2*t * p1[0] + 3*mt*t**2 * p2[0] + t**3 * p3[0],
        mt**3 * p0[1] + 3*mt**2*t * p1[1] + 3*mt*t**2 * p2[1] + t**3 * p3[1],
    )

def sample_bezier(knots, steps=12, closed=True):
    """knots: lista de dicts com keys 'in', 'anchor', 'out' em pixels."""
    if not knots:
        return []

    pts = [knots[0]["anchor"]]
    n = len(knots)
    last = n if closed else n - 1

    for i in range(last):
        k0 = knots[i]
        k1 = knots[(i + 1) % n]
        p0 = k0["anchor"]
        p1 = k0["out"]
        p2 = k1["in"]
        p3 = k1["anchor"]

        for s in range(1, steps + 1):
            t = s / float(steps)
            pts.append(_cubic(p0, p1, p2, p3, t))
    return pts

def extract_paths(psb_path, sample_curves=True, steps=12):
    psd = PSDImage.open(psb_path)
    W, H = psd.width, psd.height

    results = []  
    for res_id, res in psd.image_resources.items():
        if not (2000 <= res_id <= 2999):
            continue

        raw = res.data
        name = getattr(res, "name", f"path_{res_id}")

        if "fx" not in name.lower():
            continue
        
        i = 0
        current_knots = []
        closed = None
        subpaths_px = []

        def flush_subpath():
            nonlocal current_knots, subpaths_px
            if not current_knots:
                return
            if sample_curves:
                ring = sample_bezier(current_knots, steps=steps, closed=True)
            else:
                ring = [k["anchor"] for k in current_knots]
                if ring and ring[0] != ring[-1]:
                    ring.append(ring[0])
            subpaths_px.append(ring)
            current_knots = []

        while i + 26 <= len(raw):
            rec = raw[i:i+26]; i += 26
            sel = struct.unpack(">h", rec[0:2])[0]

            if sel in (CLOSED_LEN, OPEN_LEN):
                if current_knots:
                    flush_subpath()
                closed = (sel == CLOSED_LEN)
                continue

            if sel in KNOTS:
                yin = _fix_to_unit(rec[2:6]);  xin = _fix_to_unit(rec[6:10])
                ya  = _fix_to_unit(rec[10:14]); xa  = _fix_to_unit(rec[14:18])
                yout= _fix_to_unit(rec[18:22]); xout= _fix_to_unit(rec[22:26])

                pts_unit = [(xin, yin), (xa, ya), (xout, yout)]
                pts_px = [(_unit_to_px(x, W), _unit_to_px(y, H)) for (x, y) in pts_unit]

                current_knots.append({"in": pts_px[0], "anchor": pts_px[1], "out": pts_px[2]})
                continue

        if current_knots:
            flush_subpath()

        if subpaths_px:
            results.append((name, subpaths_px, closed))


    return results, psd

def export_to_shp(paths, tfw_path, epsg="EPSG:31983", gpkg_out="saida_tudo.shp"):
    a, d, b, e, c, f_ = read_world_file(tfw_path)
    schema = {"geometry": "Unknown", "properties": {"tipo": "str"}}

    with fiona.open(gpkg_out, "w", driver="GPKG", crs=epsg, schema=schema, layer="vetores") as gpkg:
        for name, subpaths, is_closed in paths:
            for ring_px in subpaths:
                coords = [pixel_to_geo(x, y, a, d, b, e, c, f_) for (x, y) in ring_px]

                if is_closed and len(coords) >= 4:
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    gpkg.write({
                        "geometry": mapping(Polygon(coords)),
                        "properties": {"tipo": "poligono"}
                    })
                elif not is_closed and len(coords) >= 2:
                    gpkg.write({
                        "geometry": {"type": "LineString", "coordinates": coords},
                        "properties": {"tipo": "linha"}
                    })


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    input_dir = config.get("paths", "input_dir", fallback="./imagens/")
    output_dir = config.get("paths", "output_dir", fallback="./shapefiles/")

    if not os.path.isdir(input_dir):
        print(f"Caminho de entrada inválido no config.ini: {input_dir}")
        exit(1)
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if not file_name.lower().endswith('.psb'):
            continue

        base_name = os.path.splitext(file_name)[0]
        psb_file = os.path.join(input_dir, file_name)
        tfw_file = os.path.join(input_dir, base_name + '.tfw')

        if not os.path.exists(tfw_file):
            print(f"⚠️  Arquivo .tfw correspondente não encontrado para {file_name}, pulando...")
            continue

        print(f"Processando {psb_file}")

        paths, psd = extract_paths(psb_file, sample_curves=True, steps=16)
        print(f"  {len(paths)} paths encontrados.")

        export_to_shp(
            paths,
            tfw_file,
            epsg="EPSG:31983",
            gpkg_out=os.path.join(output_dir, f"{base_name}_vetor.gpkg")
        )
        del psd
        gc.collect()

        print(f"  ✅ Exportação {base_name} concluída.\n")
