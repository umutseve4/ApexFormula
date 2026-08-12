#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Uludag Formula - self test for the procedural bodywork surface module.

This file holds the whole test suite for af_bodywork_profile. It lives in
its own module for one reason: the geometry module and its proof are
reviewed by different people at different times, and keeping them apart
means a change to the tests can never be mistaken for a change to the car.

It is pure Python. It imports no Blender API and no third party package,
so it runs in the static validation job as well as inside Blender.

Run it through the geometry module:

    python3 af_bodywork_profile.py --self-test

Decision reference: D-044.
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import af_pipeline_config as cfg  # noqa: E402

from af_bodywork_profile import (  # noqa: E402
    BUDGET,
    COLLISION_BASE_NAME,
    EPS_CONVEX_M,
    EPS_UV,
    HALO_APEX_CLEARANCE_M,
    HALO_TUBE_STATIONS,
    _THICKNESS_PEAK,
    _d,
    _dented_box,
    _reserved_marks,
    _thickness_shape,
    _unit_box,
    budget_report,
    build_parts,
    chassis_span_x,
    collision_proxies,
    convexity_report,
    diagnostics_report,
    envelope_report,
    halo_apex_z_m,
    halo_arc_height_m,
    halo_base_z_m,
    halo_thetas,
    halo_tube_radius_m,
    is_closed_manifold,
    is_convex,
    lod_plan,
    loft,
    mesh_diagnostics,
    nose_tip_x,
    planar_uvs,
    section_points,
    signed_volume,
    superellipse_ring,
    tail_x,
    uv_face_area,
)


