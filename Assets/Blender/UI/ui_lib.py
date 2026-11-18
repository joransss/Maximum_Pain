"""Maximum Pain - the menus' art, made in Blender (the vault's "Menus, Loadout, Progression and Shop
- To Do", section 3).

Run it from a terminal with Blender 5.2 or newer, from the repo's root:

    blender -b --factory-startup --python-exit-code 1 --python Assets/Blender/UI/ui_lib.py -- [group ...]

Groups (all of them when none are named):
    logo      UI_Logo.blend: "MAXIMUM PAIN" in Oswald Bold, the HUD's own font (found in Roblox's install
              folder; set UI_FONT to a copy of Oswald-Bold.ttf to use another), extruded, worn white paint
              over steel, rendered flat-on. UI_Logo_Full (one line) and UI_Logo_Compact (two lines).
    overlays  the film look, worked out pixel by pixel: UI_Overlay_Grain (a 256 px tile with no seams),
              UI_Overlay_Vignette, UI_Overlay_Bokeh1 (warm) and UI_Overlay_Bokeh2 (cool),
              UI_Overlay_LightLeak.
    weapons   UI_Icons_Weapons.blend: every gun the weapon pipeline exported to
              Assets/Blender/Weapons/Exports/FBX, side-on with the muzzle to the right, in white (the game
              tints it grey with ImageColor3). Named UI_Icon_<last part of the gun's id>: UI_Icon_AK47.

Options:
    --rebuild        build a group's .blend afresh from this script (otherwise an existing one is
                     rendered as it is, with whatever was changed in it by hand)
    --out DIR        write the images, the manifest and the .blend files to DIR instead (for tests)
    --weapons-from DIR   take the guns' FBX files from DIR

Each image goes to Assets/Blender/UI/Exports/<name>.png and is listed in Exports/manifest.json with its
size and SHA-256, which the game's UiAssets module copies (ASSETS). Re-running gives byte-identical files:
fixed seeds, fixed render settings (Cycles on the CPU, no denoiser), no dates or names in the PNGs.

The .blend files are scenes to look at and adjust. Every object in a scene's UI_Render collection is
rendered one by one through the camera UI_Camera, lit by the UI_Rig lights, each framed to fit: the object's
custom properties say how. "ui_frame" = (width, height) renders it into a frame of that many pixels;
"ui_height" = the pixels it is drawn at on a 1080p screen, rendered at twice that (the plan's rule) and
never wider than MAX_SIZE. So an object added to UI_Render by hand is rendered too.
"""
import glob
import hashlib
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
WEAPON_FBX = os.path.join(REPO, "Assets", "Blender", "Weapons", "Exports", "FBX")
MAX_SIZE = 1024  # Roblox shows images up to 1024 px on a side
MARGIN = 0.05  # of the frame's height, left clear round each object so bevels and shading aren't cut
SAMPLES = 256
GROUPS = ("logo", "overlays", "weapons")

# The palette (the HUD's): white, black, mid grey. Colours below are sRGB, as the PNGs store them.
PAINT = (0.86, 0.86, 0.84)  # the logo's paint, linear: shows near white under the rig
STEEL = (0.11, 0.115, 0.12)  # the steel under it, linear


# --- Settings that make every render the same ------------------------------------------------------

def plain_output(scene):
    """PNG, RGBA, 8 bits, transparent film, sRGB with no tone curve, and no metadata at all."""
    render = scene.render
    render.resolution_percentage = 100
    render.film_transparent = True
    render.use_compositing = False
    render.use_sequencer = False
    settings = render.image_settings
    settings.file_format = "PNG"
    settings.color_mode = "RGBA"
    settings.color_depth = "8"
    settings.compression = 90
    for name in dir(render):
        if name.startswith("use_stamp"):
            setattr(render, name, False)
    scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


def cycles(scene):
    scene.render.engine = "CYCLES"
    c = scene.cycles
    c.device = "CPU"
    c.samples = SAMPLES
    c.use_adaptive_sampling = False
    c.use_denoising = False
    c.seed = 0
    c.use_animated_seed = False
    c.max_bounces = 6
    c.diffuse_bounces = 3
    c.glossy_bounces = 3
    c.transparent_max_bounces = 8
    c.sample_clamp_indirect = 4.0
    c.pixel_filter_type = "BLACKMAN_HARRIS"
    c.filter_width = 1.5
    plain_output(scene)


