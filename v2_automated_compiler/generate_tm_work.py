import json
import zipfile
import os
import math

def build_model_xml(model):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<model class="org.workcraft.plugins.cpog.Cpog" ref="">')
    lines.append('  <AbstractModel>')
    lines.append(f'    <property class="java.lang.String" name="title" value="Automated TM CPOG ({model["benchmark_name"]})"/>')
    lines.append('  </AbstractModel>')
    lines.append('  <root class="org.workcraft.dom.math.MathGroup" ref=".">')
    
    # Variables
    for var in model["scenario_variables"]:
        lines.append(f'    <node class="org.workcraft.plugins.cpog.Variable" ref="{var}">')
        lines.append('      <Variable>')
        lines.append(f'        <property class="java.lang.String" name="label" value="{var}"/>')
        lines.append('        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>')
        lines.append('      </Variable>')
        lines.append('    </node>')

    # Vertices
    for v in model["vertices"]:
        lines.append(f'    <node class="org.workcraft.plugins.cpog.Vertex" ref="{v["id"]}">')
        lines.append(f'      <Vertex formula="{v["phi"]}"/>')
        lines.append('    </node>')

    # Arcs
    for i, e in enumerate(model["edges"]):
        # Workcraft formulas: use !, *, + instead of ~, &, |
        formula = e["rho_str"].replace("~", "!").replace(" * ", "*")
        lines.append(f'    <node class="org.workcraft.plugins.cpog.Arc" ref="arc_{i}">')
        lines.append(f'      <Arc formula="{formula}"/>')
        lines.append(f'      <MathConnection first="{e["from"]}" second="{e["to"]}"/>')
        lines.append('    </node>')

    lines.append('  </root>')
    lines.append('</model>')
    return "\n".join(lines)


