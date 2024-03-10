import pygame as pg
import moderngl as mgl

class Texture:
    def __init__(self, ctx, app):
        self.app = app
        self.ctx = ctx
        self.textures = {}
        self.textures[0] = self.get_texture(path='textures/wood.png')
        self.textures[1] = self.get_texture(path='textures/steel.png')
        self.textures[2] = self.get_texture(path='textures/gold.png')
        self.textures['cat'] = self.get_texture(path='objects/20430_cat_diff_v1.jpg')
        self.textures['advanced_skybox'] = self.get_texture_cube(dir_path='textures/skybox/', ext='png')
        self.textures['depth_texture'] = self.get_depth_texture()
        
    def get_depth_texture(self):
        depth_texture = self.ctx.depth_texture(self.app.WIN_SIZE)
        depth_texture.repeat_x = False
        depth_texture.repeat_y = False
        return depth_texture

        
    def get_texture_cube(self, dir_path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        textures = []
        for face in faces:
            texture = pg.image.load(dir_path + f'{face}.{ext}').convert()
            if face in ['right', 'left', 'front', 'back']:
                texture = pg.transform.flip(texture, flip_x=True, flip_y=False)
            else:
                texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
            textures.append(texture)

        size = textures[0].get_size()
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3,
                                   data=pg.image.tostring(texture, 'RGB'))
        # mipmaps
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        # AF
        texture.anisotrophy=32.0
        return texture

    def destroy(self):
        [texture.release() for texture in self.textures.values()]