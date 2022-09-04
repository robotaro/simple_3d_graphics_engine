"""
NOTE: This example is from ModernGL 4 or earlier. We simply disable and archive them for now.
"""

# import struct
# import tkinter as tk

# import ModernGL
# import ModernGL.tk

# ctx = ModernGL.create_standalone_context()

# fbo = ctx.framebuffer(ctx.renderbuffer((512, 512)))

# prog = ctx.program(
#     ctx.vertex_shader('''
#         #version 330

#         in vec2 vert;

#         void main() {
#             gl_Position = vec4(vert, 0.0, 1.0);
#         }
#     '''),
#     ctx.fragment_shader('''
#         #version 330

#         uniform float R;
#         uniform float G;
#         uniform float B;

#         out vec4 color;

#         void main() {
#             color = vec4(B, G, R, 1.0);
#         }
#     '''),
# ])

# vbo = ctx.buffer(struct.pack('6f', 0.0, 0.8, -0.6, -0.8, 0.6, -0.8))
# vao = ctx.simple_vertex_array(prog, vbo, ['vert'])

# root = tk.Tk()
# frame = ModernGL.tk.ModernGLCanvas(root, 512, 512)
# frame.pack()


# def redraw(name, value):
#     prog.uniforms[name].value = value

#     fbo.use()
#     fbo.clear(0.94, 0.94, 0.94)
#     vao.render()

#     fbo.read_into(frame.pixels)
#     frame.update()


# R = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=lambda x: redraw('R', int(x) / 255), length=300)
# G = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=lambda x: redraw('G', int(x) / 255), length=300)
# B = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=lambda x: redraw('B', int(x) / 255), length=300)

# R.pack()
# G.pack()
# B.pack()

# R.set(30)
# G.set(80)
# B.set(200)

# root.mainloop()
