#!/usr/bin/env python3
"""Apply the OPEN-071-A rear-wing-pylon patch and verify the result.

Run from the repository root:

    python3 tools/apply_open071a.py

The script edits BlenderPipeline/scripts/af_bodywork_profile.py and
af_bodywork_selftest.py in place, then checks the git blob sha of each
file against the sha verified in the sandbox. It refuses to touch files
that are not in the expected pristine state, and it is idempotent: if
the patch is already applied it reports success and exits.
"""
import hashlib
import os
import sys

BASE = "BlenderPipeline/scripts"

EXPECTED = {
    "af_bodywork_profile.py": "8e427f45a83c8fb8e590b11a812d32907cde2c40",
    "af_bodywork_selftest.py": "3614b4cdd179fc4c38e0539e1fefbfb5248f4025",
}

PRISTINE = {
    "af_bodywork_profile.py": "44275f609bfeea92b1eca23d6807a55a6d5461ac",
    "af_bodywork_selftest.py": "71bce5fb9df1bcff19e01c09f69c4c906f341364",
}

PYLON = '''def _rear_wing_pylon():
    """Central swan-neck pylon joining the tail to the rear wing.

    The rear wing used to float 0.250 m behind the tail with nothing
    holding it up (OPEN-071-A). Real cars hang the wing from a single
    central swan-neck pylon that rises out of the engine cover and
    curls back to meet the wing from above; that is what is swept here.
    The path lives in the X/Z plane on the centre line, one end buried
    inside the tail solid and the other buried inside the wing solid,
    so the assembled body reads as one connected object from every
    camera angle while each part stays an independent closed manifold,
    exactly as the halo already interpenetrates the monocoque.
    """
    half_chord = _d("rear_wing_chord_m") / 2.0
    wing_x = tail_x() + half_chord
    wing_z = _d("rear_wing_height_m")
    radius = 0.030

    path = [
        (-2.04, 0.36),
        (-2.16, 0.47),
        (-2.30, 0.62),
        (-2.46, 0.78),
        (-2.56, 0.85),
        (wing_x, wing_z),
    ]

    section = superellipse_ring(_HALO_RING_POINTS, radius, radius, _EXP_TUBE)

    rings = []
    for i, (px, pz) in enumerate(path):
        if i == 0:
            ax, az = path[1][0] - px, path[1][1] - pz
        elif i == len(path) - 1:
            ax, az = px - path[i - 1][0], pz - path[i - 1][1]
        else:
            ax = path[i + 1][0] - path[i - 1][0]
            az = path[i + 1][1] - path[i - 1][1]
        length = math.sqrt(ax * ax + az * az)
        tx, tz = ax / length, az / length
        # Normal in the sweep plane; the binormal is the lateral axis.
        nx, nz = -tz, tx
        ring = [(px + nx * a, b, pz + nz * a) for (a, b) in section]
        rings.append(ring)
    return _swept_solid(rings)


'''


def blob_sha(data):
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha_of(path):
    with open(path, "rb") as fh:
        return blob_sha(fh.read())


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main():
    if not os.path.isdir(BASE):
        fail("run this from the repository root (BlenderPipeline/ not found)")

    profile = os.path.join(BASE, "af_bodywork_profile.py")
    selftest = os.path.join(BASE, "af_bodywork_selftest.py")

    if (sha_of(profile) == EXPECTED["af_bodywork_profile.py"]
            and sha_of(selftest) == EXPECTED["af_bodywork_selftest.py"]):
        print("already patched -- nothing to do")
        print("profile :", sha_of(profile))
        print("selftest:", sha_of(selftest))
        return

    if sha_of(profile) != PRISTINE["af_bodywork_profile.py"]:
        fail("af_bodywork_profile.py is not pristine; run\n"
             "  git restore " + profile + "\nand retry")
    if sha_of(selftest) != PRISTINE["af_bodywork_selftest.py"]:
        fail("af_bodywork_selftest.py is not pristine; run\n"
             "  git restore " + selftest + "\nand retry")

    # ---- profile: insert the pylon builder and register the 13th part ----
    with open(profile, encoding="utf-8") as fh:
        s = fh.read()
    anchor = "def build_parts():"
    if s.count(anchor) != 1:
        fail("anchor 'def build_parts():' not unique in profile")
    if "def _rear_wing_pylon" in s:
        fail("profile already contains _rear_wing_pylon but sha differs")
    s = s.replace(anchor, PYLON + anchor)
    entry = '        ("AF_Surface_Halo",) + _halo(),\n'
    if s.count(entry) != 1:
        fail("halo entry line not unique in build_parts()")
    s = s.replace(
        entry,
        entry + '        ("AF_Surface_RearWingPylon",) + _rear_wing_pylon(),\n',
    )
    with open(profile, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s)

    # ---- selftest: the body is now built from thirteen parts ----
    with open(selftest, encoding="utf-8") as fh:
        s2 = fh.read()
    old = 'self.ok(len(names) == 12, "the body is built from twelve parts")'
    if s2.count(old) != 1:
        fail("twelve-parts assertion not unique in selftest")
    s2 = s2.replace(
        old,
        'self.ok(len(names) == 13, "the body is built from thirteen parts")',
    )
    with open(selftest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(s2)

    # ---- verify ----
    got_p = sha_of(profile)
    got_s = sha_of(selftest)
    print("profile :", got_p)
    print("selftest:", got_s)
    if got_p != EXPECTED["af_bodywork_profile.py"]:
        fail("profile sha mismatch after patch -- do NOT commit")
    if got_s != EXPECTED["af_bodywork_selftest.py"]:
        fail("selftest sha mismatch after patch -- do NOT commit")
    print("OK: both files match the sandbox-verified shas")


if __name__ == "__main__":
    main()
