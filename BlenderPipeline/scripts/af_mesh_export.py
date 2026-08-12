#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wavefront OBJ and Stanford PLY writers for the Uludag Formula bodywork.

Milestone 4, slice 3.

Why this module exists
----------------------
Slice 1 and slice 2 built twelve bodywork surfaces and a set of convex
collision proxies entirely in stdlib Python, and proved their arithmetic in
continuous integration.  Nothing produced by those slices has ever been seen
by a human being.  A signed volume of +0.19952084794791036 is a number, not a
car.  This module is the bridge: it serialises the generated meshes to two
plain text interchange formats that Blender, MeshLab and Unreal can all open,
so that the geometry can finally be inspected with eyes rather than asserts.

Design rules obeyed here
------------------------
*   Standard library only.  No bpy, no numpy.  The continuous integration
    matrix runs Python 3.9 and Python 3.12, so the syntax stays inside the
    intersection of the two.
*   The writers are pure functions over (verts, faces) tuples.  Nothing
    touches the filesystem except dump_parts, and that function is never
    called from the self test with a path outside a caller supplied
    directory.
*   Vertex coordinates are written with the %.17g format.  Seventeen
    significant digits is the shortest field width that is guaranteed to
    round trip an IEEE 754 double exactly.  %.6f, the format most OBJ
    exporters use, would silently discard roughly ten digits of the geometry
    this project spent two slices computing.  The round trip cases below
    assert bit exact equality, which is only meaningful because of that
    choice.
*   A writer that cannot be read back is not a writer.  parse_obj exists so
    that every emitted file can be re-imported and compared against the mesh
    it came from, vertex by vertex and face by face.

Nothing in this file changes af_bodywork_profile.py.  That module is 42219
bytes, is already committed, and already executes in continuous integration.
Extending it in place would mean retranscribing all of it, which this project
forbids for files past roughly twenty kilobytes.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import af_bodywork_profile as bw  # noqa: E402


# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------

#: Seventeen significant digits round trips an IEEE 754 double exactly.
FLOAT_FORMAT = "%.17g"

#: Written into the header of every emitted file.
GENERATOR_TAG = "UludagFormula af_mesh_export"

#: Extension used by the OBJ writer, including the leading dot.
OBJ_EXT = ".obj"

#: Extension used by the PLY writer, including the leading dot.
PLY_EXT = ".ply"

#: File name, without extension, of the single combined body export.
COMBINED_STEM = "AF_Bodywork_Combined"

#: File name, without extension, of the combined collision proxy export.
COLLISION_STEM = "AF_Bodywork_Collision"


class ExportError(ValueError):
    """Raised when a mesh cannot be serialised or a file cannot be parsed."""


# --------------------------------------------------------------------------
# formatting helpers
# --------------------------------------------------------------------------

def format_float(value):
    """Render one coordinate so that float(format_float(v)) == v exactly."""
    if not isinstance(value, float):
        value = float(value)
    return FLOAT_FORMAT % value


def _validate_mesh(verts, faces):
    """Reject the mesh shapes that the writers cannot represent."""
    if not verts:
        raise ExportError("mesh has no vertices")
    if not faces:
        raise ExportError("mesh has no faces")
    count = len(verts)
    for vert in verts:
        if len(vert) != 3:
            raise ExportError("vertex is not a three tuple: %r" % (vert,))
    for face in faces:
        if len(face) < 3:
            raise ExportError("face has fewer than three corners: %r"
                              % (face,))
        for index in face:
            if not isinstance(index, int):
                raise ExportError("face index is not an int: %r" % (index,))
            if index < 0 or index >= count:
                raise ExportError("face index out of range: %d" % index)
    return count


# --------------------------------------------------------------------------
# Wavefront OBJ
# --------------------------------------------------------------------------

def format_obj(name, verts, faces, offset=0):
    """One OBJ group as a list of lines, without a trailing newline.

    ``offset`` shifts the emitted one based indices, which is what lets
    several groups share one file.
    """
    _validate_mesh(verts, faces)
    lines = ["g %s" % name, "o %s" % name]
    for (x, y, z) in verts:
        lines.append("v %s %s %s" % (format_float(x), format_float(y),
                                     format_float(z)))
    for face in faces:
        corners = " ".join(str(index + 1 + offset) for index in face)
        lines.append("f %s" % corners)
    return lines


