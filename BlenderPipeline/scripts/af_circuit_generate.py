"""ApexFormula - original test circuit generator.

Milestone 3, output "test circuit geometry".

WHAT THIS IS
------------
A closed-loop circuit centreline is built from an ORIGINAL fictional polygon
with filleted corners, then sampled into a drivable ribbon and a checkpoint
table that matches the ``UAFTrackDefinition`` contract in
``Unreal/Source/ApexFormulaRace/Public/AFTrackDefinition.h``.

The layout maths is pure Python and needs no Blender. ``bpy`` is imported
defensively and is used only by :func:`build_in_blender`, which is the sole
function that touches a scene. That split is deliberate: it lets the geometry
be EXECUTED and checked in the engine-free CI job instead of merely
byte-compiled.

WHAT THIS PROVES
----------------
Run with ``--self-test`` it proves, by execution:

  * the centreline closes on itself (start point == end point, and the total
    signed turning is exactly one full revolution);
  * lap length equals the sum of straight and arc pieces, independently
    recomputed from the sampled polyline;
  * every straight piece has positive length, i.e. no fillet radius eats its
    neighbour;
  * checkpoint stations are strictly increasing around the lap and index 0 is
    the timing line;
  * the emitted track definition satisfies a faithful Python mirror of
    ``UAFTrackDefinition::ValidateSelf()``;
  * sector closing indices obey the C++ rule that the final sector closes at
    the timing line;
  * generation is deterministic - identical input gives byte-identical output;
  * no checkpoint, track id or display string reproduces a real venue.

WHAT THIS DOES NOT PROVE
------------------------
  * It does NOT prove the C++ compiles. Nothing here is compiled.
  * It does NOT prove the ribbon mesh looks correct, is drivable, or imports
    into Unreal. That is "requires Blender execution" and "requires Unreal
    Editor verification".
  * The mirror of ``ValidateSelf()`` is still WRITTEN by hand, but since
    D-045 it is no longer UNGUARDED: ``Tools/af_track_drift_guard.py`` runs
    in CI and fails the build if the diagnostic messages, the predicates or
    the field names drift apart from ``AFTrackDefinition.cpp``. That guard is
    TEXT-ONLY - it does not compile or execute the C++, so behavioural
    equivalence is NOT proven and identical drift applied to both sides at
    once would pass unnoticed. See D-043 for the original risk and D-045 for
    the control.

ORIGINALITY
-----------
The layout is generated from ApexFormula design values invented for this
project. It is not traced from, measured against, or named after any real
circuit. Criterion 5 of Milestone 3.

Usage
-----
    python3 af_circuit_generate.py --self-test
    python3 af_circuit_generate.py --dump
    blender --background --python af_circuit_generate.py

Exit codes: 0 ok, 1 a self-test case failed, 2 bad invocation.
"""

from __future__ import annotations

import json
import math
import sys

try:
    import bpy
except ImportError:  # pragma: no cover - only present inside Blender
    bpy = None


EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

RULE = "=" * 70

# Numerical tolerances. Metres unless stated.
CLOSURE_TOLERANCE_M = 1e-6
LENGTH_TOLERANCE_M = 0.5
TURN_TOLERANCE_RAD = 1e-9


# ---------------------------------------------------------------------------
# Circuit design values
#
# ApexFormula design values. Invented for this project. Not measurements of
# any real venue. Cross-Milestone Rule 7 binds VEHICLE dimensions to
# af_pipeline_config.DESIGN; circuit layout is a separate concern and lives
# here (decision D-043).
# ---------------------------------------------------------------------------

TRACK_ID = "af_test_crescent"
TRACK_DISPLAY_NAME = "Crescent Vale Test Circuit"
TRACK_REGION_NAME = "Vale Province"

TRACK_WIDTH_M = 13.0
GRID_SLOT_COUNT = 20
PIT_LANE_SPEED_LIMIT_KPH = 80.0
HAS_PIT_LANE = True

# Sampling resolution of the centreline.
STRAIGHT_STEP_M = 8.0
ARC_STEP_RAD = math.radians(3.0)

# Closed polygon of corner vertices, metres, counter-clockwise.
# (x, y, fillet_radius_m)
CIRCUIT_VERTICES = (
    (0.0, 0.0, 95.0),
    (620.0, 0.0, 70.0),
    (860.0, 150.0, 55.0),
    (860.0, 420.0, 80.0),
    (700.0, 560.0, 45.0),
    (700.0, 760.0, 90.0),
    (300.0, 900.0, 110.0),
    (-140.0, 780.0, 65.0),
    (-260.0, 560.0, 75.0),
    (-180.0, 320.0, 60.0),
    (-320.0, 180.0, 85.0),
    (-180.0, 20.0, 70.0),
)