def build_visual_xml(model):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<model class="org.workcraft.plugins.cpog.VisualCpog" ref="">')
    lines.append('  <AbstractModel>')
    lines.append(f'    <property class="java.lang.String" name="title" value="Automated TM CPOG ({model["benchmark_name"]})"/>')
    lines.append('  </AbstractModel>')
    lines.append('  <root class="org.workcraft.dom.visual.VisualGroup" ref="0">')
    lines.append('    <VisualGroup>')
    lines.append('      <property class="boolean" name="isCollapsed" value="false"/>')
    lines.append('    </VisualGroup>')
    lines.append('    <VisualTransformableNode>')
    lines.append('      <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0x0.0p0 0x0.0p0" name="transform"/>')
    lines.append('    </VisualTransformableNode>')

    ref_id = 1
    
    # Visual Variables (Placed neatly top-left)
    for i, var in enumerate(model["scenario_variables"]):
        lines.append(f'    <node class="org.workcraft.plugins.cpog.VisualVariable" ref="{ref_id}">')
        lines.append(f'      <VisualVariable ref="{var}">')
        lines.append('        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>')
        lines.append('      </VisualVariable>')
        lines.append('      <VisualComponent>')
        lines.append('        <property class="java.awt.Color" name="fillColor" rgb="#f1f5f9"/>')
        lines.append('        <property class="java.awt.Color" name="foregroundColor" rgb="#0f172a"/>')
        lines.append(f'        <property class="java.lang.String" name="label" value="{var}"/>')
        lines.append('        <property class="java.awt.Color" name="labelColor" rgb="#0f172a"/>')
        lines.append('        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>')
        lines.append('      </VisualComponent>')
        lines.append('      <VisualTransformableNode>')
        x_pos = -14.0 + i * 3.0
        lines.append(f'        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 {x_pos} -10.0" name="transform"/>')
        lines.append('      </VisualTransformableNode>')
        lines.append('    </node>')
        ref_id += 1

    # --- Hierarchical Schematic Layout Calculation ---
    inputs = [v for v in model["vertices"] if v["type"] == "input"]
    and_gates = [v for v in model["vertices"] if v["type"] == "and_gate"]
    accumulators = [v for v in model["vertices"] if v["type"] == "accumulator"]
    comparators = [v for v in model["vertices"] if v["type"] == "comparator"]
    num_cores = len(and_gates)

    node_coords = {}
    node_colors = {}
    node_labels = {}
    label_positions = {}

    # Core-aligned hardware placement
    core_spacing = 8.5 if num_cores > 1 else 0.0
    for core in range(num_cores):
        cx = (core - (num_cores - 1) / 2.0) * core_spacing
        mux_offset = 2.6 if num_cores == 1 else 2.0
        
        # Symmetrical MUX funnel directly over AND_core
        node_coords[f"mux1_core{core}"] = (cx - mux_offset, -2.0)
        node_coords[f"mux2_core{core}"] = (cx + mux_offset, -2.0)
        node_coords[f"and_core{core}"]  = (cx, 3.5)
        node_coords[f"acc_core{core}"]  = (cx, 8.5)
        
        # Smart non-colliding label orientations
        label_positions[f"mux1_core{core}"] = "LEFT"
        label_positions[f"mux2_core{core}"] = "RIGHT"
        label_positions[f"and_core{core}"]  = "RIGHT"
        label_positions[f"acc_core{core}"]  = "RIGHT"

    # Inputs layout at Y = -7.0
    n_in = len(inputs)
    in_dx = 3.6 if n_in <= 4 else 2.8
    in_start_x = -((n_in - 1) / 2.0) * in_dx
    for idx, node in enumerate(inputs):
        node_coords[node["id"]] = (in_start_x + idx * in_dx, -7.0)
        label_positions[node["id"]] = "TOP"

    # Comparator at bottom center Y = 13.5
    for comp in comparators:
        node_coords[comp["id"]] = (0.0, 13.5)
        label_positions[comp["id"]] = "BOTTOM"

    # Clean display labels and styling
    for v in model["vertices"]:
        vid = v["id"]
        vtype = v["type"]
        if vtype == "input":
            node_colors[vid] = "#ffffff"
            # Format: in_not_x1 -> ~x1, in_not_sl_low -> ~sl_lo
            clean = vid.replace("in_not_", "~").replace("in_", "")
            clean = clean.replace("_low", "_lo").replace("_high", "_hi")
            node_labels[vid] = clean
        elif vtype == "mux":
            node_colors[vid] = "#fef08a" # Warm amber
            node_labels[vid] = vid.replace("mux1_core", "M1_").replace("mux2_core", "M2_")
        elif vtype == "and_gate":
            node_colors[vid] = "#bbf7d0" # Soft green
            node_labels[vid] = vid.replace("and_core", "AND_")
        elif vtype == "accumulator":
            node_colors[vid] = "#f3e8ff" # Soft purple
            node_labels[vid] = vid.replace("acc_core", "ACC_")
        elif vtype == "comparator":
            node_colors[vid] = "#fed7aa" # Soft orange
            node_labels[vid] = "CMP"
        else:
            node_colors[vid] = "#ffffff"
            node_labels[vid] = vid

    # Visual Vertices Serialization
    vertex_ref_map = {}
    for i, v in enumerate(model["vertices"]):
        vid = v["id"]
        vertex_ref_map[vid] = ref_id
        x_pos, y_pos = node_coords.get(vid, (0.0, 0.0))
        lbl_pos = label_positions.get(vid, "TOP")
        lines.append(f'    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="{ref_id}">')
        lines.append(f'      <VisualVertex ref="{vid}">')
        lines.append('        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>')
        lines.append('      </VisualVertex>')
        lines.append('      <VisualComponent>')
        lines.append(f'        <property class="java.awt.Color" name="fillColor" rgb="{node_colors[vid]}"/>')
        lines.append('        <property class="java.awt.Color" name="foregroundColor" rgb="#0f172a"/>')
        lines.append(f'        <property class="java.lang.String" name="label" value="{node_labels[vid]}"/>')
        lines.append('        <property class="java.awt.Color" name="labelColor" rgb="#0f172a"/>')
        lines.append(f'        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="{lbl_pos}"/>')
        lines.append('      </VisualComponent>')
        lines.append('      <VisualTransformableNode>')
        lines.append(f'        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 {x_pos:.2f} {y_pos:.2f}" name="transform"/>')
        lines.append('      </VisualTransformableNode>')
        lines.append('    </node>')
        ref_id += 1
        
    # Visual Arcs
    poly_id = 500
    for i, e in enumerate(model["edges"]):
        first_ref = vertex_ref_map.get(e["from"], 0)
        second_ref = vertex_ref_map.get(e["to"], 0)
        arc_ref = f"arc_{i}"
        lines.append(f'    <node class="org.workcraft.plugins.cpog.VisualArc" ref="{ref_id}">')
        lines.append(f'      <VisualArc ref="{arc_ref}"/>')
        lines.append(f'      <VisualConnection first="{first_ref}" ref="{arc_ref}" second="{second_ref}">')
        lines.append('        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>')
        lines.append('        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>')
        lines.append('        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>')
        lines.append('        <property class="java.awt.Color" name="color" rgb="#0"/>')
        lines.append('        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>')
        lines.append('        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>')
        lines.append('        <property class="boolean" name="tokenColorPropagator" value="false"/>')
        lines.append(f'        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="{poly_id}"/>')
        lines.append('      </VisualConnection>')
        lines.append('    </node>')
        ref_id += 1
        poly_id += 1
        
    lines.append('  </root>')
    lines.append('</model>')
    return "\n".join(lines)


def create_work_files(output_dir="./generated", model_file="cpog_model.json", out_name="workcraft_automated.work"):
    model_path = os.path.join(output_dir, model_file)
    with open(model_path, "r", encoding="utf-8") as f:
        model = json.load(f)

    model_xml_str = build_model_xml(model)
    visual_xml_str = build_visual_xml(model)

    state_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<workcraft-state>
  <level ref="0"/>
  <selection/>
</workcraft-state>
"""

    meta = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<workcraft-meta>
  <version major="3" minor="2" revision="1" status=""/>
  <descriptor class="org.workcraft.plugins.cpog.CpogDescriptor"/>
  <math entry-name="model.xml" format-uuid="6ea20f69-c9c4-4888-9124-252fe4345309"/>
  <visual entry-name="visualModel.xml" format-uuid="6ea20f69-c9c4-4888-9124-252fe4345309"/>
</workcraft-meta>
"""

    out_path = os.path.join(output_dir, out_name)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("model.xml", model_xml_str)
        zf.writestr("visualModel.xml", visual_xml_str)
        zf.writestr("state.xml", state_xml)
        zf.writestr("meta", meta)

    print(f"[generate_tm_work] Generated native Workcraft binary model: {out_path}")
    return [out_path]

if __name__ == "__main__":
    create_work_files()
