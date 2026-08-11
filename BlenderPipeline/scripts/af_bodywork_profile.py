#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Uludag Formula - procedural bodywork surface module (geometry core).

Slice 1 of the re-authored module. It carries the pure geometry layer only:
section maths, superellipse rings, lofting, mesh diagnostics, convexity and
planar texture coordinates. Nothing in this slice reads the design config and
nothing imports the Blender API, so the module is importable by the static
validation job on a bare Python interpreter.

The design driven layer (stations, halo arithmetic, build_parts,
collision_proxies, budget, level of detail plan, diagnostics report) is not in
this slice. Until it lands, the suite kept on branch milestone-4-bodywork
cannot run; the cases below are this slice's own gate.

Provenance: the previous module of this name was never committed and is lost.
Nothing here is copied from its documentation. Every number reported by
--self-test is measured by the run that prints it.

Run:

    python3 af_bodywork_profile.py --self-test
"""

from __future__ import annotations

import math
import sys

# --------------------------------------------------------------------------
# tolerances
# --------------------------------------------------------------------------

#: Largest outward excursion, in metres, still accepted as convex.
EPS_CONVEX_M = 1.0e-6

#: Slack allowed when asserting that a texture coordinate is in the unit
#: square. Projection arithmetic can land a hair outside on the extremes.
EPS_UV = 1.0e-9

#: Positions closer than this in every axis count as the same point.
EPS_WELD_M = 1.0e-9

_ROUND = 9


# --------------------------------------------------------------------------
# section maths
# --------------------------------------------------------------------------

def _thickness_shape(s):
    """Unnormalised half thickness distribution over a chord fraction.

    Closes at both ends, is fullest ahead of mid chord. The caller divides by
    _THICKNESS_PEAK so that the true peak equals the requested half thickness.
    """
    if s <= 0.0 or s >= 1.0:
        return 0.0
    return math.sqrt(s) * (1.0 - s) * (1.0 + 0.6 * (1.0 - s))


def _solve_thickness_peak(samples=200001):
    """Peak of _thickness_shape, found by a dense sweep then a golden search."""
    best_s, best_v = 0.0, 0.0
    for i in range(samples):
        s = i / float(samples - 1)
        v = _thickness_shape(s)
        if v > best_v:
            best_s, best_v = s, v
    lo = max(0.0, best_s - 1.0 / samples)
    hi = min(1.0, best_s + 1.0 / samples)
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    for _ in range(200):
        a = hi - phi * (hi - lo)
        b = lo + phi * (hi - lo)
        if _thickness_shape(a) < _thickness_shape(b):
            lo = a
        else:
            hi = b
    return _thickness_shape(0.5 * (lo + hi))


#: Value of _thickness_shape at its peak. Used to normalise the section.
_THICKNESS_PEAK = _solve_thickness_peak()


def _camber_line(s, camber):
    """Parabolic mean line, peaking at mid chord."""
    return 4.0 * camber * s * (1.0 - s)


def section_points(count, chord, thickness, camber):
    """Closed outline of an aerofoil like section in the (u, v) plane.

    count is the total number of surface samples requested, split evenly
    between the upper and the lower surface. The leading and the trailing edge
    samples are shared by both surfaces, so the returned outline holds
    count - 2 unique points, ordered upper surface first.
    """
    if not isinstance(count, int):
        raise TypeError("count must be an integer")
    if count < 6:
        raise ValueError("count must be at least six")
    if count % 2 != 0:
        raise ValueError("count must be even")
    if chord <= 0.0:
        raise ValueError("chord must be positive")
    if thickness <= 0.0:
        raise ValueError("thickness must be positive")

    half = count // 2
    half_thickness = 0.5 * thickness
    stations = []
    for i in range(half):
        s = 0.5 * (1.0 - math.cos(math.pi * i / float(half - 1)))
        t = half_thickness * _thickness_shape(s) / _THICKNESS_PEAK
        m = _camber_line(s, camber)
        stations.append((s * chord, m, t))

    points = [(u, m + t) for (u, m, t) in stations]
    for i in range(half - 2, 0, -1):
        u, m, t = stations[i]
        points.append((u, m - t))
    return points


# --------------------------------------------------------------------------
# superellipse
# --------------------------------------------------------------------------

def _signed_pow(value, power):
    if value == 0.0:
        return 0.0
    return math.copysign(abs(value) ** power, value)


def superellipse_ring(count, half_width, half_height, exponent):
    """Closed ring of (y, z) points on a superellipse.

    An exponent of two is a plain ellipse; higher exponents give a fuller,
    squarer section. The ring always starts on the positive width axis.
    """
    if not isinstance(count, int):
        raise TypeError("count must be an integer")
    if count < 4:
        raise ValueError("count must be at least four")
    if half_width <= 0.0:
        raise ValueError("half width must be positive")
    if half_height <= 0.0:
        raise ValueError("half height must be positive")
    if exponent < 2.0:
        raise ValueError("exponent must be at least two")

    power = 2.0 / exponent
    ring = []
    for i in range(count):
        t = 2.0 * math.pi * i / float(count)
        y = half_width * _signed_pow(math.cos(t), power)
        z = half_height * _signed_pow(math.sin(t), power)
        ring.append((y, z))
    return ring


# --------------------------------------------------------------------------
# lofting
# --------------------------------------------------------------------------

def loft(rings):
    """Sweep a sequence of equally wide rings into a closed solid.

    rings is a list of lists of (x, y, z). Side faces are quads, the two ends
    are capped with a single polygon each. The result is wound outward: if the
    supplied ring order sweeps against the outward sense the whole face list is
    reversed, so a caller lofting toward negative X cannot silently produce an
    inward wound solid.
    """
    if len(rings) < 2:
        raise ValueError("a loft needs at least two rings")
    width = len(rings[0])
    if width < 3:
        raise ValueError("a ring needs at least three points")
    for ring in rings:
        if len(ring) != width:
            raise ValueError("every ring must have the same point count")

    verts = []
    for ring in rings:
        for point in ring:
            if len(point) != 3:
                raise ValueError("ring points must be three dimensional")
            verts.append((float(point[0]), float(point[1]), float(point[2])))

    faces = []
    for i in range(len(rings) - 1):
        base = i * width
        nxt = base + width
        for j in range(width):
            k = (j + 1) % width
            faces.append((base + j, base + k, nxt + k, nxt + j))
    last = (len(rings) - 1) * width
    faces.append(tuple(range(last, last + width)))
    faces.append(tuple(reversed(range(0, width))))

    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]
    return verts, faces


# --------------------------------------------------------------------------
# mesh diagnostics
# --------------------------------------------------------------------------

def signed_volume(verts, faces):
    """Six times the signed volume divided by six, by the divergence theorem.

    Positive means the faces are wound counter clockwise seen from outside.
    """
    total = 0.0
    for face in faces:
        if len(face) < 3:
            continue
        a = verts[face[0]]
        for i in range(1, len(face) - 1):
            b = verts[face[i]]
            c = verts[face[i + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total / 6.0


def mesh_diagnostics(verts, faces):
    """Topology and orientation facts about a polygon soup."""
    edge_use = {}
    for face in faces:
        n = len(face)
        for i in range(n):
            a = face[i]
            b = face[(i + 1) % n]
            key = (a, b) if a <= b else (b, a)
            edge_use[key] = edge_use.get(key, 0) + 1

    boundary = sum(1 for c in edge_use.values() if c == 1)
    non_manifold = sum(1 for c in edge_use.values() if c > 2)

    seen = {}
    coincident = 0
    for v in verts:
        key = (round(v[0], _ROUND), round(v[1], _ROUND), round(v[2], _ROUND))
        if key in seen:
            coincident += 1
        else:
            seen[key] = True

    return {
        "vertices": len(verts),
        "faces": len(faces),
        "edges": len(edge_use),
        "euler": len(verts) - len(edge_use) + len(faces),
        "boundary_edges": boundary,
        "non_manifold_edges": non_manifold,
        "coincident_vertices": coincident,
        "signed_volume": signed_volume(verts, faces),
    }


def is_closed_manifold(diag):
    """A mesh passes only if it is closed, manifold, genus zero and outward."""
    return (diag["boundary_edges"] == 0
            and diag["non_manifold_edges"] == 0
            and diag["euler"] == 2
            and diag["coincident_vertices"] == 0
            and diag["signed_volume"] > 0.0)


# --------------------------------------------------------------------------
# convexity
# --------------------------------------------------------------------------

def _face_plane(verts, face):
    """Outward unit normal and offset of a face, or None if degenerate."""
    n = len(face)
    a = verts[face[0]]
    for i in range(1, n - 1):
        b = verts[face[i]]
        c = verts[face[i + 1]]
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length > 1.0e-12:
            return (nx / length, ny / length, nz / length,
                    (nx * a[0] + ny * a[1] + nz * a[2]) / length)
    return None


def convexity_report(verts, faces):
    """Largest distance, in metres, by which a vertex sits outside a face plane."""
    worst = 0.0
    for face in faces:
        plane = _face_plane(verts, face)
        if plane is None:
            continue
        nx, ny, nz, d = plane
        for v in verts:
            excursion = nx * v[0] + ny * v[1] + nz * v[2] - d
            if excursion > worst:
                worst = excursion
    return worst


def is_convex(verts, faces):
    """True when no vertex sits outside the plane of any face."""
    return convexity_report(verts, faces) <= EPS_CONVEX_M


# --------------------------------------------------------------------------
# control solids used by the tests
# --------------------------------------------------------------------------

def _unit_box():
    """Axis aligned unit cube on the origin, wound outward."""
    verts = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0),
    ]
    faces = [
        (0, 3, 2, 1),   # bottom, normal -Z
        (4, 5, 6, 7),   # top, normal +Z
        (0, 1, 5, 4),   # front, normal -Y
        (1, 2, 6, 5),   # right, normal +X
        (2, 3, 7, 6),   # back, normal +Y
        (3, 0, 4, 7),   # left, normal -X
    ]
    return verts, faces


def _dented_box():
    """Unit cube whose top face is pushed inward, so it is not convex."""
    verts, faces = _unit_box()
    verts = list(verts) + [(0.5, 0.5, 0.8)]
    centre = len(verts) - 1
    faces = [f for f in faces if f != (4, 5, 6, 7)]
    faces += [
        (4, 5, centre),
        (5, 6, centre),
        (6, 7, centre),
        (7, 4, centre),
    ]
    return verts, faces


# --------------------------------------------------------------------------
# texture coordinates
# --------------------------------------------------------------------------

def planar_uvs(verts, faces, axis_u, axis_v):
    """Project a mesh onto two axes and normalise into the unit square.

    Returns one list of (u, v) per face, in face corner order.
    """
    if axis_u == axis_v:
        raise ValueError("the two projection axes must differ")
    for axis in (axis_u, axis_v):
        if axis not in (0, 1, 2):
            raise ValueError("a projection axis must be 0, 1 or 2")
    if not verts:
        raise ValueError("an empty mesh has no texture coordinates")

    lo_u = min(v[axis_u] for v in verts)
    hi_u = max(v[axis_u] for v in verts)
    lo_v = min(v[axis_v] for v in verts)
    hi_v = max(v[axis_v] for v in verts)
    span_u = hi_u - lo_u
    span_v = hi_v - lo_v
    if span_u <= EPS_WELD_M or span_v <= EPS_WELD_M:
        raise ValueError("the mesh is flat along a projection axis")

    corners = []
    for face in faces:
        corners.append([((verts[i][axis_u] - lo_u) / span_u,
                         (verts[i][axis_v] - lo_v) / span_v) for i in face])
    return corners


def uv_face_area(corners):
    """Absolute area of one texture polygon, by the shoelace formula."""
    total = 0.0
    n = len(corners)
    for i in range(n):
        u0, v0 = corners[i]
        u1, v1 = corners[(i + 1) % n]
        total += u0 * v1 - u1 * v0
    return abs(total) / 2.0


# --------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------

class _SliceOneSelfTest(object):
    """Gate for the geometry core. Methods named check_ are the cases."""

    def __init__(self):
        self.passed = 0
        self.failed = []

    def ok(self, condition, message):
        if condition:
            self.passed += 1
        else:
            self.failed.append(message)

    def close(self, value, expected, tol, message):
        self.ok(abs(value - expected) <= tol,
                "%s (got %r, expected %r +/- %r)" % (message, value,
                                                     expected, tol))

    def raises(self, func, message):
        try:
            func()
        except Exception:
            self.passed += 1
            return
        self.failed.append(message)

    # -- section ---------------------------------------------------------

    def check_thickness_shape_closes(self):
        self.close(_thickness_shape(0.0), 0.0, 1e-12,
                   "thickness shape closes at the leading edge")
        self.close(_thickness_shape(1.0), 0.0, 1e-12,
                   "thickness shape closes at the trailing edge")
        self.ok(_THICKNESS_PEAK > 0.0, "the thickness normaliser is positive")
        self.ok(_thickness_shape(0.25) > _thickness_shape(0.75),
                "the section is fullest ahead of mid chord")

    def check_section_point_count(self):
        for count in (6, 10, 24):
            pts = section_points(count, 1.2, 0.09, 0.02)
            self.ok(len(pts) == count - 2,
                    "section drops the two shared edge samples")
            rounded = set((round(u, 9), round(v, 9)) for (u, v) in pts)
            self.ok(len(rounded) == len(pts),
                    "no section vertex is emitted twice")

    def check_section_rejections(self):
        self.raises(lambda: section_points(7, 1.0, 0.1, 0.0),
                    "an odd point count must be rejected")
        self.raises(lambda: section_points(4, 1.0, 0.1, 0.0),
                    "fewer than six points must be rejected")
        self.raises(lambda: section_points(-2, 1.0, 0.1, 0.0),
                    "a negative point count must be rejected")
        self.raises(lambda: section_points(12, 0.0, 0.1, 0.0),
                    "a zero chord must be rejected")
        self.raises(lambda: section_points(12, 1.0, -0.1, 0.0),
                    "a negative thickness must be rejected")

    def check_section_chord_extent(self):
        pts = section_points(20, 1.5, 0.08, 0.0)
        us = [u for (u, _v) in pts]
        self.close(min(us), 0.0, 1e-9, "section starts at the leading edge")
        self.close(max(us), 1.5, 1e-9, "section ends at the chord length")

    def check_section_peak_thickness(self):
        for count in (6, 12, 24, 40):
            pts = section_points(count, 1.0, 0.10, 0.0)
            half = max(abs(v) for (_u, v) in pts)
            self.ok(half <= 0.05 + 1e-12,
                    "sampled half thickness never exceeds the requested peak")
        for count in (24, 40):
            pts = section_points(count, 1.0, 0.10, 0.0)
            self.ok(max(abs(v) for (_u, v) in pts) > 0.0495,
                    "a realistic station count lands close to the peak")
        dense = section_points(400, 1.0, 0.10, 0.0)
        self.close(max(abs(v) for (_u, v) in dense), 0.05, 1e-4,
                   "dense sampling converges on the requested peak")

    def check_section_camber_raises_mean_line(self):
        flat = section_points(20, 1.0, 0.08, 0.0)
        curved = section_points(20, 1.0, 0.08, 0.05)
        flat_mid = sum(v for (_u, v) in flat) / len(flat)
        curved_mid = sum(v for (_u, v) in curved) / len(curved)
        self.ok(curved_mid > flat_mid + 1e-6,
                "camber raises the mean line of the section")

    # -- superellipse ----------------------------------------------------

    def check_superellipse_extents(self):
        ring = superellipse_ring(16, 0.4, 0.25, 3.2)
        self.ok(len(ring) == 16, "superellipse returns the requested count")
        self.close(max(abs(y) for (y, _z) in ring), 0.4, 1e-9,
                   "superellipse reaches its half width")
        self.close(max(abs(z) for (_y, z) in ring), 0.25, 1e-9,
                   "superellipse reaches its half height")

    def check_superellipse_rejections(self):
        self.raises(lambda: superellipse_ring(3, 0.4, 0.2, 3.0),
                    "fewer than four ring points must be rejected")
        self.raises(lambda: superellipse_ring(8, 0.0, 0.2, 3.0),
                    "a zero half width must be rejected")
        self.raises(lambda: superellipse_ring(8, 0.4, -0.2, 3.0),
                    "a negative half height must be rejected")
        self.raises(lambda: superellipse_ring(8, 0.4, 0.2, 1.5),
                    "an exponent below two must be rejected")

    def check_superellipse_is_fuller_than_an_ellipse(self):
        soft = superellipse_ring(64, 1.0, 1.0, 2.0)
        firm = superellipse_ring(64, 1.0, 1.0, 4.0)
        self.ok(sum(abs(y * z) for (y, z) in firm)
                > sum(abs(y * z) for (y, z) in soft),
                "a higher exponent gives a fuller section")

    # -- loft ------------------------------------------------------------

    def check_loft_rejections(self):
        ring = superellipse_ring(8, 0.2, 0.2, 3.0)
        self.raises(lambda: loft([[(0.0, y, z) for (y, z) in ring]]),
                    "a single ring loft must be rejected")
        ragged = [
            [(0.0, y, z) for (y, z) in ring],
            [(1.0, y, z) for (y, z) in superellipse_ring(6, 0.2, 0.2, 3.0)],
        ]
        self.raises(lambda: loft(ragged),
                    "rings of unequal width must be rejected")

    def check_loft_counts(self):
        ring = superellipse_ring(12, 0.3, 0.2, 3.0)
        rings = [[(float(i), y, z) for (y, z) in ring] for i in range(4)]
        verts, faces = loft(rings)
        self.ok(len(verts) == 48, "loft vertex count is rings times width")
        self.ok(len(faces) == 3 * 12 + 2,
                "loft face count is the side quads plus two caps")

    def check_loft_is_closed(self):
        ring = superellipse_ring(10, 0.3, 0.2, 3.0)
        rings = [[(float(i) * 0.5, y, z) for (y, z) in ring]
                 for i in range(3)]
        verts, faces = loft(rings)
        self.ok(is_closed_manifold(mesh_diagnostics(verts, faces)),
                "a plain loft is a closed manifold")

    def check_loft_toward_negative_x_is_still_outward(self):
        # The defect this case exists for: sweeping the rings the other way
        # reverses the sense of every side quad. The loft must correct it.
        ring = superellipse_ring(10, 0.3, 0.2, 3.0)
        forward = loft([[(float(i) * 0.5, y, z) for (y, z) in ring]
                        for i in range(3)])
        backward = loft([[(-float(i) * 0.5, y, z) for (y, z) in ring]
                         for i in range(3)])
        self.ok(signed_volume(*forward) > 0.0,
                "a forward loft encloses a positive volume")
        self.ok(signed_volume(*backward) > 0.0,
                "a backward loft encloses a positive volume")
        self.close(signed_volume(*backward), signed_volume(*forward), 1e-12,
                   "sweep direction does not change the enclosed volume")
        self.ok(is_closed_manifold(mesh_diagnostics(*backward)),
                "a backward loft passes the manifold gate")

    # -- diagnostics -----------------------------------------------------

    def check_unit_box_diagnostics(self):
        verts, faces = _unit_box()
        diag = mesh_diagnostics(verts, faces)
        self.ok(diag["euler"] == 2, "the control box has Euler number two")
        self.ok(diag["edges"] == 12, "the control box has twelve edges")
        self.ok(diag["non_manifold_edges"] == 0,
                "the control box has no non manifold edges")
        self.ok(diag["boundary_edges"] == 0,
                "the control box has no boundary edges")
        self.close(diag["signed_volume"], 1.0, 1e-12,
                   "the control box encloses unit volume")
        self.ok(is_closed_manifold(diag),
                "the control box passes the manifold gate")

    def check_open_mesh_is_rejected(self):
        verts, faces = _unit_box()
        diag = mesh_diagnostics(verts, faces[:-1])
        self.ok(diag["boundary_edges"] > 0,
                "removing a face opens the surface")
        self.ok(not is_closed_manifold(diag),
                "an open surface fails the manifold gate")

    def check_inverted_winding_is_rejected(self):
        verts, faces = _unit_box()
        diag = mesh_diagnostics(verts, [tuple(reversed(f)) for f in faces])
        self.ok(diag["signed_volume"] < 0.0,
                "reversing every face inverts the volume sign")
        self.ok(diag["boundary_edges"] == 0,
                "an inward wound solid is still closed")
        self.ok(not is_closed_manifold(diag),
                "an inward wound solid fails the manifold gate")

    def check_coincident_vertices_are_detected(self):
        verts, faces = _unit_box()
        diag = mesh_diagnostics(list(verts) + [verts[0]], faces)
        self.ok(diag["coincident_vertices"] >= 1,
                "a duplicated vertex position is detected")
        self.ok(not is_closed_manifold(diag),
                "a mesh with a duplicated vertex fails the gate")

    def check_convexity_control(self):
        verts, faces = _unit_box()
        self.ok(is_convex(verts, faces), "the control box is convex")
        self.close(convexity_report(verts, faces), 0.0, 1e-9,
                   "the control box has no outward excursion")
        dv, df = _dented_box()
        self.ok(not is_convex(dv, df), "a dented box is not convex")
        self.ok(convexity_report(dv, df) > EPS_CONVEX_M,
                "the dent is reported as a positive excursion")
        self.ok(is_closed_manifold(mesh_diagnostics(dv, df)),
                "the dented box is still a closed manifold")

    # -- texture coordinates ---------------------------------------------

    def check_uvs_are_inside_the_unit_square(self):
        verts, faces = _unit_box()
        corners = planar_uvs(verts, faces, 0, 2)
        lo = min(min(min(u, v) for (u, v) in c) for c in corners)
        hi = max(max(max(u, v) for (u, v) in c) for c in corners)
        self.ok(lo >= -EPS_UV, "no texture coordinate falls below zero")
        self.ok(hi <= 1.0 + EPS_UV, "no texture coordinate rises above one")

    def check_uv_shape_and_area(self):
        verts, faces = _unit_box()
        corners = planar_uvs(verts, faces, 0, 2)
        self.ok(len(corners) == len(faces),
                "there is one texture polygon per face")
        self.ok(all(len(c) == len(f) for (c, f) in zip(corners, faces)),
                "there is one texture coordinate per face corner")
        self.ok(sum(uv_face_area(c) for c in corners) > 1e-6,
                "the projected texture area is not degenerate")
        self.close(uv_face_area([(0.0, 0.0), (1.0, 0.0),
                                 (1.0, 1.0), (0.0, 1.0)]), 1.0, 1e-12,
                   "the unit square has unit texture area")

    def check_uv_rejections(self):
        verts, faces = _unit_box()
        self.raises(lambda: planar_uvs(verts, faces, 1, 1),
                    "two equal projection axes must be rejected")
        self.raises(lambda: planar_uvs(verts, faces, 0, 3),
                    "an out of range projection axis must be rejected")
        flat = [(x, y, 0.0) for (x, y, _z) in verts]
        self.raises(lambda: planar_uvs(flat, faces, 0, 2),
                    "a mesh flat along a projection axis must be rejected")

    # -- determinism -----------------------------------------------------

    def check_generation_is_deterministic(self):
        self.ok(section_points(24, 1.0, 0.1, 0.02)
                == section_points(24, 1.0, 0.1, 0.02),
                "two section runs produce identical points")
        self.ok(superellipse_ring(24, 0.4, 0.3, 3.2)
                == superellipse_ring(24, 0.4, 0.3, 3.2),
                "two ring runs produce identical points")
        ring = superellipse_ring(12, 0.3, 0.2, 3.0)
        rings = [[(float(i), y, z) for (y, z) in ring] for i in range(3)]
        self.ok(loft(rings) == loft(rings),
                "two loft runs produce identical geometry")

    def run(self):
        names = [n for n in sorted(dir(self)) if n.startswith("check_")]
        for name in names:
            getattr(self, name)()
        return self.passed, self.failed, len(names)


def _self_test():
    runner = _SliceOneSelfTest()
    passed, failed, cases = runner.run()
    for message in failed:
        sys.stderr.write("FAIL: %s\n" % message)
    sys.stdout.write(
        "af_bodywork_profile slice 1: %d cases, %d assertions, %d failures\n"
        % (cases, passed, len(failed)))
    sys.stdout.write("thickness peak: %.12f\n" % _THICKNESS_PEAK)
    return 0 if not failed else 1


def main(argv):
    if "--self-test" in argv:
        return _self_test()
    sys.stderr.write("usage: af_bodywork_profile.py --self-test\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