# Checkpoint order. Index 0 is the timing line. Neutral AF_CP_ prefix only.
# ``station_fraction`` is the position around the lap, 0.0 at the timing line.
CHECKPOINT_LAYOUT = (
    ("AF_CP_Line", 0.0),
    ("AF_CP_Alpha", 0.16),
    ("AF_CP_Bravo", 0.33),
    ("AF_CP_Charlie", 0.50),
    ("AF_CP_Delta", 0.66),
    ("AF_CP_Echo", 0.83),
)

# Sectors, in ascending index order. Each entry is the CheckpointOrder index
# that CLOSES the sector. The final sector must close at the timing line, 0.
SECTOR_CLOSING_INDICES = (2, 4, 0)
SECTOR_DISPLAY_NAMES = ("Sector 1", "Sector 2", "Sector 3")

# Strings that must never appear anywhere in the generated output.
PROHIBITED_SUBSTRINGS = (
    "f1", "fia", "formulaone", "formula1", "formula 1", "formula-1",
    "formula_1", "grandprix", "grand prix", "grand-prix", "grand_prix",
)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _normalise_angle(angle):
    """Wrap an angle into (-pi, pi]."""
    wrapped = math.fmod(angle + math.pi, 2.0 * math.pi)
    if wrapped <= 0.0:
        wrapped += 2.0 * math.pi
    return wrapped - math.pi


def _distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _unit(a, b):
    length = _distance(a, b)
    if length <= 0.0:
        raise ValueError("coincident vertices: %r and %r" % (a, b))
    return ((b[0] - a[0]) / length, (b[1] - a[1]) / length)


# ---------------------------------------------------------------------------
# Centreline construction
# ---------------------------------------------------------------------------

def build_corners(vertices=CIRCUIT_VERTICES):
    """Resolve each polygon vertex into a fillet arc.

    Returns a list of dicts describing, per corner, the arc centre, radius,
    signed turn, tangent length and the two tangent points.
    """
    count = len(vertices)
    if count < 3:
        raise ValueError("a circuit needs at least 3 vertices, got %d" % count)

    corners = []
    for index in range(count):
        previous = vertices[index - 1]
        current = vertices[index]
        following = vertices[(index + 1) % count]

        incoming = _unit(previous[:2], current[:2])
        outgoing = _unit(current[:2], following[:2])

        heading_in = math.atan2(incoming[1], incoming[0])
        heading_out = math.atan2(outgoing[1], outgoing[0])
        turn = _normalise_angle(heading_out - heading_in)

        if abs(turn) < 1e-9:
            raise ValueError("vertex %d is collinear; remove it" % index)

        radius = current[2]
        if radius <= 0.0:
            raise ValueError("vertex %d needs a positive radius" % index)

        tangent = radius * math.tan(abs(turn) / 2.0)

        entry = (current[0] - incoming[0] * tangent,
                 current[1] - incoming[1] * tangent)
        exit_ = (current[0] + outgoing[0] * tangent,
                 current[1] + outgoing[1] * tangent)

        # Arc centre sits perpendicular to the incoming direction, on the
        # inside of the turn.
        sign = 1.0 if turn > 0.0 else -1.0
        normal = (-incoming[1] * sign, incoming[0] * sign)
        centre = (entry[0] + normal[0] * radius, entry[1] + normal[1] * radius)

        corners.append({
            "index": index,
            "vertex": (current[0], current[1]),
            "radius": radius,
            "turn": turn,
            "tangent": tangent,
            "entry": entry,
            "exit": exit_,
            "centre": centre,
            "arc_length": radius * abs(turn),
            "heading_in": heading_in,
            "heading_out": heading_out,
        })

    return corners


def build_segments(vertices=CIRCUIT_VERTICES):
    """Return the alternating straight/arc segment list for one lap."""
    corners = build_corners(vertices)
    count = len(corners)
    segments = []

    for index in range(count):
        corner = corners[index]
        following = corners[(index + 1) % count]

        segments.append({
            "kind": "arc",
            "corner_index": corner["index"],
            "length": corner["arc_length"],
            "radius": corner["radius"],
            "turn": corner["turn"],
            "start": corner["entry"],
            "end": corner["exit"],
            "centre": corner["centre"],
            "heading_in": corner["heading_in"],
        })

        straight_length = _distance(corner["exit"], following["entry"])
        gap = _distance(corner["vertex"], following["vertex"])
        if corner["tangent"] + following["tangent"] > gap + 1e-9:
            raise ValueError(
                "fillet radii at vertices %d and %d overlap: %.3f + %.3f > %.3f"
                % (corner["index"], following["index"], corner["tangent"],
                   following["tangent"], gap))

        segments.append({
            "kind": "straight",
            "corner_index": corner["index"],
            "length": straight_length,
            "start": corner["exit"],
            "end": following["entry"],
        })

    return segments


