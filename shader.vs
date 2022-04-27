#version 330

layout (location = 0) in vec3 Position;
layout (location = 1) in vec2 TexCoord;


uniform mat4 translationMat;
out vec2 tex_coord;
out vec4 color;
flat out int Vertex_id;

void main()
{
    gl_Position = translationMat * vec4(Position, 1.0);
    Vertex_id = gl_VertexID + 1;
    tex_coord = TexCoord;
}