def obj_document(groups):
    """A complete OBJ file, as text, from an iterable of named meshes."""
    lines = ["# %s" % GENERATOR_TAG,
             "# units: metres, right handed, Z up"]
    offset = 0
    for (name, verts, faces) in groups:
        lines.extend(format_obj(name, verts, faces, offset))
        offset += len(verts)
    return "\n".join(lines) + "\n"


def parse_obj(text):
    """Read an OBJ document back into a list of (name, verts, faces).

    Only the subset this module emits is understood: comments, ``g``, ``o``,
    ``v`` and ``f``.  Anything else raises, because silently skipping an
    unknown record would let a round trip pass while losing data.
    """
    groups = []
    verts = []
    pending_name = None
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        tag = parts[0]
        if tag == "g":
            pending_name = " ".join(parts[1:])
        elif tag == "o":
            name = " ".join(parts[1:])
            if pending_name is not None and pending_name != name:
                raise ExportError("g and o disagree: %r vs %r"
                                  % (pending_name, name))
            current = (name, [])
            groups.append(current)
            pending_name = None
        elif tag == "v":
            if len(parts) != 4:
                raise ExportError("vertex record is malformed: %r" % (line,))
            verts.append((float(parts[1]), float(parts[2]),
                          float(parts[3])))
        elif tag == "f":
            if current is None:
                raise ExportError("face before any group")
            corners = []
            for token in parts[1:]:
                index = int(token.split("/")[0])
                if index <= 0:
                    raise ExportError("index is not one based: %d" % index)
                corners.append(index - 1)
            if len(corners) < 3:
                raise ExportError("face has fewer than three corners")
            current[1].append(tuple(corners))
        else:
            raise ExportError("unsupported OBJ record: %r" % (tag,))

    result = []
    base = 0
    for (name, faces) in groups:
        highest = -1
        for face in faces:
            for index in face:
                if index > highest:
                    highest = index
        span = highest - base + 1
        if span <= 0:
            raise ExportError("group %r references no vertices" % (name,))
        block = verts[base:base + span]
        rebased = [tuple(index - base for index in face) for face in faces]
        for face in rebased:
            for index in face:
                if index < 0 or index >= len(block):
                    raise ExportError("group %r has a stray index" % (name,))
        result.append((name, block, rebased))
        base += span
    if base != len(verts):
        raise ExportError("trailing vertices are unreferenced")
    return result


# --------------------------------------------------------------------------
# Stanford PLY
# --------------------------------------------------------------------------

def ply_document(name, verts, faces):
    """A complete ascii PLY file, as text, for a single mesh."""
    _validate_mesh(verts, faces)
    lines = [
        "ply",
        "format ascii 1.0",
        "comment %s" % GENERATOR_TAG,
        "comment object %s" % name,
        "element vertex %d" % len(verts),
        "property float x",
        "property float y",
        "property float z",
        "element face %d" % len(faces),
        "property list uchar int vertex_index",
        "end_header",
    ]
    for (x, y, z) in verts:
        lines.append("%s %s %s" % (format_float(x), format_float(y),
                                   format_float(z)))
    for face in faces:
        lines.append("%d %s" % (len(face),
                                " ".join(str(index) for index in face)))
    return "\n".join(lines) + "\n"


def ply_header_fields(text):
    """The element counts declared by a PLY header, as a dict."""
    counts = {}
    for line in text.splitlines():
        if line == "end_header":
            return counts
        parts = line.split()
        if parts and parts[0] == "element" and len(parts) == 3:
            counts[parts[1]] = int(parts[2])
    raise ExportError("PLY header is not terminated")


# --------------------------------------------------------------------------
# filesystem
# --------------------------------------------------------------------------

def export_plan():
    """Every file this module would write, as (stem, groups) pairs."""
    parts = bw.build_parts()
    proxies = bw.collision_proxies()
    plan = []
    for (name, verts, faces) in parts:
        plan.append((name, [(name, verts, faces)]))
    plan.append((COMBINED_STEM, list(parts)))
    plan.append((COLLISION_STEM, list(proxies)))
    return plan


