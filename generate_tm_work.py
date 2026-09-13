"""
generate_tm_work.py
Generates an authentic, fully compliant Workcraft .work file for the Tsetlin Machine CPOG.
"""
import zipfile
import subprocess

model_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<model class="org.workcraft.plugins.cpog.Cpog" ref="">
  <AbstractModel>
    <property class="java.lang.String" name="title" value="Tsetlin Machine CPOG (XOR)"/>
  </AbstractModel>
  <root class="org.workcraft.dom.math.MathGroup" ref=".">
    <node class="org.workcraft.plugins.cpog.Variable" ref="s0">
      <Variable>
        <property class="java.lang.String" name="label" value="s0"/>
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </Variable>
    </node>
    <node class="org.workcraft.plugins.cpog.Variable" ref="s1">
      <Variable>
        <property class="java.lang.String" name="label" value="s1"/>
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </Variable>
    </node>

    <!-- 9 Functional Vertices -->
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_x1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_not_x1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_x2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_not_x2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_mux1">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_mux2">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_and">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_acc">
      <Vertex formula="1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Vertex" ref="v_cmp">
      <Vertex formula="1"/>
    </node>

    <!-- 8 Conditional / Direct Arcs -->
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_x1_mux1">
      <Arc formula="!s0"/>
      <MathConnection first="v_x1" second="v_mux1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_nx1_mux1">
      <Arc formula="s0"/>
      <MathConnection first="v_not_x1" second="v_mux1"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_x2_mux2">
      <Arc formula="s1 ^ s0"/>
      <MathConnection first="v_x2" second="v_mux2"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_nx2_mux2">
      <Arc formula="!(s1 ^ s0)"/>
      <MathConnection first="v_not_x2" second="v_mux2"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_mux1_and">
      <Arc formula="1"/>
      <MathConnection first="v_mux1" second="v_and"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_mux2_and">
      <Arc formula="1"/>
      <MathConnection first="v_mux2" second="v_and"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_and_acc">
      <Arc formula="1"/>
      <MathConnection first="v_and" second="v_acc"/>
    </node>
    <node class="org.workcraft.plugins.cpog.Arc" ref="a_acc_cmp">
      <Arc formula="1"/>
      <MathConnection first="v_acc" second="v_cmp"/>
    </node>
  </root>
