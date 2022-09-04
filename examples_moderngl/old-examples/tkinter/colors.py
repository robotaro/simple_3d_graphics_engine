"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import tkinter

# import ModernGL
# import ModernGL.tk

# ctx = ModernGL.create_standalone_context()

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;

#         in vec3 vert_color;
#         out vec3 frag_color;

#         uniform vec2 scale;
#         uniform float rotation;

#         void main() {
#             frag_color = vert_color;
#             mat2 rot = mat2(
#                 cos(rotation), sin(rotation),
#                 -sin(rotation), cos(rotation)
#             );
#             gl_Position = vec4((rot * vert) * scale, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         in vec3 frag_color;
#         out vec4 color;

#         void main() {
#             color = vec4(frag_color, 1.0);
#         }
#     '''),
# ])

# # Uniforms

# scale = prog.uniforms['scale']
# rotation = prog.uniforms['rotation']

# width, height = 512, 512
# scale.value = (height / width * 0.75, 0.75)

# # Buffer

# vbo = ctx.buffer(struct.pack(
#     '15f',

#     1.0, 0.0,
#     1.0, 0.0, 0.0,

#     -0.5, 0.86,
#     0.0, 1.0, 0.0,

#     -0.5, -0.86,
#     0.0, 0.0, 1.0,
# ))

# # Put everything together

# vao = ctx.simple_vertex_array(prog, vbo, ['vert', 'vert_color'])

# # Main loop


# size = (512, 512)
# color_rbo = ctx.renderbuffer(size)
# depth_rbo = ctx.depth_renderbuffer(size)
# fbo = ctx.framebuffer(color_rbo, depth_rbo)

# root = tkinter.Tk()

# # frame = tkinter.Frame(root, width=512, height=512, bg="", colormap="new")
# frame = ModernGL.tk.ModernGLCanvas(root, 512, 512)
# frame.pack()

# # connector = ModernGL.tk.connect(frame)
# R = tkinter.Scale(root, from_=0, to=255, orient=tkinter.HORIZONTAL, length=300)
# R.pack()

# k = 1


# def task():
#     global k
#     k += 0.02
#     fbo.use()
#     ctx.viewport = (0, 0, 512, 512)
#     ctx.clear(0.9, 0.9, 0.9)
#     rotation.value = k
#     vao.render()

#     fbo.read_into(frame.pixels, components=3)
#     frame.update()

#     root.after(1, task)


# root.after(1, task)
# tkinter.mainloop()