def sample_centreline(vertices=CIRCUIT_VERTICES,
                      straight_step=STRAIGHT_STEP_M,
                      arc_step=ARC_STEP_RAD):
    """Sample the closed centreline.

    Returns ``(points, stations)`` where ``points`` is a list of (x, y) and
    ``stations`` the cumulative arc length at each point. The closing point is
    NOT repeated; the polyline is implicitly closed.
    """
    segments = build_segments(vertices)
    points = []
    stations = []
    travelled = 0.0

    for segment in segments:
        if segment["kind"] == "straight":
            length = segment["length"]
            steps = max(1, int(math.ceil(length / straight_step)))
            start = segment["start"]
            end = segment["end"]
            for step in range(steps):
                ratio = step / float(steps)
                points.append((start[0] + (end[0] - start[0]) * ratio,
                               start[1] + (end[1] - start[1]) * ratio))
                stations.append(travelled + length * ratio)
            travelled += length
        else:
            radius = segment["radius"]
            turn = segment["turn"]
            centre = segment["centre"]
            start = segment["start"]
            start_angle = math.atan2(start[1] - centre[1],
                                     start[0] - centre[0])
            steps = max(1, int(math.ceil(abs(turn) / arc_step)))
            for step in range(steps):
                ratio = step / float(steps)
                angle = start_angle + turn * ratio
                points.append((centre[0] + math.cos(angle) * radius,
                               centre[1] + math.sin(angle) * radius))
                stations.append(travelled + radius * abs(turn) * ratio)
            travelled += radius * abs(turn)

    return points, stations, travelled


def polyline_length(points):
    """Closed-polyline length, recomputed independently of the sampler."""
    total = 0.0
    for index in range(len(points)):
        total += _distance(points[index], points[(index + 1) % len(points)])
    return total


def total_turning(vertices=CIRCUIT_VERTICES):
    """Sum of signed corner turns. A simple closed loop gives +/- 2 pi."""
    return sum(corner["turn"] for corner in build_corners(vertices))


# ---------------------------------------------------------------------------
# Checkpoints and sectors
# ---------------------------------------------------------------------------

def point_at_station(points, stations, lap_length, target):
    """Interpolate the centreline at an arc-length station."""
    target = target % lap_length
    count = len(points)
    for index in range(count):
        here = stations[index]
        nxt = stations[index + 1] if index + 1 < count else lap_length
        if here <= target <= nxt:
            span = nxt - here
            ratio = 0.0 if span <= 0.0 else (target - here) / span
            a = points[index]
            b = points[(index + 1) % count]
            return (a[0] + (b[0] - a[0]) * ratio,
                    a[1] + (b[1] - a[1]) * ratio)
    return points[0]


def build_checkpoints(layout=CHECKPOINT_LAYOUT, vertices=CIRCUIT_VERTICES):
    """Resolve the checkpoint layout into positioned, ordered checkpoints."""
    points, stations, lap_length = sample_centreline(vertices)

    checkpoints = []
    for index, (name, fraction) in enumerate(layout):
        station = lap_length * fraction
        position = point_at_station(points, stations, lap_length, station)
        ahead = point_at_station(points, stations, lap_length, station + 1.0)
        heading = math.degrees(math.atan2(ahead[1] - position[1],
                                          ahead[0] - position[0]))
        checkpoints.append({
            "checkpoint_id": name,
            "authoring_order_index": index,
            "is_timing_line": index == 0,
            "station_m": round(station, 4),
            "station_fraction": fraction,
            "x_m": round(position[0], 4),
            "y_m": round(position[1], 4),
            "heading_deg": round(heading, 4),
            "gate_width_m": TRACK_WIDTH_M,
        })

    return checkpoints, lap_length


def build_sectors(closing=SECTOR_CLOSING_INDICES,
                  names=SECTOR_DISPLAY_NAMES):
    return [
        {
            "sector_index": index,
            "display_name": names[index] if index < len(names)
                            else "Sector %d" % (index + 1),
            "closing_checkpoint_index": closing_index,
        }
        for index, closing_index in enumerate(closing)
    ]


def build_track_definition(vertices=CIRCUIT_VERTICES,
                           layout=CHECKPOINT_LAYOUT):
    """Emit a dict shaped like UAFTrackDefinition."""
    checkpoints, lap_length = build_checkpoints(layout, vertices)
    return {
        "data_version": 1,
        "track_id": TRACK_ID,
        "display_name": TRACK_DISPLAY_NAME,
        "region_name": TRACK_REGION_NAME,
        "lap_length_m": round(lap_length, 3),
        "grid_slot_count": GRID_SLOT_COUNT,
        "track_width_m": TRACK_WIDTH_M,
        "checkpoint_order": [cp["checkpoint_id"] for cp in checkpoints],
        "checkpoints": checkpoints,
        "sectors": build_sectors(),
        "has_pit_lane": HAS_PIT_LANE,
        "pit_lane_speed_limit_kph": PIT_LANE_SPEED_LIMIT_KPH,
        "originality_note": (
            "Original fictional layout. ApexFormula design values. "
            "Not traced from or named after any real venue."),
    }