</model>
"""

# Vertex visual positions (x, y)
# ref 1..2: variables
# ref 10..18: visual vertices
# ref 20..27: visual arcs
# ref 30..37: polylines

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

    <!-- Variable s0 -->
    <node class="org.workcraft.plugins.cpog.VisualVariable" ref="1">
      <VisualVariable ref="s0">
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </VisualVariable>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="s0"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -12.0 0.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- Variable s1 -->
    <node class="org.workcraft.plugins.cpog.VisualVariable" ref="2">
      <VisualVariable ref="s1">
        <property class="org.workcraft.plugins.cpog.VariableState" enum-class="org.workcraft.plugins.cpog.VariableState" name="state" value="FALSE"/>
      </VisualVariable>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="s1"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -10.0 0.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- Vertices -->
    <!-- v_x1 (ref 10) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="10">
      <VisualVertex ref="v_x1">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="x1"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -6.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_not_x1 (ref 11) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="11">
      <VisualVertex ref="v_not_x1">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="~x1"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -2.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_x2 (ref 12) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="12">
      <VisualVertex ref="v_x2">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="x2"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 2.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_not_x2 (ref 13) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="13">
      <VisualVertex ref="v_not_x2">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ffffff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="~x2"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 6.0 -6.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_mux1 (ref 14) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="14">
      <VisualVertex ref="v_mux1">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#fef08a"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="MUX1"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 -4.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_mux2 (ref 15) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="15">
      <VisualVertex ref="v_mux2">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#fef08a"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="MUX2"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 4.0 -2.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_and (ref 16) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="16">
      <VisualVertex ref="v_and">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#dcfce7"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="AND_CORE"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 1.5" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_acc (ref 17) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="17">
      <VisualVertex ref="v_acc">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#f3e8ff"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="ACCUMULATOR"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 5.0" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- v_cmp (ref 18) -->
    <node class="org.workcraft.plugins.cpog.VisualVertex" ref="18">
      <VisualVertex ref="v_cmp">
        <property class="org.workcraft.plugins.cpog.VisualVertex$RenderType" enum-class="org.workcraft.plugins.cpog.VisualVertex$RenderType" name="renderType" value="CIRCLE"/>
      </VisualVertex>
      <VisualComponent>
        <property class="java.awt.Color" name="fillColor" rgb="#ede9fe"/>
        <property class="java.awt.Color" name="foregroundColor" rgb="#0"/>
        <property class="java.lang.String" name="label" value="COMPARATOR"/>
        <property class="java.awt.Color" name="labelColor" rgb="#0"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="labelPositioning" value="TOP"/>
        <property class="java.awt.Color" name="nameColor" rgb="#595959"/>
        <property class="org.workcraft.dom.visual.Positioning" enum-class="org.workcraft.dom.visual.Positioning" name="namePositioning" value="BOTTOM"/>
      </VisualComponent>
      <VisualTransformableNode>
        <property class="java.awt.geom.AffineTransform" matrix="0x1.0p0 0x0.0p0 0x0.0p0 0x1.0p0 0.0 8.5" name="transform"/>
      </VisualTransformableNode>
    </node>

    <!-- Visual Connections -->
    <!-- a_x1_mux1: 10 -> 14 (ref 20, poly 30) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="20">
      <VisualArc ref="a_x1_mux1"/>
      <VisualConnection first="10" ref="a_x1_mux1" second="14">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="30"/>
      </VisualConnection>
    </node>

    <!-- a_nx1_mux1: 11 -> 14 (ref 21, poly 31) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="21">
      <VisualArc ref="a_nx1_mux1"/>
      <VisualConnection first="11" ref="a_nx1_mux1" second="14">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="31"/>
      </VisualConnection>
    </node>

    <!-- a_x2_mux2: 12 -> 15 (ref 22, poly 32) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="22">
      <VisualArc ref="a_x2_mux2"/>
      <VisualConnection first="12" ref="a_x2_mux2" second="15">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="32"/>
      </VisualConnection>
    </node>

    <!-- a_nx2_mux2: 13 -> 15 (ref 23, poly 33) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="23">
      <VisualArc ref="a_nx2_mux2"/>
      <VisualConnection first="13" ref="a_nx2_mux2" second="15">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="33"/>
      </VisualConnection>
    </node>

    <!-- a_mux1_and: 14 -> 16 (ref 24, poly 34) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="24">
      <VisualArc ref="a_mux1_and"/>
      <VisualConnection first="14" ref="a_mux1_and" second="16">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="34"/>
      </VisualConnection>
    </node>

    <!-- a_mux2_and: 15 -> 16 (ref 25, poly 35) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="25">
      <VisualArc ref="a_mux2_and"/>
      <VisualConnection first="15" ref="a_mux2_and" second="16">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="35"/>
      </VisualConnection>
    </node>

    <!-- a_and_acc: 16 -> 17 (ref 26, poly 36) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="26">
      <VisualArc ref="a_and_acc"/>
      <VisualConnection first="16" ref="a_and_acc" second="17">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="36"/>
      </VisualConnection>
    </node>

    <!-- a_acc_cmp: 17 -> 18 (ref 27, poly 37) -->
    <node class="org.workcraft.plugins.cpog.VisualArc" ref="27">
      <VisualArc ref="a_acc_cmp"/>
      <VisualConnection first="17" ref="a_acc_cmp" second="18">
        <property class="double" name="arrowLength" value="0x1.999999999999ap-2"/>
        <property class="double" name="arrowWidth" value="0x1.3333333333333p-3"/>
        <property class="double" name="bubbleSize" value="0x1.999999999999ap-3"/>
        <property class="java.awt.Color" name="color" rgb="#0"/>
        <property class="double" name="lineWidth" value="0x1.47ae147ae147bp-6"/>
        <property class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" enum-class="org.workcraft.dom.visual.connections.VisualConnection$ScaleMode" name="scaleMode" value="NONE"/>
        <property class="boolean" name="tokenColorPropagator" value="false"/>
        <graphic class="org.workcraft.dom.visual.connections.Polyline" ref="37"/>
      </VisualConnection>
    </node>
  </root>
</model>
"""

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

import os

def create_work_files(output_dir="generated"):
    os.makedirs(output_dir, exist_ok=True)
    paths = [
        os.path.join(output_dir, "workcraft_cpog.work"),
        os.path.join(output_dir, "tsetlin_machine_cpog.work")
    ]
    for path in paths:
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("model.xml", model_xml)
            z.writestr("visualModel.xml", visual_xml)
            z.writestr("state.xml", state_xml)
            z.writestr("meta", meta)
        print(f"[generate_tm_work] Successfully generated Workcraft .work file: {path}")
    return paths

if __name__ == "__main__":
    create_work_files()