class BodyworkSelfTest(object):
    """A tiny test runner so the module depends on nothing but the standard
    library. Methods whose name starts with check_ are the cases."""

    def __init__(self):
        self.passed = 0
        self.failed = []

    # -- assertions ------------------------------------------------------

    def ok(self, condition, message):
        if condition:
            self.passed += 1
        else:
            self.failed.append(message)

    def close(self, value, expected, tol, message):
        self.ok(abs(value - expected) <= tol,
                "%s (got %r, expected %r +/- %r)"
                % (message, value, expected, tol))

    def raises(self, func, message):
        try:
            func()
        except Exception:
            self.passed += 1
            return
        self.failed.append(message)

    # -- section maths ---------------------------------------------------

    def check_section_peak_thickness(self):
        # The shape is normalised so that its true peak equals the requested
        # half thickness. A caller sampling a finite number of stations will
        # land near the peak, never past it, and closer as the count rises.
        # Cosine spacing does not straddle the peak monotonically, so the
        # guarantee is a bound plus convergence, not a monotone sequence.
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

    def check_section_rejects_odd_and_small(self):
        self.raises(lambda: section_points(7, 1.0, 0.1, 0.0),
                    "an odd point count must be rejected")
        self.raises(lambda: section_points(4, 1.0, 0.1, 0.0),
                    "fewer than six points must be rejected")
        self.raises(lambda: section_points(-2, 1.0, 0.1, 0.0),
                    "a negative point count must be rejected")

    def check_section_emits_no_duplicates(self):
        # The leading and trailing edge samples are shared by the upper and
        # lower surfaces, so a request for N stations per surface yields a
        # closed outline of N minus two unique points.
        for count in (6, 10, 24):
            pts = section_points(count, 1.2, 0.09, 0.02)
            self.ok(len(pts) == count - 2,
                    "section drops the two shared edge samples")
            rounded = set((round(u, 9), round(v, 9)) for (u, v) in pts)
            self.ok(len(rounded) == len(pts),
                    "no section vertex is emitted twice")

    def check_section_chord_extent(self):
        pts = section_points(20, 1.5, 0.08, 0.0)
        us = [u for (u, _v) in pts]
        self.close(min(us), 0.0, 1e-9, "section starts at the leading edge")
        self.close(max(us), 1.5, 1e-9, "section ends at the chord length")

    def check_section_camber_raises_mean_line(self):
        flat = section_points(20, 1.0, 0.08, 0.0)
        curved = section_points(20, 1.0, 0.08, 0.05)
        flat_mid = sum(v for (_u, v) in flat) / len(flat)
        curved_mid = sum(v for (_u, v) in curved) / len(curved)
        self.ok(curved_mid > flat_mid + 1e-6,
                "camber raises the mean line of the section")

    def check_thickness_shape_endpoints(self):
        self.close(_thickness_shape(0.0), 0.0, 1e-12,
                   "thickness shape closes at the leading edge")
        self.close(_thickness_shape(1.0), 0.0, 1e-12,
                   "thickness shape closes at the trailing edge")
        self.ok(_THICKNESS_PEAK > 0.0,
                "the thickness normaliser is positive")

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
        soft_area = sum(abs(y * z) for (y, z) in soft)
        firm_area = sum(abs(y * z) for (y, z) in firm)
        self.ok(firm_area > soft_area,
                "a higher exponent gives a fuller section")

    # -- loft ------------------------------------------------------------

    def check_loft_rejections(self):
        ring = superellipse_ring(8, 0.2, 0.2, 3.0)
        rings = [[(0.0, y, z) for (y, z) in ring]]
        self.raises(lambda: loft(rings), "a single ring loft must be rejected")
        ragged = [
            [(0.0, y, z) for (y, z) in ring],
            [(1.0, y, z) for (y, z) in superellipse_ring(6, 0.2, 0.2, 3.0)],
        ]
        self.raises(lambda: loft(ragged),
                    "rings of unequal width must be rejected")

    def check_loft_face_and_vertex_count(self):
        ring = superellipse_ring(12, 0.3, 0.2, 3.0)
        rings = [[(float(i), y, z) for (y, z) in ring] for i in range(4)]
        verts, faces = loft(rings)
        self.ok(len(verts) == 48, "loft vertex count is rings times width")
        self.ok(len(faces) == 3 * 12 + 2,
                "loft face count is the side quads plus two caps")

    def check_loft_is_closed(self):
        ring = superellipse_ring(10, 0.3, 0.2, 3.0)
        rings = [[(float(i) * 0.5, y, z) for (y, z) in ring] for i in range(3)]
        verts, faces = loft(rings)
        diag = mesh_diagnostics(verts, faces)
        self.ok(is_closed_manifold(diag), "a plain loft is a closed manifold")

    # -- diagnostics -----------------------------------------------------

    def check_unit_box_diagnostics(self):
        verts, faces = _unit_box()
        diag = mesh_diagnostics(verts, faces)
        self.ok(diag["euler"] == 2, "the control box has Euler number two")
        self.ok(diag["non_manifold_edges"] == 0,
                "the control box has no non manifold edges")
        self.ok(diag["boundary_edges"] == 0,
                "the control box has no boundary edges")
        self.ok(diag["signed_volume"] > 0.0,
                "the control box is wound outward")
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
        flipped = [tuple(reversed(f)) for f in faces]
        diag = mesh_diagnostics(verts, flipped)
        self.ok(diag["signed_volume"] < 0.0,
                "reversing every face inverts the volume sign")
        self.ok(not is_closed_manifold(diag),
                "an inward wound solid fails the manifold gate")

    def check_coincident_vertices_are_detected(self):
        verts, faces = _unit_box()
        verts = list(verts) + [verts[0]]
        diag = mesh_diagnostics(verts, faces)
        self.ok(diag["coincident_vertices"] >= 1,
                "a duplicated vertex position is detected")

    def check_convexity_control(self):
        verts, faces = _unit_box()
        self.ok(is_convex(verts, faces), "the control box is convex")
        self.close(convexity_report(verts, faces), 0.0, 1e-9,
                   "the control box has no outward excursion")
        dv, df = _dented_box()
        self.ok(not is_convex(dv, df), "a dented box is not convex")
        self.ok(convexity_report(dv, df) > EPS_CONVEX_M,
                "the dent is reported as a positive excursion")

    # -- halo arithmetic (D-040 discipline) -------------------------------

    def check_halo_apex_respects_the_envelope(self):
        apex = halo_apex_z_m()
        limit = _d("overall_height_m")
        self.ok(apex <= limit + 1e-9,
                "the halo apex stays inside the height envelope")
        self.close(apex, limit - HALO_APEX_CLEARANCE_M, 1e-9,
                   "the halo apex lands on the clearance line")

    def check_halo_arc_includes_tube_thickness(self):
        base = halo_base_z_m()
        radius = halo_tube_radius_m()
        arc = halo_arc_height_m()
        apex = base + arc * (0.5 + max(math.sin(t) for t in halo_thetas()))
        self.close(apex + radius, halo_apex_z_m(), 1e-9,
                   "the solved arc accounts for the tube radius")

    def check_halo_theta_sweep(self):
        thetas = halo_thetas()
        self.ok(len(thetas) == HALO_TUBE_STATIONS,
                "the halo uses the configured station count")
        self.close(max(math.sin(t) for t in thetas), 1.0, 1e-12,
                   "the halo sweep reaches its exact apex sample")

    def check_halo_arc_is_capped(self):
        self.ok(halo_arc_height_m() <= _d("halo_radius_m") + 1e-9,
                "the halo arc never exceeds the configured radius")

    # -- stations --------------------------------------------------------

    def check_station_ordering(self):
        rear_x, front_x = chassis_span_x()
        self.ok(rear_x < front_x, "the survival cell runs rear to front")
        self.ok(front_x < nose_tip_x(), "the nose is ahead of the cell")
        self.ok(tail_x() < rear_x, "the tail is behind the cell")

    def check_station_extremes_match_the_envelope(self):
        half = _d("overall_length_m") / 2.0
        self.close(nose_tip_x(), half, 1e-9,
                   "the nose tip sits on the front envelope face")
        self.close(tail_x(), -half, 1e-9,
                   "the tail sits on the rear envelope face")

    # -- parts -----------------------------------------------------------

    def check_part_names_are_unique(self):
        names = [name for (name, _v, _f) in build_parts()]
        self.ok(len(names) == len(set(names)), "part names are unique")
        self.ok(len(names) == 12, "the body is built from twelve parts")

    def check_every_part_is_a_closed_manifold(self):
        for (name, verts, faces) in build_parts():
            diag = mesh_diagnostics(verts, faces)
            self.ok(is_closed_manifold(diag),
                    "%s is a closed outward wound manifold" % name)

    def check_every_part_has_positive_volume(self):
        for (name, verts, faces) in build_parts():
            self.ok(signed_volume(verts, faces) > 0.0,
                    "%s encloses a positive volume" % name)

    def check_every_part_is_within_the_per_part_budget(self):
        limit = BUDGET["part_faces_max"]
        for (name, _verts, faces) in build_parts():
            self.ok(len(faces) <= limit,
                    "%s is within the per part face budget" % name)

    def check_parts_are_symmetric_in_pairs(self):
        parts = dict((name, (v, f)) for (name, v, f) in build_parts())
        pairs = [
            ("AF_Surface_Sidepod_L", "AF_Surface_Sidepod_R"),
            ("AF_Surface_EndplateFront_L", "AF_Surface_EndplateFront_R"),
            ("AF_Surface_EndplateRear_L", "AF_Surface_EndplateRear_R"),
        ]
        for (left, right) in pairs:
            self.ok(left in parts and right in parts,
                    "the pair %s and %s both exist" % (left, right))
            lv = parts[left][0]
            rv = parts[right][0]
            self.ok(len(lv) == len(rv),
                    "%s and %s have equal vertex counts" % (left, right))
            # The two parts are lofted independently, so the mirror holds as
            # a set of positions rather than index by index.
            mirrored = sorted((round(-v[1], 9), round(v[0], 9),
                               round(v[2], 9)) for v in lv)
            actual = sorted((round(v[1], 9), round(v[0], 9),
                             round(v[2], 9)) for v in rv)
            self.ok(mirrored == actual,
                    "%s mirrors %s across the centre line" % (right, left))

    # -- envelope and budget ---------------------------------------------

    def check_envelope_report_passes(self):
        report = envelope_report(build_parts())
        for check in report["checks"]:
            self.ok(check["passed"],
                    "envelope check %r passes" % check["name"])
        self.ok(report["passed"], "the envelope report passes as a whole")

    def check_measured_length_matches_the_design(self):
        bounds = envelope_report(build_parts())["bounds"]
        self.close(bounds["length"], _d("overall_length_m"), 1e-6,
                   "the measured length equals the design length")
        self.ok(bounds["width"] <= _d("overall_width_m") + 1e-9,
                "the measured width is inside the design width")
        self.ok(bounds["max_z"] <= _d("overall_height_m") + 1e-9,
                "the measured height is inside the design height")
        self.ok(bounds["min_z"] >= 0.0,
                "no bodywork vertex passes through the ground plane")

    def check_budget_report_passes(self):
        report = budget_report(build_parts())
        for check in report["checks"]:
            self.ok(check["passed"], "budget check %r passes" % check["name"])
        self.ok(report["total_faces"] <= BUDGET["body_faces_max"],
                "the total face count is inside the budget")
        self.ok(report["total_verts"] <= BUDGET["body_verts_max"],
                "the total vertex count is inside the budget")

    # -- collision --------------------------------------------------------

    def check_collision_names_follow_the_convention(self):
        proxies = collision_proxies()
        self.ok(len(proxies) >= 5, "at least five collision proxies exist")
        self.ok(len(proxies) <= BUDGET["collision_pieces_max"],
                "the collision proxy count is inside the budget")
        for index, (name, _v, _f) in enumerate(proxies, start=1):
            self.ok(name == "UCX_%s_%02d" % (COLLISION_BASE_NAME, index),
                    "%s follows the UCX naming convention" % name)

    def check_every_proxy_is_convex(self):
        for (name, verts, faces) in collision_proxies():
            self.ok(is_convex(verts, faces), "%s is convex" % name)
            self.ok(signed_volume(verts, faces) > 0.0,
                    "%s is wound outward" % name)

    def check_every_proxy_is_a_closed_manifold(self):
        for (name, verts, faces) in collision_proxies():
            diag = mesh_diagnostics(verts, faces)
            self.ok(is_closed_manifold(diag),
                    "%s is a closed manifold" % name)

    def check_proxies_stay_inside_the_envelope(self):
        half = _d("overall_length_m") / 2.0
        tol = cfg.TOLERANCE["length_m"]
        for (name, verts, _f) in collision_proxies():
            self.ok(max(v[0] for v in verts) <= half + tol,
                    "%s stays behind the front envelope face" % name)
            self.ok(min(v[0] for v in verts) >= -half - tol,
                    "%s stays ahead of the rear envelope face" % name)
            self.ok(min(v[2] for v in verts) >= -tol,
                    "%s stays above the ground plane" % name)

    # -- texture coordinates ---------------------------------------------

    def check_uvs_are_inside_the_unit_square(self):
        for (name, verts, faces) in build_parts():
            corners = planar_uvs(verts, faces, 0, 2)
            lo = min(min(min(u, v) for (u, v) in c) for c in corners)
            hi = max(max(max(u, v) for (u, v) in c) for c in corners)
            self.ok(lo >= -EPS_UV, "%s has no UV below zero" % name)
            self.ok(hi <= 1.0 + EPS_UV, "%s has no UV above one" % name)

    def check_uv_area_is_non_zero(self):
        for (name, verts, faces) in build_parts():
            corners = planar_uvs(verts, faces, 0, 2)
            total = sum(uv_face_area(c) for c in corners)
            self.ok(total > 1e-6, "%s has a non zero UV area" % name)

    def check_uv_corner_count_matches_the_faces(self):
        for (name, verts, faces) in build_parts():
            corners = planar_uvs(verts, faces, 0, 2)
            self.ok(len(corners) == len(faces),
                    "%s has one UV polygon per face" % name)
            self.ok(all(len(c) == len(f) for (c, f) in zip(corners, faces)),
                    "%s has one UV per face corner" % name)

    # -- determinism and originality --------------------------------------

    def check_generation_is_deterministic(self):
        first = repr(build_parts())
        second = repr(build_parts())
        self.ok(first == second,
                "two generation runs produce identical geometry")
        self.ok(repr(collision_proxies()) == repr(collision_proxies()),
                "two collision runs produce identical proxies")

    def check_names_carry_no_reserved_marks(self):
        names = [n for (n, _v, _f) in build_parts()]
        names += [n for (n, _v, _f) in collision_proxies()]
        for name in names:
            lowered = name.lower()
            for mark in _reserved_marks():
                self.ok(mark.lower() not in lowered,
                        "%s carries no reserved mark" % name)

    def check_lod_plan_is_complete_and_named(self):
        parts = build_parts()
        plan = lod_plan(parts)
        self.ok(len(plan) == len(parts) * len(cfg.LOD_RATIOS),
                "every part receives every level of detail")
        names = [row[1] for row in plan]
        self.ok(len(set(names)) == len(names),
                "level of detail object names are unique")
        sources = set(row[0] for row in plan)
        self.ok(sources == set(p[0] for p in parts),
                "the plan covers exactly the built parts")
        for (source, lod, ratio) in plan:
            self.ok(lod.startswith(source + "_LOD"),
                    "%s is named after its source" % (lod,))
            self.ok(0.0 < ratio < 1.0,
                    "%s uses a reducing ratio" % (lod,))
        self.ok(plan == lod_plan(build_parts()),
                "the level of detail plan is deterministic")

    def check_report_shape(self):
        report = diagnostics_report(build_parts(), collision_proxies())
        for key in ("module", "variant", "parts", "collision",
                    "envelope", "budget", "summary", "passed"):
            self.ok(key in report, "the report carries the key %r" % key)
        self.ok(report["passed"], "the report passes as a whole")
        self.ok(report["summary"]["all_parts_closed_manifold"],
                "the report agrees that every part is a closed manifold")
        self.ok(report["summary"]["all_proxies_convex"],
                "the report agrees that every proxy is convex")
        self.ok(json.dumps(report) is not None,
                "the report is JSON serialisable")

    # -- runner ------------------------------------------------------------

    def run(self):
        names = [n for n in sorted(dir(self)) if n.startswith("check_")]
        if len(names) != len(set(names)):
            raise AssertionError("duplicate self test method name")
        for name in names:
            getattr(self, name)()
        return self.passed, self.failed, len(names)
