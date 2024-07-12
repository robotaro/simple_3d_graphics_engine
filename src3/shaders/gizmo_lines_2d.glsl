#version 330

#if defined VERTEX_SHADER

layout(location = 0) in vec2 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in float aSize;

out VertexData {
    noperspective vec2 m_position;
    smooth vec4 m_color;
    noperspective float m_size;
} vData;

void main() {
    vData.m_position = aPosition;
    vData.m_color = aColor;
    vData.m_size = aSize;
    gl_Position = vec4(aPosition, 0.0, 1.0);
}

#elif defined GEOMETRY_SHADER


layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

uniform vec2 uViewport;

in VertexData {
    noperspective vec2 m_position;
    smooth vec4 m_color;
    noperspective float m_size;
} vData[];

out VertexData {
    noperspective vec2 m_position;
    smooth vec4 m_color;
    noperspective float m_size;
    noperspective float m_edgeDistance;
} vDataOut;

void main() {
    vec2 pos0 = vData[0].m_position;
    vec2 pos1 = vData[1].m_position;

    vec2 dir = normalize(pos1 - pos0);
    vec2 tng = vec2(-dir.y, dir.x) * vData[0].m_size / uViewport;

    // Line start
    gl_Position = vec4(pos0 - tng, 0.0, 1.0);
    vDataOut.m_position = pos0 - tng;
    vDataOut.m_edgeDistance = -vData[0].m_size;
    vDataOut.m_size = vData[0].m_size;
    vDataOut.m_color = vData[0].m_color;
    EmitVertex();

    gl_Position = vec4(pos0 + tng, 0.0, 1.0);
    vDataOut.m_position = pos0 + tng;
    vDataOut.m_edgeDistance = vData[0].m_size;
    vDataOut.m_size = vData[0].m_size;
    vDataOut.m_color = vData[0].m_color;
    EmitVertex();

    // Line end
    gl_Position = vec4(pos1 - tng, 0.0, 1.0);
    vDataOut.m_position = pos1 - tng;
    vDataOut.m_edgeDistance = -vData[1].m_size;
    vDataOut.m_size = vData[1].m_size;
    vDataOut.m_color = vData[1].m_color;
    EmitVertex();

    gl_Position = vec4(pos1 + tng, 0.0, 1.0);
    vDataOut.m_position = pos1 + tng;
    vDataOut.m_edgeDistance = vData[1].m_size;
    vDataOut.m_size = vData[1].m_size;
    vDataOut.m_color = vData[1].m_color;
    EmitVertex();

    EndPrimitive();
}

#elif defined FRAGMENT_SHADER


in VertexData {
    noperspective vec2 m_position;
    smooth vec4 m_color;
    noperspective float m_size;
    noperspective float m_edgeDistance;
} vData;

layout(location=0) out vec4 fResult;

void main() {
    fResult = vData.m_color;
    float d = abs(vData.m_edgeDistance) / vData.m_size;
    d = smoothstep(1.0, 1.0 - (2.0 / vData.m_size), d);
    fResult.a *= d;
}

#endif
