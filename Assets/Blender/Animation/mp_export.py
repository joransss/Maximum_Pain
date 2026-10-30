"""Bakes every clip (actions with a "length" property) to Roblox Motor6D transforms.

- JSON (clips.json): [{name, length, loop, priority, joints, frames: [[time, [x,y,z,qx,qy,qz,qw] * joints]]}],
  sampled at 30 fps with IK and constraints evaluated. Studio builds KeyframeSequences from it.
- NLA: each clip on its own muted track, so the .blend lists every clip.
- FBX (optional, export_fbx=True): one baked file per clip for Studio's Animation Editor importer.
Run after mp_author/mp_clips:  exec(open(path).read(), {"__file__": path, "OUT": r"<folder>", "ONLY": None})
"""
import bpy, json, os
from mathutils import Matrix

exec(open(os.path.join(os.path.dirname(__file__), "mp_author.py")).read(), globals())
OUT = globals().get("OUT") or os.path.join(HERE, "export")
ONLY = globals().get("ONLY")
EXPORT_FBX = globals().get("EXPORT_FBX", False)


def transform(name):
    """Motor6D.Transform for a joint from the evaluated pose: T = Q P Q^-1."""
    parent = PARENT[name]
    bones, pose = ARM.data.bones, ARM.pose.bones
    rest_rel = bones[parent].matrix_local.inverted() @ bones[name].matrix_local
    local = rest_rel.inverted() @ pose[parent].matrix.inverted() @ pose[name].matrix
    return Q[name] @ local @ Q[name].inverted()


def bake(act):
    reset_pose()
    use_action(act)
    scene = bpy.context.scene
    length = act["length"]
    n = int(round(length * FPS))
    times = [k / FPS for k in range(n)] + [length]
    joints = list(act["joints"])
    frames = []
    for t in times:
        f = t * FPS
        scene.frame_set(int(f), subframe=f - int(f))
        vals = []
        for j in joints:
            T = transform(j)
            p, q = T.translation, T.to_quaternion()
            vals += [round(p.x, 4), round(p.y, 4), round(p.z, 4), round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5)]
        frames.append([round(t, 4), vals])
    return {"name": act.name, "length": length, "loop": bool(act["loop"]), "priority": act["priority"], "joints": joints, "frames": frames}


def nla_tracks(actions):
    ad = ARM.animation_data
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    for act in actions:
        tr = ad.nla_tracks.new()
        tr.name, tr.mute = act.name, True
        tr.strips.new(act.name, 0, act)
    ad.action = None


def export_fbx(act, folder):
    reset_pose()
    use_action(act)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 0, int(round(act["length"] * FPS))
    bpy.ops.object.select_all(action="DESELECT")
    ARM.select_set(True)
    bpy.context.view_layer.objects.active = ARM
    bpy.ops.export_scene.fbx(filepath=os.path.join(folder, act.name + ".fbx"), use_selection=True, object_types={"ARMATURE"},
                             add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_simplify_factor=0, use_armature_deform_only=True, apply_scale_options="FBX_SCALE_ALL")


actions = sorted((a for a in bpy.data.actions if "length" in a), key=lambda a: a.name)
if ONLY:
    actions = [a for a in actions if a.name in ONLY]
os.makedirs(OUT, exist_ok=True)
clips = [bake(a) for a in actions]
with open(os.path.join(OUT, "clips.json"), "w") as fh:
    json.dump(clips, fh, separators=(",", ":"))
if EXPORT_FBX:
    fbx_dir = os.path.join(HERE, "FBX")
    os.makedirs(fbx_dir, exist_ok=True)
    for a in actions:
        export_fbx(a, fbx_dir)
if not ONLY:
    nla_tracks(actions)
reset_pose()
EXPORTED = [(c["name"], len(c["frames"])) for c in clips]