# ---------------------------------------------------------------------------
# Python mirror of UAFTrackDefinition::ValidateSelf()
#
# Written by hand. Mirrors AFTrackDefinition.cpp check for check, in the same
# order, with the same thresholds. D-043 records the drift risk this created.
# Since D-045 that risk is controlled mechanically: Tools/af_track_drift_guard.py
# runs in CI and fails the build if the diagnostic messages, the predicates or
# the field names here stop matching the C++. The guard is TEXT-ONLY - it does
# not compile or run the C++, so behavioural equivalence is still unproven.
# ---------------------------------------------------------------------------

def validate_track_definition(track):
    problems = []

    if track["data_version"] < 1:
        problems.append("DataVersion must be >= 1, is %d"
                        % track["data_version"])

    track_id = track["track_id"]
    if not track_id:
        problems.append("TrackId must be set")
    else:
        if track_id != track_id.lower():
            problems.append("TrackId '%s' must be lower case" % track_id)
        if " " in track_id:
            problems.append("TrackId '%s' must not contain spaces" % track_id)

    if not track["display_name"]:
        problems.append("DisplayName must be set")

    if track["lap_length_m"] <= 0.0:
        problems.append("LapLengthM must be > 0, is %f"
                        % track["lap_length_m"])

    if track["grid_slot_count"] < 1:
        problems.append("GridSlotCount must be >= 1, is %d"
                        % track["grid_slot_count"])

    order = track["checkpoint_order"]
    if len(order) < 2:
        problems.append(
            "CheckpointOrder must contain at least 2 entries, has %d"
            % len(order))

    seen = set()
    for index, checkpoint_id in enumerate(order):
        if not checkpoint_id:
            problems.append("CheckpointOrder[%d] is unset" % index)
            continue
        if checkpoint_id in seen:
            problems.append("CheckpointOrder[%d] duplicates checkpoint '%s'"
                            % (index, checkpoint_id))
        seen.add(checkpoint_id)

    sectors = track["sectors"]
    if len(sectors) < 1:
        problems.append("At least one sector must be defined")

    seen_indices = set()
    for index, sector in enumerate(sectors):
        if sector["sector_index"] != index:
            problems.append(
                "Sectors[%d] has SectorIndex %d; sectors must be stored in "
                "ascending order starting at 0"
                % (index, sector["sector_index"]))
        if sector["sector_index"] in seen_indices:
            problems.append("Sector index %d is used more than once"
                            % sector["sector_index"])
        seen_indices.add(sector["sector_index"])

        closing = sector["closing_checkpoint_index"]
        if not (0 <= closing < len(order)):
            problems.append(
                "Sectors[%d].ClosingCheckpointIndex %d is outside "
                "CheckpointOrder (0..%d)"
                % (index, closing, len(order) - 1))

    if sectors and order:
        if sectors[-1]["closing_checkpoint_index"] != 0:
            problems.append(
                "The final sector must close at the timing line (checkpoint "
                "index 0), closes at %d"
                % sectors[-1]["closing_checkpoint_index"])

    if track["has_pit_lane"] and track["pit_lane_speed_limit_kph"] <= 0.0:
        problems.append(
            "PitLaneSpeedLimitKph must be > 0 when bHasPitLane is true, is %f"
            % track["pit_lane_speed_limit_kph"])

    return problems


# ---------------------------------------------------------------------------
# Blender construction (only path that touches a scene)
# ---------------------------------------------------------------------------

