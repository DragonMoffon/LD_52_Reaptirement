from typing import List, Tuple
from math import floor

import arcade.gl as gl
from arcade.gl.geometry import quad_2d
from arcade import ArcadeContext, get_display_size


class LowResFBO(gl.Framebuffer):
    _program: gl.Program = None

    def __init__(self, _ctx: ArcadeContext, size: Tuple[int, int] = None, color_attachments: List[gl.Texture] = None):
        _size = size or get_display_size()
        _color_attachments = color_attachments or [_ctx.texture(size=_size, filter=(gl.NEAREST, gl.NEAREST))]

        super().__init__(_ctx, color_attachments=_color_attachments)
        _display_size = get_display_size()
        _upscale_mod = _display_size[0]/size[0]

        _target_width = floor(_upscale_mod)*size[0]
        _target_height = floor(_upscale_mod)*size[1]

        self._geometry = quad_2d((2.0*_target_width/_display_size[0],
                                  2.0*_target_height/_display_size[1]))

        if LowResFBO._program is None:
            LowResFBO._program = _ctx.program(
                vertex_shader="""
                    #version 330
                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 uv;
                    void main(){
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        uv = in_uv;
                    }                    
                """,
                fragment_shader="""
                    #version 330
                    uniform sampler2D downSampleTexture;
                    in vec2 uv;
                    out vec4 fragColour;
                    void main(){
                        fragColour = texture(downSampleTexture, uv);
                    }
                """
            )

    def draw(self):
        self._color_attachments[0].use(0)
        self._geometry.render(LowResFBO._program)