def rewrite_plain(path):
    """Saves the PNG at `path` again with nothing but its pixels: Cycles writes its render times into
    every file it renders, which would make each run's file differ. The pixels go through unchanged
    (8-bit values in and out, straight alpha)."""
    source = bpy.data.images.load(path, check_existing=False)
    width, height = source.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    source.pixels.foreach_get(pixels)
    bpy.data.images.remove(source)
    plain = bpy.data.images.new("plain", width, height, alpha=True, float_buffer=False)
    plain.colorspace_settings.name = "sRGB"
    plain.alpha_mode = "STRAIGHT"
    plain.pixels.foreach_set(pixels)
    plain.filepath_raw = path
    plain.file_format = "PNG"
    plain.save()
    bpy.data.images.remove(plain)


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


class Manifest:
    """Exports/manifest.json: every image's size and hash, by name, sorted so it only changes with them."""

    def __init__(self, folder):
        self.path = os.path.join(folder, "manifest.json")
        self.entries = {}
        if os.path.exists(self.path):
            with open(self.path, encoding="utf-8") as handle:
                self.entries = json.load(handle)

    def add(self, name, path):
        image = bpy.data.images.load(path, check_existing=False)
        width, height = image.size
        bpy.data.images.remove(image)
        self.entries[name] = {"file": os.path.basename(path), "width": width, "height": height, "sha256": sha256(path)}
        print("  %-26s %4d x %-4d %s" % (name, width, height, self.entries[name]["sha256"][:12]))

    def save(self):
        with open(self.path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(dict(sorted(self.entries.items())), handle, indent=2)
            handle.write("\n")


# --- Images worked out pixel by pixel ------------------------------------------------------------

def save_pixels(name, rgba, folder):
    """Writes an (height, width, 4) array of sRGB values 0..1, top row first, as <folder>/<name>.png."""
    height, width = rgba.shape[:2]
    image = bpy.data.images.new(name, width, height, alpha=True, float_buffer=False)
    image.colorspace_settings.name = "sRGB"
    image.alpha_mode = "STRAIGHT"
    flipped = np.ascontiguousarray(np.clip(rgba[::-1], 0.0, 1.0), dtype=np.float32)  # Blender's rows go bottom up
    image.pixels.foreach_set(flipped.ravel())
    path = os.path.join(folder, name + ".png")
    image.filepath_raw = path
    image.file_format = "PNG"
    image.save()
    bpy.data.images.remove(image)
    return path


def smoothstep(low, high, x):
    t = np.clip((x - low) / (high - low), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def periodic_blur(field, sigma):
    """A gaussian blur that wraps round the edges, so a tile stays seamless."""
    fy = np.fft.fftfreq(field.shape[0])[:, None]
    fx = np.fft.fftfreq(field.shape[1])[None, :]
    kernel = np.exp(-2.0 * (math.pi ** 2) * (sigma ** 2) * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(field) * kernel))


def dither(rng, shape):
    """Half a step of 8-bit noise, so smooth gradients don't band."""
    return (rng.random(shape) - 0.5) / 255.0


def grain(size=256, seed=11):
    """Film grain: white and black specks with soft clumps, as much lightening as darkening, so it adds
    texture without greying the picture. Tiles with no seams (the blur wraps round)."""
    rng = np.random.default_rng(seed)
    noise = periodic_blur(rng.standard_normal((size, size)), 0.5)
    noise /= noise.std()
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = np.where(noise > 0.0, 1.0, 0.0)[..., None]
    # Full strength here; the game sets how much shows (MenuKit's ImageTransparency).
    rgba[..., 3] = np.clip(np.abs(noise) * 0.5, 0.0, 1.0)
    return rgba


def vignette(width=1024, height=576, seed=12):
    """Black edges fading to clear: stretched over the screen, its ellipse follows any shape of screen."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:height, 0:width]
    u = (x + 0.5) / width * 2.0 - 1.0
    v = (y + 0.5) / height * 2.0 - 1.0
    r = np.sqrt(u * u + 1.2 * v * v)
    rgba = np.zeros((height, width, 4))
    rgba[..., 3] = smoothstep(0.5, 1.5, r) ** 1.5 * 0.9 + dither(rng, (height, width))
    return rgba


def bokeh(discs, size=512, seed=13):
    """Out-of-focus lights: discs a little brighter at the rim, as a lens draws them, with soft edges
    and a faint mottle. `discs` are (x, y, radius) as shares of the image, colour (sRGB) and strength."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size]
    px = (x + 0.5) / size
    py = (y + 0.5) / size
    mottle = periodic_blur(rng.standard_normal((size, size)), 6.0)
    mottle /= mottle.std()
    keep = np.ones((size, size))  # 1 - alpha so far: the discs add up like light (screen)
    colour = np.zeros((size, size, 3))
    for (cx, cy, radius), tint, strength in discs:
        d = np.sqrt((px - cx) ** 2 + (py - cy) ** 2) / radius
        body = 0.72 + 0.28 * smoothstep(0.75, 0.96, d)
        edge = 1.0 - smoothstep(0.93, 1.04, d)
        alpha = np.clip(strength * body * edge * (1.0 + 0.025 * mottle), 0.0, 1.0)
        colour += np.array(tint)[None, None, :] * alpha[..., None]
        keep *= 1.0 - alpha
    total = 1.0 - keep
    rgba = np.zeros((size, size, 4))
    weight = np.maximum(colour.max(axis=2, keepdims=True), 1e-6)
    rgba[..., :3] = np.where(total[..., None] > 1e-6, colour / weight, 1.0)
    rgba[..., 3] = total + dither(rng, (size, size)) * (total > 0.002)
    return rgba


def light_leak(size=512, seed=14):
    """A warm leak of light from one corner (top right as drawn), amber at its heart, orange outside."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size]
    px = (x + 0.5) / size
    py = (y + 0.5) / size
    d = np.sqrt((px - 1.05) ** 2 + 1.3 * (py + 0.05) ** 2)
    alpha = np.exp(-((d / 0.62) ** 2)) * 0.85
    warmth = np.clip(d / 0.9, 0.0, 1.0)[..., None]
    inner = np.array([1.0, 0.86, 0.56])
    outer = np.array([1.0, 0.52, 0.22])
    rgba = np.zeros((size, size, 4))
    rgba[..., :3] = inner * (1.0 - warmth) + outer * warmth
    rgba[..., 3] = np.clip(alpha + dither(rng, (size, size)) * (alpha > 0.002), 0.0, 1.0)
    return rgba


def build_overlays(folder, manifest):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    images = {
        "UI_Overlay_Grain": grain(),
        "UI_Overlay_Vignette": vignette(),
        "UI_Overlay_Bokeh1": bokeh([
            ((0.30, 0.34, 0.20), (1.0, 0.76, 0.48), 0.60),
            ((0.62, 0.52, 0.26), (1.0, 0.86, 0.64), 0.46),
            ((0.42, 0.74, 0.14), (1.0, 0.70, 0.42), 0.55),
            ((0.78, 0.24, 0.11), (1.0, 0.92, 0.78), 0.42),
        ], seed=13),
        "UI_Overlay_Bokeh2": bokeh([
            ((0.36, 0.40, 0.24), (0.72, 0.92, 0.96), 0.44),
            ((0.68, 0.64, 0.17), (0.90, 0.97, 1.0), 0.52),
            ((0.24, 0.72, 0.12), (0.66, 0.88, 0.90), 0.40),
        ], seed=15),
        "UI_Overlay_LightLeak": light_leak(),
    }
    for name, rgba in images.items():
        manifest.add(name, save_pixels(name, rgba, folder))


# --- The shared scene: camera, lights, collections ------------------------------------------------

def nodes_of(datablock):
    """A material's or world's node tree. Blender 5 always has one; older versions make it on request."""
    if datablock.node_tree is None:
        datablock.use_nodes = True
    return datablock.node_tree


def collection(name, parent=None):
    found = bpy.data.collections.get(name)
    if found:
        return found
    made = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(made)
    return made


def aim(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def build_rig():
    """The camera (orthographic, looking down -Z: the picture's right is +X and its top +Y) and a soft
    three-point rig round the origin, all under the empty UI_RigCenter that each render moves and sizes
    to the object it frames. Energies are for an object about 1 unit across; each render scales them
    with the square of the object's size."""
    rig = collection("UI_Rig")
    centre = bpy.data.objects.new("UI_RigCenter", None)
    rig.objects.link(centre)

    camera_data = bpy.data.cameras.new("UI_Camera")
    camera_data.type = "ORTHO"
    camera_data.sensor_fit = "HORIZONTAL"
    camera_data.clip_start = 0.01
    camera_data.clip_end = 200.0
    camera = bpy.data.objects.new("UI_Camera", camera_data)
    rig.objects.link(camera)
    bpy.context.scene.camera = camera

    lights = [
        # name, position (x right, y up, z toward the camera), energy (W at 1 unit), colour, size.
        # Set so the logo's white paint comes out at about 0.9 and never clips (measured 2026-11-18).
        ("UI_Key", Vector((-2.2, 2.0, 3.0)), 150.0, (1.0, 0.95, 0.88), 2.5),
        ("UI_Fill", Vector((2.6, -0.8, 2.6)), 52.0, (0.86, 0.93, 1.0), 3.0),
        ("UI_Rim", Vector((0.4, 3.2, 0.5)), 125.0, (1.0, 1.0, 1.0), 1.5),
    ]
    for name, position, energy, colour, size in lights:
        data = bpy.data.lights.new(name, "AREA")
        data.shape = "DISK"
        data.size = size
        data.energy = energy
        data.color = colour
        data["ui_energy"] = energy
        light = bpy.data.objects.new(name, data)
        light.location = position
        aim(light, Vector((0.0, 0.0, 0.0)))
        light.parent = centre
        rig.objects.link(light)

    world = bpy.data.worlds.new("UI_World")
    tree = nodes_of(world)
    background = next((n for n in tree.nodes if n.type == "BACKGROUND"), None)
    if background is None:
        background = tree.nodes.new("ShaderNodeBackground")
        output = next((n for n in tree.nodes if n.type == "OUTPUT_WORLD"), None) or tree.nodes.new("ShaderNodeOutputWorld")
        tree.links.new(background.outputs["Background"], output.inputs["Surface"])
    background.inputs["Color"].default_value = (0.03, 0.03, 0.035, 1.0)
    background.inputs["Strength"].default_value = 1.0
    bpy.context.scene.world = world


def bounds(objects):
    """The world-space box round the objects as they render (modifiers, bevels and extrusion included)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    low = Vector((math.inf, math.inf, math.inf))
    high = -low
    for obj in objects:
        if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            point = evaluated.matrix_world @ Vector(corner)
            low = Vector(map(min, low, point))
            high = Vector(map(max, high, point))
    if low.x == math.inf:
        raise RuntimeError("nothing to frame in " + ", ".join(o.name for o in objects))
    return low, high


def frame_size(obj, width, height):
    """The render's size in pixels, from the object's custom properties (see the header)."""
    if "ui_frame" in obj:
        frame_w, frame_h = (int(v) for v in obj["ui_frame"])
        return frame_w, frame_h
    target = 2 * int(obj.get("ui_height", 128))
    inner = target * (1.0 - 2.0 * MARGIN)
    frame_w = math.ceil(width / height * inner + 2.0 * MARGIN * target)
    if frame_w > MAX_SIZE:
        target = math.floor(target * MAX_SIZE / frame_w)
        frame_w = MAX_SIZE
    return frame_w, target


def render_collection(path, folder, manifest, only=None):
    """Opens a .blend and renders every object in its UI_Render collection, one at a time."""
    bpy.ops.wm.open_mainfile(filepath=path)
    prepare_fonts()
    scene = bpy.context.scene
    cycles(scene)
    items = sorted(bpy.data.collections["UI_Render"].objects, key=lambda o: o.name)
    items = [o for o in items if o.parent is None and (only is None or o.name in only)]

    def family(root):
        return [root] + list(root.children_recursive)

    everything = [o for root in items for o in family(root)]
    centre = bpy.data.objects["UI_RigCenter"]
    camera = bpy.data.objects["UI_Camera"]
    for item in items:
        members = family(item)
        for obj in everything:
            obj.hide_render = obj not in members
        low, high = bounds(members)
        width, height = high.x - low.x, high.y - low.y
        frame_w, frame_h = frame_size(item, width, height)
        unit = max(width / (frame_w - 2.0 * MARGIN * frame_h), height / (frame_h * (1.0 - 2.0 * MARGIN)))
        middle = (low + high) / 2.0
        camera.location = (middle.x, middle.y, high.z + 20.0)
        camera.rotation_euler = (0.0, 0.0, 0.0)
        camera.data.ortho_scale = unit * frame_w
        reach = max(width, height)
        centre.location = middle
        centre.scale = (reach, reach, reach)
        for light in centre.children:
            light.data.energy = light.data["ui_energy"] * reach * reach
        scene.render.resolution_x, scene.render.resolution_y = frame_w, frame_h
        out = os.path.join(folder, item.name + ".png")
        scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        rewrite_plain(out)
        manifest.add(item.name, out)
    for obj in everything:
        obj.hide_render = False


# --- The logo ---------------------------------------------------------------------------------------

def find_font():
    """Oswald Bold: UI_FONT if set, else the copy inside Roblox Studio's or Roblox's install folders."""
    chosen = os.environ.get("UI_FONT")
    if chosen:
        if not os.path.isfile(chosen):
            raise RuntimeError("UI_FONT doesn't point to a file: " + chosen)
        return chosen
    roots = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "Versions"),
        r"C:\Program Files (x86)\Roblox\Versions",
        r"C:\Program Files\Roblox\Versions",
        "/Applications/RobloxStudio.app/Contents/Resources",
    ]
    found = []
    for root in roots:
        found += glob.glob(os.path.join(root, "*", "content", "fonts", "Oswald-Bold.ttf"))
        found += glob.glob(os.path.join(root, "content", "fonts", "Oswald-Bold.ttf"))
    if not found:
        raise RuntimeError("Oswald-Bold.ttf not found in Roblox's install folders: set UI_FONT to a copy of it")
    # Every Roblox version ships the same file; take the newest copy.
    return max(found, key=os.path.getmtime)


def prepare_fonts():
    """Points the scene's Oswald at this computer's copy (the .blend stores a path, not the font)."""
    for font in bpy.data.fonts:
        if font.name.startswith("Oswald"):
            font.filepath = find_font()  # setting the path loads the font from it


def socket(node, identifier):
    return next(s for s in node.inputs if s.identifier == identifier)


def logo_material():
    """Worn white paint over steel: the paint chips away in patches, along fine scratches and on the
    bevelled edges, where the steel shows. Procedural, so it renders the same every time."""
    material = bpy.data.materials.new("MAT_UI_LogoPaint")
    tree = nodes_of(material)
    nodes, links = tree.nodes, tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    coords = nodes.new("ShaderNodeTexCoord")
    # Chips: broken patches where a coarse noise dips.
    chips = nodes.new("ShaderNodeTexNoise")
    chips.inputs["Scale"].default_value = 7.0
    chips.inputs["Detail"].default_value = 9.0
    chips.inputs["Roughness"].default_value = 0.62
    links.new(coords.outputs["Object"], chips.inputs["Vector"])
    chip_mask = nodes.new("ShaderNodeMapRange")
    chip_mask.interpolation_type = "SMOOTHSTEP"
    chip_mask.inputs["From Min"].default_value = 0.30
    chip_mask.inputs["From Max"].default_value = 0.36
    links.new(chips.outputs["Fac"], chip_mask.inputs["Value"])
    # Scratches: a noise stretched sideways, cut to thin lines.
    stretch = nodes.new("ShaderNodeMapping")
    stretch.inputs["Scale"].default_value = (2.0, 60.0, 2.0)
    links.new(coords.outputs["Object"], stretch.inputs["Vector"])
    scratches = nodes.new("ShaderNodeTexNoise")
    scratches.inputs["Scale"].default_value = 3.0
    scratches.inputs["Detail"].default_value = 2.0
    links.new(stretch.outputs["Vector"], scratches.inputs["Vector"])
    scratch_mask = nodes.new("ShaderNodeMapRange")
    scratch_mask.interpolation_type = "SMOOTHSTEP"
    scratch_mask.inputs["From Min"].default_value = 0.735
    scratch_mask.inputs["From Max"].default_value = 0.705
    links.new(scratches.outputs["Fac"], scratch_mask.inputs["Value"])
    # Edges: wherever the surface turns away from the camera (the bevel), the paint has worn off.
    geometry = nodes.new("ShaderNodeNewGeometry")
    split = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geometry.outputs["Normal"], split.inputs["Vector"])
    edge_mask = nodes.new("ShaderNodeMapRange")
    edge_mask.interpolation_type = "SMOOTHSTEP"
    edge_mask.inputs["From Min"].default_value = 0.80
    edge_mask.inputs["From Max"].default_value = 0.97
    links.new(split.outputs["Z"], edge_mask.inputs["Value"])

    # paint = chips x scratches x edges (each 1 where the paint is whole).
    first = nodes.new("ShaderNodeMath")
    first.operation = "MULTIPLY"
    links.new(chip_mask.outputs["Result"], first.inputs[0])
    links.new(scratch_mask.outputs["Result"], first.inputs[1])
    paint = nodes.new("ShaderNodeMath")
    paint.operation = "MULTIPLY"
    links.new(first.outputs["Value"], paint.inputs[0])
    links.new(edge_mask.outputs["Result"], paint.inputs[1])

    colour = nodes.new("ShaderNodeValToRGB")
    colour.color_ramp.elements[0].color = (*STEEL, 1.0)
    colour.color_ramp.elements[1].color = (*PAINT, 1.0)
    links.new(paint.outputs["Value"], colour.inputs["Fac"])
    links.new(colour.outputs["Color"], shader.inputs["Base Color"])
    for name, steel, painted in (("Metallic", 1.0, 0.0), ("Roughness", 0.32, 0.58)):
        mapped = nodes.new("ShaderNodeMapRange")
        mapped.inputs["To Min"].default_value = steel
        mapped.inputs["To Max"].default_value = painted
        links.new(paint.outputs["Value"], mapped.inputs["Value"])
        links.new(mapped.outputs["Result"], shader.inputs[name])
    return material


def text_object(name, body, font, material, location, height_px):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.font = font
    curve.size = 1.0
    curve.align_x = "LEFT"
    curve.space_character = 1.04
    curve.space_line = 0.74
    curve.extrude = 0.03
    curve.bevel_depth = 0.014
    curve.bevel_resolution = 3
    curve.materials.append(material)
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj["ui_height"] = height_px
    return obj


def build_logo(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_rig()
    items = collection("UI_Render")
    font = bpy.data.fonts.load(find_font())
    font.name = "Oswald-Bold"
    material = logo_material()
    # The menu draws the full logo 104 px high at 1080p (MenuController's LOGO_HEIGHT); the compact one
    # is for narrow places.
    items.objects.link(text_object("UI_Logo_Full", "MAXIMUM PAIN", font, material, (0.0, 0.0, 0.0), 104))
    items.objects.link(text_object("UI_Logo_Compact", "MAXIMUM\nPAIN", font, material, (0.0, -3.0, 0.0), 160))
    bpy.ops.wm.save_as_mainfile(filepath=path)


# --- Weapon icons -------------------------------------------------------------------------------------

POINTS = ("Muzzle", "Grip", "Support", "Aim", "Eject", "Hinge")


def is_point(obj):
    base = obj.name.split(".")[0]
    return base.endswith("_Att") or any(base == p or base.endswith("_" + p) for p in POINTS)


def icon_material():
    material = bpy.data.materials.new("MAT_UI_Icon")
    tree = nodes_of(material)
    shader = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if shader is None:
        tree.nodes.clear()
        shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
        output = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    shader.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1.0)
    shader.inputs["Roughness"].default_value = 0.55
    shader.inputs["Metallic"].default_value = 0.0
    return material


def build_weapons(path, source):
    files = sorted(glob.glob(os.path.join(source, "*.fbx")))
    if not files:
        raise RuntimeError("no gun FBX files in " + source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_rig()
    items = collection("UI_Render")
    material = icon_material()
    spacing = 0.0
    for file in files:
        weapon_id = os.path.splitext(os.path.basename(file))[0]
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=file)
        imported = [o for o in bpy.data.objects if o not in before]
        muzzle = next((o for o in imported if o.name.split(".")[0].endswith("Muzzle_Att") or o.name.split(".")[0] == "Muzzle"), None)
        bpy.context.view_layer.update()
        muzzle_at = muzzle.matrix_world.translation.copy() if muzzle else None
        for obj in imported:
            if is_point(obj) or obj.type not in {"MESH", "EMPTY"}:
                bpy.data.objects.remove(obj)
        imported = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in imported if o.type == "MESH"]
        low, high = bounds(meshes)
        middle = (low + high) / 2.0
        # The gun points along its longest flat axis, toward the muzzle if there is one.
        size = high - low
        forward = Vector((1.0, 0.0, 0.0)) if size.x >= size.y else Vector((0.0, 1.0, 0.0))
        if muzzle_at is not None and (muzzle_at - middle).dot(forward) < 0.0:
            forward = -forward
        up = Vector((0.0, 0.0, 1.0))
        right = forward.cross(up)
        # Turn it so the muzzle is to the picture's right (+X), its top up (+Y) and its right side faces
        # the camera (+Z): the HUD's view, muzzle right.
        turn = Matrix((forward, up, right)).to_4x4()
        root = bpy.data.objects.new("UI_Icon_" + weapon_id.split("_")[-1], None)
        items.objects.link(root)
        root["ui_frame"] = (512, 160)
        root["weapon_id"] = weapon_id
        for obj in imported:
            if obj.parent is None:
                world = obj.matrix_world.copy()
                obj.parent = root
                obj.matrix_world = turn @ Matrix.Translation(-middle) @ world
            for user in list(obj.users_collection):
                user.objects.unlink(obj)
            items.objects.link(obj)
            if obj.type == "MESH":
                obj.data.materials.clear()
                obj.data.materials.append(material)
        root.location = (0.0, spacing, 0.0)
        spacing -= 2.0
    bpy.ops.wm.save_as_mainfile(filepath=path)


# --- Running it ---------------------------------------------------------------------------------------

def arguments():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    options = {"groups": [], "rebuild": False, "out": None, "weapons_from": WEAPON_FBX}
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--rebuild":
            options["rebuild"] = True
        elif arg in ("--out", "--weapons-from"):
            index += 1
            options[arg[2:].replace("-", "_")] = os.path.abspath(args[index])
        elif arg in GROUPS:
            options["groups"].append(arg)
        else:
            raise SystemExit("ui_lib: unknown argument " + arg + " (groups: " + ", ".join(GROUPS) + ")")
        index += 1
    return options


def main():
    options = arguments()
    named = options["groups"]
    groups = named or list(GROUPS)
    folder = options["out"] or os.path.join(HERE, "Exports")
    blends = options["out"] or HERE
    os.makedirs(folder, exist_ok=True)
    manifest = Manifest(folder)
    for group in groups:
        print("ui_lib: " + group)
        if group == "overlays":
            build_overlays(folder, manifest)
            continue
        if group == "logo":
            path = os.path.join(blends, "UI_Logo.blend")
            if options["rebuild"] or not os.path.exists(path):
                build_logo(path)
        else:
            path = os.path.join(blends, "UI_Icons_Weapons.blend")
            if options["rebuild"] or not os.path.exists(path):
                if not glob.glob(os.path.join(options["weapons_from"], "*.fbx")):
                    if named:
                        raise SystemExit("ui_lib: no gun FBX files in " + options["weapons_from"])
                    print("  skipped: no gun FBX files in " + options["weapons_from"])
                    continue
                build_weapons(path, options["weapons_from"])
        render_collection(path, folder, manifest)
    manifest.save()
    print("ui_lib: done, " + os.path.join(folder, "manifest.json"))


if __name__ == "__main__":
    main()