def dump_parts(directory, ply=True):
    """Write the whole export plan under ``directory``.

    Returns the sorted list of file names written.  The directory is created
    if it does not already exist.
    """
    if not directory:
        raise ExportError("no output directory given")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    written = []
    for (stem, groups) in export_plan():
        obj_path = os.path.join(directory, stem + OBJ_EXT)
        handle = open(obj_path, "w")
        try:
            handle.write(obj_document(groups))
        finally:
            handle.close()
        written.append(stem + OBJ_EXT)
        if ply and len(groups) == 1:
            (name, verts, faces) = groups[0]
            ply_path = os.path.join(directory, stem + PLY_EXT)
            handle = open(ply_path, "w")
            try:
                handle.write(ply_document(name, verts, faces))
            finally:
                handle.close()
            written.append(stem + PLY_EXT)
    return sorted(written)


# --------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------

class _ExportSelfTest(object):
    """Round trip and formatting cases for the writers above."""

    def __init__(self):
        self.assertions = 0
        self.failures = []
        self._parts = None

    # -- harness ---------------------------------------------------------

    def ok(self, condition, message):
        self.assertions += 1
        if not condition:
            self.failures.append(message)

    def close(self, got, want, tolerance, message):
        self.assertions += 1
        if abs(got - want) > tolerance:
            self.failures.append("%s: got %r want %r" % (message, got, want))

    def raises(self, callable_object, message):
        self.assertions += 1
        try:
            callable_object()
        except ExportError:
            return
        except (TypeError, ValueError):
            return
        self.failures.append("%s: no exception" % message)

    def parts(self):
        if self._parts is None:
            self._parts = bw.build_parts()
        return self._parts

    # -- cases -----------------------------------------------------------

    def check_float_format_round_trips(self):
        for value in (0.0, 1.0, -1.0, 0.1, 1.0 / 3.0, 0.545590827299,
                      0.19952084794791036, 1e-9, -2.5e7):
            self.ok(float(format_float(value)) == value,
                    "float %r did not round trip" % (value,))

    def check_obj_header_present(self):
        text = obj_document([("Cube",) + bw._unit_box()])
        self.ok(text.startswith("# " + GENERATOR_TAG),
                "OBJ does not carry the generator tag")
        self.ok(text.endswith("\n"), "OBJ does not end with a newline")

    def check_obj_record_counts(self):
        (verts, faces) = bw._unit_box()
        lines = obj_document([("Cube", verts, faces)]).splitlines()
        self.ok(len([x for x in lines if x.startswith("v ")]) == len(verts),
                "vertex record count is wrong")
        self.ok(len([x for x in lines if x.startswith("f ")]) == len(faces),
                "face record count is wrong")
        self.ok(len([x for x in lines if x.startswith("g ")]) == 1,
                "group record count is wrong")

    def check_obj_indices_are_one_based(self):
        (verts, faces) = bw._unit_box()
        lines = obj_document([("Cube", verts, faces)]).splitlines()
        lowest = None
        for line in lines:
            if line.startswith("f "):
                for token in line.split()[1:]:
                    value = int(token)
                    if lowest is None or value < lowest:
                        lowest = value
        self.ok(lowest == 1, "lowest OBJ index is %r, expected 1" % (lowest,))

    def check_obj_round_trip_unit_box(self):
        (verts, faces) = bw._unit_box()
        back = parse_obj(obj_document([("Cube", verts, faces)]))
        self.ok(len(back) == 1, "unit box did not come back as one group")
        (name, got_verts, got_faces) = back[0]
        self.ok(name == "Cube", "group name was lost")
        self.ok(got_verts == [tuple(v) for v in verts],
                "unit box vertices are not bit exact")
        self.ok(got_faces == [tuple(f) for f in faces],
                "unit box faces are not bit exact")

    def check_obj_round_trip_every_part(self):
        for (name, verts, faces) in self.parts():
            back = parse_obj(obj_document([(name, verts, faces)]))
            (got_name, got_verts, got_faces) = back[0]
            self.ok(got_name == name, "%s lost its name" % name)
            self.ok(got_verts == [tuple(v) for v in verts],
                    "%s vertices are not bit exact" % name)
            self.ok(got_faces == [tuple(f) for f in faces],
                    "%s faces are not bit exact" % name)

    def check_round_trip_preserves_volume(self):
        for (name, verts, faces) in self.parts():
            back = parse_obj(obj_document([(name, verts, faces)]))
            (_n, got_verts, got_faces) = back[0]
            before = bw.signed_volume(verts, faces)
            after = bw.signed_volume(got_verts, got_faces)
            self.ok(before == after,
                    "%s changed volume across a round trip" % name)

    def check_round_trip_preserves_diagnostics(self):
        for (name, verts, faces) in self.parts():
            back = parse_obj(obj_document([(name, verts, faces)]))
            (_n, got_verts, got_faces) = back[0]
            before = bw.mesh_diagnostics(verts, faces)
            after = bw.mesh_diagnostics(got_verts, got_faces)
            self.ok(before == after,
                    "%s changed diagnostics across a round trip" % name)

    def check_combined_document_holds_every_part(self):
        parts = self.parts()
        back = parse_obj(obj_document(parts))
        self.ok(len(back) == len(parts),
                "combined document lost a group: %d of %d"
                % (len(back), len(parts)))
        for (index, (name, verts, faces)) in enumerate(parts):
            (got_name, got_verts, got_faces) = back[index]
            self.ok(got_name == name, "group %d is out of order" % index)
            self.ok(got_verts == [tuple(v) for v in verts],
                    "%s moved inside the combined document" % name)
            self.ok(got_faces == [tuple(f) for f in faces],
                    "%s faces shifted inside the combined document" % name)

    def check_combined_offsets_are_cumulative(self):
        parts = self.parts()
        text = obj_document(parts)
        highest = 0
        for line in text.splitlines():
            if line.startswith("f "):
                for token in line.split()[1:]:
                    value = int(token)
                    if value > highest:
                        highest = value
        total = sum(len(verts) for (_n, verts, _f) in parts)
        self.ok(highest == total,
                "highest index %d does not match %d vertices"
                % (highest, total))

    def check_ply_header_is_well_formed(self):
        (name, verts, faces) = self.parts()[0]
        text = ply_document(name, verts, faces)
        lines = text.splitlines()
        self.ok(lines[0] == "ply", "PLY magic is missing")
        self.ok(lines[1] == "format ascii 1.0", "PLY format line is wrong")
        self.ok("end_header" in lines, "PLY header is not terminated")

    def check_ply_counts_match_the_mesh(self):
        for (name, verts, faces) in self.parts():
            text = ply_document(name, verts, faces)
            counts = ply_header_fields(text)
            self.ok(counts.get("vertex") == len(verts),
                    "%s PLY vertex count is wrong" % name)
            self.ok(counts.get("face") == len(faces),
                    "%s PLY face count is wrong" % name)

    def check_ply_body_line_count(self):
        (name, verts, faces) = self.parts()[0]
        lines = ply_document(name, verts, faces).splitlines()
        header = lines.index("end_header")
        body = len(lines) - header - 1
        self.ok(body == len(verts) + len(faces),
                "PLY body has %d lines, expected %d"
                % (body, len(verts) + len(faces)))

    def check_ply_face_records_are_zero_based(self):
        (name, verts, faces) = self.parts()[0]
        lines = ply_document(name, verts, faces).splitlines()
        header = lines.index("end_header")
        record = lines[header + 1 + len(verts)]
        tokens = record.split()
        self.ok(int(tokens[0]) == len(faces[0]),
                "PLY face arity prefix is wrong")
        self.ok(tokens[1:] == [str(i) for i in faces[0]],
                "PLY face indices are not zero based")

    def check_collision_proxies_export(self):
        proxies = bw.collision_proxies()
        self.ok(len(proxies) > 0, "there are no collision proxies to export")
        back = parse_obj(obj_document(proxies))
        self.ok(len(back) == len(proxies), "a collision proxy was lost")
        for (index, (name, verts, faces)) in enumerate(proxies):
            self.ok(back[index][1] == [tuple(v) for v in verts],
                    "%s moved across a round trip" % name)

    def check_export_plan_shape(self):
        plan = export_plan()
        stems = [stem for (stem, _groups) in plan]
        self.ok(len(stems) == len(set(stems)),
                "the export plan has a duplicate stem")
        self.ok(COMBINED_STEM in stems, "the combined export is missing")
        self.ok(COLLISION_STEM in stems, "the collision export is missing")
        self.ok(len(plan) == len(self.parts()) + 2,
                "the export plan has %d entries, expected %d"
                % (len(plan), len(self.parts()) + 2))

    def check_names_avoid_prohibited_tokens(self):
        for (stem, _groups) in export_plan():
            for token in bw.cfg.PROHIBITED_NAME_TOKENS:
                self.ok(token not in stem,
                        "%s carries the prohibited token %s" % (stem, token))

    def check_writer_is_deterministic(self):
        parts = self.parts()
        first = obj_document(parts)
        second = obj_document(bw.build_parts())
        self.ok(first == second, "two builds serialised differently")

    def check_writer_rejects_broken_meshes(self):
        (verts, faces) = bw._unit_box()
        self.raises(lambda: format_obj("X", [], faces), "empty vertices")
        self.raises(lambda: format_obj("X", verts, []), "empty faces")
        self.raises(lambda: format_obj("X", verts, [(0, 1)]), "two corners")
        self.raises(lambda: format_obj("X", verts, [(0, 1, 999)]),
                    "index out of range")
        self.raises(lambda: format_obj("X", verts, [(0, 1, 2.0)]),
                    "float index")

    def check_parser_rejects_broken_documents(self):
        self.raises(lambda: parse_obj("v 0 0 0\nf 1 2 3\n"),
                    "face before a group")
        self.raises(lambda: parse_obj("g A\no A\nv 0 0\nf 1 2 3\n"),
                    "short vertex record")
        self.raises(lambda: parse_obj("g A\no B\nv 0 0 0\n"),
                    "g and o disagree")
        self.raises(lambda: parse_obj("g A\no A\nv 0 0 0\nf 0 1 2\n"),
                    "zero based index")
        self.raises(lambda: parse_obj("g A\no A\nv 0 0 0\nvt 1 1\n"),
                    "unsupported record")

    def check_parser_tolerates_comments_and_blanks(self):
        (verts, faces) = bw._unit_box()
        text = obj_document([("Cube", verts, faces)])
        noisy = "\n\n# a comment\n" + text + "\n   \n# trailing\n"
        back = parse_obj(noisy)
        self.ok(len(back) == 1, "comments confused the parser")
        self.ok(back[0][1] == [tuple(v) for v in verts],
                "comments perturbed the vertices")

    # -- runner ----------------------------------------------------------

    def run(self):
        names = [name for name in sorted(dir(self))
                 if name.startswith("check_")]
        if len(names) != len(set(names)):
            raise AssertionError("duplicate case name")
        passed = 0
        for name in names:
            before = len(self.failures)
            getattr(self, name)()
            if len(self.failures) == before:
                passed += 1
        return (passed, self.failures, len(names))


def _self_test():
    suite = _ExportSelfTest()
    (passed, failures, total) = suite.run()
    sys.stdout.write("af_mesh_export: %d cases, %d assertions, %d failures\n"
                     % (total, suite.assertions, len(failures)))
    for failure in failures:
        sys.stdout.write("  FAIL %s\n" % failure)
    plan = export_plan()
    faces = sum(len(f) for (_s, groups) in plan for (_n, _v, f) in groups)
    sys.stdout.write("export plan: %d files, %d serialised faces\n"
                     % (len(plan), faces))
    return 0 if not failures and passed == total else 1


def main(argv):
    if len(argv) >= 2 and argv[1] == "--self-test":
        return _self_test()
    if len(argv) >= 3 and argv[1] == "--dump":
        written = dump_parts(argv[2])
        for name in written:
            sys.stdout.write("%s\n" % name)
        sys.stdout.write("wrote %d files to %s\n" % (len(written), argv[2]))
        return 0
    sys.stdout.write("usage: af_mesh_export.py --self-test | --dump <dir>\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
