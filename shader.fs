#version 330

layout (location = 0) out vec4 FragColor;
layout (location = 1) out int index;

flat in int Vertex_id;
in vec4 color;
in vec2 tex_coord;
uniform sampler2D sampler2;

void main()
{
    FragColor = vec4(1,0,0,1);
    index = Vertex_id;
}