def build_in_blender(collection_name="AF_Circuit"):  # pragma: no cover
    """Build the ribbon mesh and checkpoint empties. Requires Blender."""
    if bpy is None:
        raise RuntimeError("build_in_blender requires Blender (bpy)")

    points, _stations, lap_length = sample_centreline()
    track = build_track_definition()

    scene_collection = bpy.context.scene.collection
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        scene_collection.children.link(collection)

    for existing in list(collection.objects):
        bpy.data.objects.remove(existing, do_unlink=True)

    half = TRACK_WIDTH_M / 2.0
    verts = []
    faces = []
    count = len(points)

    for index in range(count):
        here = points[index]
        following = points[(index + 1) % count]
        direction = (following[0] - here[0], following[1] - here[1])
        length = math.hypot(direction[0], direction[1]) or 1.0
        normal = (-direction[1] / length, direction[0] / length)
        verts.append((here[0] + normal[0] * half,
                      here[1] + normal[1] * half, 0.0))
        verts.append((here[0] - normal[0] * half,
                      here[1] - normal[1] * half, 0.0))

    for index in range(count):
        a = index * 2
        b = index * 2 + 1
        c = ((index + 1) % count) * 2 + 1
        d = ((index + 1) % count) * 2
        faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new("AF_CircuitSurface")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    surface = bpy.data.objects.new("AF_CircuitSurface", mesh)
    collection.objects.link(surface)

    for checkpoint in track["checkpoints"]:
        empty = bpy.data.objects.new(checkpoint["checkpoint_id"], None)
        empty.empty_display_type = "CUBE"
        empty.empty_display_size = TRACK_WIDTH_M / 2.0
        empty.location = (checkpoint["x_m"], checkpoint["y_m"], 0.0)
        empty.rotation_euler = (0.0, 0.0,
                                math.radians(checkpoint["heading_deg"]))
        collection.objects.link(empty)

    return {
        "collection": collection_name,
        "surface": surface.name,
        "centreline_points": count,
        "quads": len(faces),
        "checkpoints": len(track["checkpoints"]),
        "lap_length_m": round(lap_length, 3),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

class SelfTest(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.names = set()
        self.failures = []

    def check(self, name, condition, detail=""):
        assert name not in self.names, "duplicate test case name: %s" % name
        self.names.add(name)
        if condition:
            self.passed += 1
            if self.verbose:
                print("  pass  %s" % name)
        else:
            self.failed += 1
            self.failures.append((name, detail))
            print("  FAIL  %s %s" % (name, detail))

    # -- geometry ---------------------------------------------------------

    def test_corner_resolution(self):
        corners = build_corners()
        self.check("corner count matches vertex count",
                   len(corners) == len(CIRCUIT_VERTICES))
        self.check("every corner has a positive radius",
                   all(c["radius"] > 0.0 for c in corners))
        self.check("every corner has a positive arc length",
                   all(c["arc_length"] > 0.0 for c in corners))
        self.check("every corner turn is non-zero",
                   all(abs(c["turn"]) > 1e-9 for c in corners))
        self.check("every corner turn is within +/- pi",
                   all(abs(c["turn"]) <= math.pi + 1e-12 for c in corners))
        self.check("entry point sits on the arc within 1e-9",
                   all(abs(_distance(c["entry"], c["centre"]) - c["radius"])
                       < 1e-9 for c in corners))
        self.check("exit point sits on the arc within 1e-9",
                   all(abs(_distance(c["exit"], c["centre"]) - c["radius"])
                       < 1e-9 for c in corners))

    def test_closure(self):
        turning = total_turning()
        self.check("total turning is one full revolution",
                   abs(abs(turning) - 2.0 * math.pi) < TURN_TOLERANCE_RAD,
                   "turning=%.12f" % turning)

        segments = build_segments()
        self.check("segments alternate arc and straight",
                   all(segments[i]["kind"] == ("arc" if i % 2 == 0
                                               else "straight")
                       for i in range(len(segments))))
        self.check("segment count is twice the vertex count",
                   len(segments) == 2 * len(CIRCUIT_VERTICES))

        for segment in segments:
            if segment["kind"] == "straight" and segment["length"] <= 0.0:
                self.check("straight after corner %d has positive length"
                           % segment["corner_index"], False,
                           "length=%.3f" % segment["length"])
                break
        else:
            self.check("every straight has positive length", True)

        # Each segment must start where the previous one ended.
        worst = 0.0
        for index in range(len(segments)):
            end = segments[index]["end"]
            start = segments[(index + 1) % len(segments)]["start"]
            worst = max(worst, _distance(end, start))
        self.check("segment chain is continuous and closed",
                   worst < CLOSURE_TOLERANCE_M, "worst gap=%.3e" % worst)

    def test_lap_length(self):
        segments = build_segments()
        summed = sum(segment["length"] for segment in segments)
        points, stations, travelled = sample_centreline()

        self.check("sampler length matches summed segment length",
                   abs(summed - travelled) < 1e-9,
                   "summed=%.6f travelled=%.6f" % (summed, travelled))

        sampled = polyline_length(points)
        self.check("independent polyline length agrees within tolerance",
                   abs(sampled - travelled) < LENGTH_TOLERANCE_M,
                   "polyline=%.3f travelled=%.3f" % (sampled, travelled))

        self.check("lap length is a plausible circuit length",
                   3000.0 < travelled < 7000.0, "lap=%.1f m" % travelled)

        self.check("stations start at zero", abs(stations[0]) < 1e-12)
        self.check("stations are strictly increasing",
                   all(stations[i] < stations[i + 1]
                       for i in range(len(stations) - 1)))
        self.check("final station is below lap length",
                   stations[-1] < travelled)
        self.check("sample count is sane",
                   200 < len(points) < 20000, "points=%d" % len(points))

        arc_total = sum(s["length"] for s in segments if s["kind"] == "arc")
        straight_total = sum(s["length"] for s in segments
                             if s["kind"] == "straight")
        self.check("arc plus straight equals lap length",
                   abs(arc_total + straight_total - travelled) < 1e-9)
        self.check("circuit has meaningful straights",
                   straight_total > 0.2 * travelled,
                   "straights=%.1f of %.1f" % (straight_total, travelled))
        self.check("circuit has meaningful corners",
                   arc_total > 0.2 * travelled,
                   "arcs=%.1f of %.1f" % (arc_total, travelled))

    def test_overlapping_fillets_rejected(self):
        bad = ((0.0, 0.0, 500.0), (100.0, 0.0, 500.0), (50.0, 90.0, 500.0))
        try:
            build_segments(bad)
        except ValueError:
            self.check("overlapping fillet radii are rejected", True)
        else:
            self.check("overlapping fillet radii are rejected", False)

    def test_degenerate_inputs_rejected(self):
        try:
            build_corners(((0.0, 0.0, 10.0), (10.0, 0.0, 10.0)))
        except ValueError:
            self.check("fewer than 3 vertices rejected", True)
        else:
            self.check("fewer than 3 vertices rejected", False)

        collinear = ((0.0, 0.0, 10.0), (50.0, 0.0, 10.0),
                     (100.0, 0.0, 10.0), (50.0, 80.0, 10.0))
        try:
            build_corners(collinear)
        except ValueError:
            self.check("collinear vertex rejected", True)
        else:
            self.check("collinear vertex rejected", False)

        zero_radius = ((0.0, 0.0, 0.0), (200.0, 0.0, 10.0), (100.0, 150.0, 10.0))
        try:
            build_corners(zero_radius)
        except ValueError:
            self.check("zero radius rejected", True)
        else:
            self.check("zero radius rejected", False)

        coincident = ((0.0, 0.0, 10.0), (0.0, 0.0, 10.0), (100.0, 100.0, 10.0))
        try:
            build_corners(coincident)
        except ValueError:
            self.check("coincident vertices rejected", True)
        else:
            self.check("coincident vertices rejected", False)

    # -- checkpoints ------------------------------------------------------

    def test_checkpoints(self):
        checkpoints, lap_length = build_checkpoints()

        self.check("checkpoint count matches layout",
                   len(checkpoints) == len(CHECKPOINT_LAYOUT))
        self.check("index 0 is the timing line",
                   checkpoints[0]["is_timing_line"] is True)
        self.check("only one timing line",
                   sum(1 for c in checkpoints if c["is_timing_line"]) == 1)
        self.check("timing line sits at station zero",
                   abs(checkpoints[0]["station_m"]) < 1e-9)
        self.check("authoring indices are 0..n-1",
                   [c["authoring_order_index"] for c in checkpoints]
                   == list(range(len(checkpoints))))
        self.check("stations strictly increase around the lap",
                   all(checkpoints[i]["station_m"]
                       < checkpoints[i + 1]["station_m"]
                       for i in range(len(checkpoints) - 1)))
        self.check("every station is below lap length",
                   all(c["station_m"] < lap_length for c in checkpoints))
        self.check("checkpoint ids are unique",
                   len({c["checkpoint_id"] for c in checkpoints})
                   == len(checkpoints))
        self.check("at least two checkpoints, so a full cut cannot score",
                   len(checkpoints) >= 2)

        # Checkpoints must actually lie on the centreline.
        points, stations, lap = sample_centreline()
        worst = 0.0
        for checkpoint in checkpoints:
            position = (checkpoint["x_m"], checkpoint["y_m"])
            nearest = min(_distance(position, p) for p in points)
            worst = max(worst, nearest)
        self.check("every checkpoint lies on the centreline",
                   worst < STRAIGHT_STEP_M, "worst offset=%.3f m" % worst)

        self.check("gate width matches track width",
                   all(abs(c["gate_width_m"] - TRACK_WIDTH_M) < 1e-12
                       for c in checkpoints))

    def test_sectors(self):
        track = build_track_definition()
        sectors = track["sectors"]
        order = track["checkpoint_order"]

        self.check("sector indices ascend from zero",
                   [s["sector_index"] for s in sectors]
                   == list(range(len(sectors))))
        self.check("final sector closes at the timing line",
                   sectors[-1]["closing_checkpoint_index"] == 0)
        self.check("every closing index is inside CheckpointOrder",
                   all(0 <= s["closing_checkpoint_index"] < len(order)
                       for s in sectors))
        self.check("closing indices are unique",
                   len({s["closing_checkpoint_index"] for s in sectors})
                   == len(sectors))
        self.check("sector count matches the rules model's three-sector lap",
                   len(sectors) == 3)
        self.check("every sector has a display name",
                   all(s["display_name"] for s in sectors))

        # Non-final sectors must close in ascending station order.
        non_final = [s["closing_checkpoint_index"] for s in sectors[:-1]]
        self.check("non-final sectors close in ascending order",
                   non_final == sorted(non_final))

    # -- track definition -------------------------------------------------

    def test_track_definition(self):
        track = build_track_definition()
        problems = validate_track_definition(track)
        self.check("generated track definition validates clean",
                   problems == [], "; ".join(problems))

        self.check("track id is lower case", track["track_id"]
                   == track["track_id"].lower())
        self.check("track id has no spaces", " " not in track["track_id"])
        self.check("display name is set", bool(track["display_name"]))
        self.check("region name is set", bool(track["region_name"]))
        self.check("data version is at least 1", track["data_version"] >= 1)
        self.check("lap length is positive", track["lap_length_m"] > 0.0)
        self.check("grid slot count is at least 1",
                   track["grid_slot_count"] >= 1)
        self.check("pit lane speed limit is positive when pit lane exists",
                   (not track["has_pit_lane"])
                   or track["pit_lane_speed_limit_kph"] > 0.0)
        self.check("checkpoint_order matches the checkpoint table",
                   track["checkpoint_order"]
                   == [c["checkpoint_id"] for c in track["checkpoints"]])
        self.check("track is JSON serialisable",
                   isinstance(json.dumps(track, sort_keys=True), str))

    def test_validator_catches_bad_definitions(self):
        base = build_track_definition()

        def mutated(**changes):
            copy = dict(base)
            copy.update(changes)
            return validate_track_definition(copy)

        self.check("validator rejects data version 0",
                   any("DataVersion" in p for p in mutated(data_version=0)))
        self.check("validator rejects empty track id",
                   any("TrackId must be set" in p for p in mutated(track_id="")))
        self.check("validator rejects upper case track id",
                   any("lower case" in p for p in mutated(track_id="AF_Test")))
        self.check("validator rejects spaces in track id",
                   any("must not contain spaces" in p
                       for p in mutated(track_id="af test")))
        self.check("validator rejects empty display name",
                   any("DisplayName" in p for p in mutated(display_name="")))
        self.check("validator rejects zero lap length",
                   any("LapLengthM" in p for p in mutated(lap_length_m=0.0)))
        self.check("validator rejects zero grid slots",
                   any("GridSlotCount" in p for p in mutated(grid_slot_count=0)))
        self.check("validator rejects a single checkpoint",
                   any("at least 2 entries" in p
                       for p in mutated(checkpoint_order=["AF_CP_Line"])))
        self.check("validator rejects duplicate checkpoints",
                   any("duplicates checkpoint" in p
                       for p in mutated(checkpoint_order=[
                           "AF_CP_Line", "AF_CP_Alpha", "AF_CP_Line"])))
        self.check("validator rejects an unset checkpoint",
                   any("is unset" in p
                       for p in mutated(checkpoint_order=[
                           "AF_CP_Line", ""])))
        self.check("validator rejects zero sectors",
                   any("At least one sector" in p for p in mutated(sectors=[])))
        self.check("validator rejects out-of-order sector indices",
                   any("ascending order" in p for p in mutated(sectors=[
                       {"sector_index": 1, "display_name": "a",
                        "closing_checkpoint_index": 0}])))
        self.check("validator rejects an out-of-range closing index",
                   any("outside CheckpointOrder" in p for p in mutated(sectors=[
                       {"sector_index": 0, "display_name": "a",
                        "closing_checkpoint_index": 99}])))
        self.check("validator rejects a final sector not closing at the line",
                   any("final sector must close" in p for p in mutated(sectors=[
                       {"sector_index": 0, "display_name": "a",
                        "closing_checkpoint_index": 2}])))
        self.check("validator rejects zero pit speed limit with a pit lane",
                   any("PitLaneSpeedLimitKph" in p
                       for p in mutated(pit_lane_speed_limit_kph=0.0)))
        self.check("validator accepts no pit lane with zero speed limit",
                   not any("PitLaneSpeedLimitKph" in p
                           for p in mutated(has_pit_lane=False,
                                            pit_lane_speed_limit_kph=0.0)))

    # -- determinism ------------------------------------------------------

    def test_determinism(self):
        first = json.dumps(build_track_definition(), sort_keys=True)
        second = json.dumps(build_track_definition(), sort_keys=True)
        third = json.dumps(build_track_definition(), sort_keys=True)
        self.check("track definition is deterministic across three runs",
                   first == second == third)

        points_a, stations_a, lap_a = sample_centreline()
        points_b, stations_b, lap_b = sample_centreline()
        self.check("centreline sampling is deterministic",
                   points_a == points_b and stations_a == stations_b
                   and lap_a == lap_b)

        self.check("build_segments is deterministic",
                   json.dumps(build_segments(), sort_keys=True)
                   == json.dumps(build_segments(), sort_keys=True))

    def test_agreement_with_lap_rules(self):
        """The circuit must be consumable by the lap rules model's contract."""
        track = build_track_definition()
        order = track["checkpoint_order"]

        # Mirror of UAFLapValidator::Configure acceptance.
        self.check("circuit satisfies validator Configure: >= 2 entries",
                   len(order) >= 2)
        self.check("circuit satisfies validator Configure: no unset ids",
                   all(bool(cp) and cp != "None" for cp in order))
        self.check("circuit satisfies validator Configure: no duplicates",
                   len(set(order)) == len(order))

        # Walking the order in sequence must complete a lap.
        next_expected = 1
        for checkpoint_id in order[1:]:
            if order[next_expected] == checkpoint_id:
                next_expected += 1
        self.check("walking the order in sequence completes the lap",
                   next_expected >= len(order))

        self.check("sector count does not exceed checkpoint count",
                   len(track["sectors"]) <= len(order))

    # -- originality ------------------------------------------------------

    def test_originality_guard(self):
        track = build_track_definition()
        blob = json.dumps(track, sort_keys=True).lower()

        offenders = [token for token in PROHIBITED_SUBSTRINGS
                     if token in blob]
        self.check("no prohibited motorsport token in generated output",
                   offenders == [], "found=%r" % offenders)

        self.check("every checkpoint uses the neutral AF_CP_ prefix",
                   all(cp.startswith("AF_CP_")
                       for cp in track["checkpoint_order"]))
        self.check("track id uses the neutral af_ prefix",
                   track["track_id"].startswith("af_"))
        self.check("originality note is present",
                   "Original fictional layout" in track["originality_note"])

    # -- runner -----------------------------------------------------------

    def run(self):
        for name in sorted(dir(self)):
            if name.startswith("test_"):
                getattr(self, name)()
        return self.failed == 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def print_summary(track):
    points, _stations, lap_length = sample_centreline()
    segments = build_segments()
    arcs = [s for s in segments if s["kind"] == "arc"]
    straights = [s for s in segments if s["kind"] == "straight"]

    print("")
    print("af_circuit_generate summary")
    print("  track id        : %s" % track["track_id"])
    print("  display name    : %s" % track["display_name"])
    print("  region          : %s" % track["region_name"])
    print("  lap length      : %.1f m" % lap_length)
    print("  track width     : %.1f m" % TRACK_WIDTH_M)
    print("  corners         : %d" % len(arcs))
    print("  straights       : %d (%.1f m total)"
          % (len(straights), sum(s["length"] for s in straights)))
    print("  corner distance : %.1f m total"
          % sum(s["length"] for s in arcs))
    print("  centreline pts  : %d" % len(points))
    print("  grid slots      : %d" % track["grid_slot_count"])
    print("  pit lane        : %s (%.0f kph limit)"
          % (track["has_pit_lane"], track["pit_lane_speed_limit_kph"]))
    print("")
    print("  checkpoints (index 0 is the timing line):")
    for checkpoint in track["checkpoints"]:
        print("    %-16s idx=%d  station=%8.1f m  pos=(%9.1f, %9.1f)  %s"
              % (checkpoint["checkpoint_id"],
                 checkpoint["authoring_order_index"],
                 checkpoint["station_m"],
                 checkpoint["x_m"], checkpoint["y_m"],
                 "TIMING LINE" if checkpoint["is_timing_line"] else ""))
    print("")
    print("  sectors:")
    for sector in track["sectors"]:
        closing = track["checkpoint_order"][
            sector["closing_checkpoint_index"]]
        print("    %-10s index=%d  closes at %s (checkpoint index %d)"
              % (sector["display_name"], sector["sector_index"],
                 closing, sector["closing_checkpoint_index"]))
    print("")
    print("  Originality: original fictional layout, ApexFormula design")
    print("  values. Not traced from or named after any real venue.")


def main(argv):
    args = list(argv[1:])

    # Blender passes its own arguments; ignore everything after "--".
    if "--" in args:
        args = args[args.index("--") + 1:]

    verbose = "--verbose" in args
    for flag in ("--verbose",):
        while flag in args:
            args.remove(flag)

    unknown = [a for a in args
               if a not in ("--self-test", "--dump", "--build")]
    if unknown and bpy is None:
        print("unknown argument(s): %s" % " ".join(unknown))
        print(__doc__)
        return EXIT_USAGE

    if "--dump" in args:
        print(json.dumps(build_track_definition(), indent=2, sort_keys=True))
        return EXIT_OK

    if "--self-test" in args:
        print("ApexFormula circuit generator self-test")
        print(RULE)
        suite = SelfTest(verbose=verbose)
        ok = suite.run()
        print(RULE)
        print("cases passed : %d" % suite.passed)
        print("cases failed : %d" % suite.failed)
        if not ok:
            print("")
            print("failing cases:")
            for name, detail in suite.failures:
                print("  - %s %s" % (name, detail))
            print("SELF-TEST FAIL")
            return EXIT_FAILED
        print("SELF-TEST PASS")
        print("")
        print("Proven by execution: layout closure, lap length, checkpoint")
        print("ordering, sector rules, the ValidateSelf mirror, determinism")
        print("and the originality guard. NOT proven: mesh appearance,")
        print("drivability, or Unreal import. Those require Blender execution")
        print("and Unreal Editor verification.")
        return EXIT_OK

    track = build_track_definition()
    print_summary(track)

    if bpy is not None:
        info = build_in_blender()
        print("")
        print("  built in Blender:")
        for key in sorted(info):
            print("    %-20s %s" % (key, info[key]))
    else:
        print("")
        print("  bpy unavailable: layout computed, no mesh built.")
        print("  Run inside Blender to build geometry:")
        print("    blender --background --python af_circuit_generate.py")

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv))
