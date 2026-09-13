"""
build_tm_workcraft_work.py
===========================
Packages the synthesized Tsetlin Machine CPOG into a native Workcraft '.work' file.
Creates:
- generated/tsetlin_machine_cpog.work
- generated/workcraft_cpog.work
"""

import os
import zipfile

def build_tm_workcraft_file(output_dir="./generated"):
    os.makedirs(output_dir, exist_ok=True)
    work_path = os.path.join(output_dir, "tsetlin_machine_cpog.work")
    alias_path = os.path.join(output_dir, "workcraft_cpog.work")

    # 1. model.xml
    model_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<model class="org.workcraft.plugins.cpog.Cpog" ref="">
  <AbstractModel>
    <property class="java.lang.String" name="title" value="Tsetlin Machine CPOG (XOR)"/>
  </AbstractModel>
  <root class="org.workcraft.dom.math.MathGroup" ref=".">
    <node class="org.workcraft.plugins.cpog.Variable" ref="s1">
      <Variable>
        <property class="java.lang.String" name="label" value="s1"/>
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </Variable>
    </node>
    <node class="org.workcraft.plugins.cpog.Variable" ref="s0">
      <Variable>
        <property class="java.lang.String" name="label" value="s0"/>
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </Variable>
    </node>
    
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_in_x1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_in_not_x1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_in_x2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_in_not_x2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_lit_mux1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_lit_mux2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_and_core">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_acc_core">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_decision_cmp">
      <Vertex formula="1"/>
    </node>

    <node class="org.workcraft.plugins.cpog.Arc" ref="arc1">
      <Arc formula="!s0"/>
      <MathConnection first="v_in_x1" second="v_lit_mux1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc2">
      <Arc formula="s0"/>
      <MathConnection first="v_in_not_x1" second="v_lit_mux1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc3">
      <Arc formula="s1 ^ s0"/>
      <MathConnection first="v_in_x2" second="v_lit_mux2"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc4">
      <Arc formula="!(s1 ^ s0)"/>
      <MathConnection first="v_in_not_x2" second="v_lit_mux2"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc5">
      <Arc formula="1"/>
      <MathConnection first="v_lit_mux1" second="v_and_core"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc6">
      <Arc formula="1"/>
      <MathConnection first="v_lit_mux2" second="v_and_core"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc7">
      <Arc formula="1"/>
      <MathConnection first="v_and_core" second="v_acc_core"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="arc8">
      <Arc formula="1"/>
      <MathConnection first="v_acc_core" second="v_decision_cmp"/>
    </node>
  </root>
</model>
"""

    # 2. visualModel.xml
    visual_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<model class="org.workcraft.plugins.cpog.VisualCpog" ref="">
  <AbstractModel>
    <property class="java.lang.String" name="title" value="Tsetlin Machine CPOG (XOR)"/>
  </AbstractModel>
  <root class="org.workcraft.dom.visual.VisualGroup" ref="0">
    <VisualGroup>
      <property class="boolean" name="isCollapsed" value="false"/>
    </VisualGroup>
    <VisualTransformableNode>
      <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0x0.0p0 0x0.0p0" name="transform"/>
    </VisualTransformableNode>

    <!-- Variables -->
    <node class="org.workcraft.plugins.cpog.VisualVariable" ref="1">
      <VisualVariable ref="s1">
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </VisualVariable>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="s1"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -12.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVariable" ref="2">
      <VisualVariable ref="s0">
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </VisualVariable>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="s0"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -10.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- Vertices -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="3">
      <VisualVertex ref="v_in_x1"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="x1"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -6.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="4">
      <VisualVertex ref="v_in_not_x1"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="~x1"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -2.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="5">
      <VisualVertex ref="v_in_x2"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="x2"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 2.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="6">
      <VisualVertex ref="v_in_not_x2"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="~x2"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 6.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="7">
      <VisualVertex ref="v_lit_mux1"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="MUX1"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -4.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="8">
      <VisualVertex ref="v_lit_mux2"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="MUX2"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 4.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="9">
      <VisualVertex ref="v_and_core"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="AND_CORE"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 1.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="10">
      <VisualVertex ref="v_acc_core"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="ACCUMULATOR"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 4.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="11">
      <VisualVertex ref="v_decision_cmp"/>
      <VisualComponent>
        <property class="java.lang.String" name="label" value="COMPARATOR"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 7.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- Visual Connections -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="12">
      <VisualArc ref="arc1"/>
      <VisualConnection first="3" second="7"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="13">
      <VisualArc ref="arc2"/>
      <VisualConnection first="4" second="7"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="14">
      <VisualArc ref="arc3"/>
      <VisualConnection first="5" second="8"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="15">
      <VisualArc ref="arc4"/>
      <VisualConnection first="6" second="8"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="16">
      <VisualArc ref="arc5"/>
      <VisualConnection first="7" second="9"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="17">
      <VisualArc ref="arc6"/>
      <VisualConnection first="8" second="9"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="18">
      <VisualArc ref="arc7"/>
      <VisualConnection first="9" second="10"/>
    </node>
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="19">
      <VisualArc ref="arc8"/>
      <VisualConnection first="10" second="11"/>
    </node>
  </root>
</model>
"""

    # 3. state.xml
    state_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<workcraft-state>
  <level ref="0"/>
  <selection/>
</workcraft-state>
"""

    # 4. meta
    meta = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<workcraft-meta>
  <version major="3" minor="5" revision="5" status=""/>
  <descriptor class="org.workcraft.plugins.cpog.CpogDescriptor"/>
  <math entry-name="model.xml" format-uuid="6ea20f69-c9c4-4888-9124-252fe4345309"/>
  <visual entry-name="visualModel.xml" format-uuid="6ea20f69-c9c4-4888-9124-252fe4345309"/>
</workcraft-meta>
"""

    for p in [work_path, alias_path]:
        with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("model.xml", model_xml)
            z.writestr("visualModel.xml", visual_xml)
            z.writestr("state.xml", state_xml)
            z.writestr("meta", meta)
        print(f"Generated native Workcraft file: {p}")

if __name__ == "__main__":
    build_tm_workcraft_file()
