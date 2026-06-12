# =============================================================================
# Lesson 052 — Doom Demo (capstone)
# =============================================================================
# A tiny first-person shooter in the spirit of Doom (1993), assembled almost
# entirely from techniques covered in earlier lessons:
#
#   Textured walls / floor / ceiling .... 016-020  (textures, UV tiling)
#   Maze baked from a text grid ......... 023-024  (world-space geometry)
#   FPS camera locked to the floor ...... 025-026  (yaw-only mouse look)
#   Flashlight following the camera ..... 036-037  (spot light + attenuation)
#   Enemies as 2D billboard sprites ..... 039      (alpha cutout via discard)
#   Sprites always facing the player .... 021      (rotate-Y model matrix)
#   Retro chunky pixel look ............. 018      (NEAREST filtering)
#   HUD: gun, crosshair, damage flash ... 040      (alpha blending)
#   Walls vs sprites depth ordering ..... 038      (depth testing)
#
# The only genuinely NEW ingredients are game logic, not graphics:
#   * grid collision  — clamp movement against wall cells (slide along walls)
#   * hit-scan ray    — step along the view ray to find what a shot hits
#   * enemy "AI"      — walk toward the player when there is line of sight
#
# All sprite artwork (imp, corpse, pistol) is drawn procedurally with
# pygame.draw at startup, so the lesson needs no extra image assets.
#
# Controls:  WASD — move   Mouse — turn   Left click — shoot   Esc — quit
# Goal:      slay all 5 imps before they claw you down.
# =============================================================================

import math
import os
import sys

import glm
import moderngl
import numpy as np
import pygame

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'

pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_PROFILE_MASK,
    pygame.GL_CONTEXT_PROFILE_CORE
)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
pygame.display.set_mode((800, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)
pygame.display.set_caption("052 — Doom Demo")


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


def surface_to_texture(ctx, surface):
    """Upload a pygame Surface drawn at runtime. NEAREST filtering keeps the
    low-res procedural art chunky and pixelated — the retro look is a feature
    (lesson 018)."""
    image = pygame.transform.flip(surface, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.filter   = (moderngl.NEAREST, moderngl.NEAREST)
    tex.repeat_x = False
    tex.repeat_y = False
    return tex


# =============================================================================
# Map — '#' wall, '.' floor, 'P' player spawn, 'E' enemy spawn.
# Edit freely: the maze geometry is rebuilt from this grid at startup.
# =============================================================================
MAP = [
    "################",
    "#P.....#.....E.#",
    "#.###..#..###..#",
    "#.#....#....#..#",
    "#.#..#####..#..#",
    "#....#......#..#",
    "#.E..#..##..#E.#",
    "#....#..#......#",
    "#.#####.#..#####",
    "#.....E.#..#..E#",
    "#..............#",
    "################",
]
MAP_ROWS = len(MAP)
MAP_COLS = len(MAP[0])

CELL   = 2.0   # world units per map cell
WALL_H = 2.5   # wall / ceiling height
EYE    = 1.0   # camera height above the floor


def is_wall(col, row):
    if col < 0 or col >= MAP_COLS or row < 0 or row >= MAP_ROWS:
        return True
    return MAP[row][col] == '#'


def is_wall_at(x, z):
    return is_wall(int(x // CELL), int(z // CELL))


def collides(x, z, radius):
    """Circle vs. wall grid, approximated by the four corners of the
    bounding square — plenty for cell-sized corridors."""
    for dx in (-radius, radius):
        for dz in (-radius, radius):
            if is_wall_at(x + dx, z + dz):
                return True
    return False


def try_move(pos, delta, radius):
    """Move a vec2 (x, z) with collision, one axis at a time so blocked
    movement slides along the wall instead of sticking to it."""
    if not collides(pos.x + delta.x, pos.y, radius):
        pos.x += delta.x
    if not collides(pos.x, pos.y + delta.y, radius):
        pos.y += delta.y


def line_of_sight(a, b):
    """Step along the segment a→b (both vec2) sampling the grid. The same
    check serves enemy vision and bullet wall-blocking."""
    dist = glm.length(b - a)
    if dist < 1e-6:
        return True
    step = glm.normalize(b - a) * 0.1
    p = glm.vec2(a)
    for _ in range(int(dist / 0.1)):
        p += step
        if is_wall_at(p.x, p.y):
            return False
    return True


def build_world_mesh():
    """Bake the maze into world-space triangles: pos(3f) normal(3f) uv(2f).
    Returns (walls, floor, ceiling) arrays. Only wall faces that border an
    open cell are emitted — interior faces could never be seen."""
    walls = []

    def quad(p0, p1, p2, p3, n, u_max, v_max):
        # Two triangles; UVs tile so texels stay square on every face.
        uv = [(0, 0), (u_max, 0), (u_max, v_max), (0, v_max)]
        for i in (0, 1, 2, 0, 2, 3):
            walls.extend((p0, p1, p2, p3)[i] + n + uv[i])

    v_rep = WALL_H / CELL  # vertical texture repeats on a wall face
    for r in range(MAP_ROWS):
        for c in range(MAP_COLS):
            if MAP[r][c] != '#':
                continue
            x0, x1 = c * CELL, (c + 1) * CELL
            z0, z1 = r * CELL, (r + 1) * CELL
            if not is_wall(c - 1, r):  # west face
                quad((x0, 0, z1), (x0, 0, z0), (x0, WALL_H, z0), (x0, WALL_H, z1),
                     (-1, 0, 0), 1, v_rep)
            if not is_wall(c + 1, r):  # east face
                quad((x1, 0, z0), (x1, 0, z1), (x1, WALL_H, z1), (x1, WALL_H, z0),
                     (1, 0, 0), 1, v_rep)
            if not is_wall(c, r - 1):  # north face (-z)
                quad((x0, 0, z0), (x1, 0, z0), (x1, WALL_H, z0), (x0, WALL_H, z0),
                     (0, 0, -1), 1, v_rep)
            if not is_wall(c, r + 1):  # south face (+z)
                quad((x1, 0, z1), (x0, 0, z1), (x0, WALL_H, z1), (x1, WALL_H, z1),
                     (0, 0, 1), 1, v_rep)

    def flat(y, n, u_max, v_max):
        x1, z1 = MAP_COLS * CELL, MAP_ROWS * CELL
        out = []
        corners = [(0, y, 0), (x1, y, 0), (x1, y, z1), (0, y, z1)]
        uv = [(0, 0), (u_max, 0), (u_max, v_max), (0, v_max)]
        for i in (0, 1, 2, 0, 2, 3):
            out.extend(corners[i] + n + uv[i])
        return np.array(out, dtype='f4')

    return (np.array(walls, dtype='f4'),
            flat(0.0,    (0, 1, 0),  MAP_COLS, MAP_ROWS),
            flat(WALL_H, (0, -1, 0), MAP_COLS, MAP_ROWS))


# =============================================================================
# Procedural sprite art — drawn once at startup with pygame.draw.
# =============================================================================
def make_imp_surface():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    BODY = (124, 62, 48)
    DARK = (88, 40, 32)
    BONE = (230, 220, 200)
    EYES = (255, 220, 60)
    pygame.draw.rect(s, DARK, (22, 50, 8, 14))                      # legs
    pygame.draw.rect(s, DARK, (34, 50, 8, 14))
    pygame.draw.ellipse(s, BODY, (16, 22, 32, 32))                  # torso
    pygame.draw.ellipse(s, BODY, (8, 26, 10, 22))                   # arms
    pygame.draw.ellipse(s, BODY, (46, 26, 10, 22))
    pygame.draw.circle(s, BONE, (13, 50), 3)                        # claws
    pygame.draw.circle(s, BONE, (51, 50), 3)
    pygame.draw.circle(s, BODY, (32, 16), 11)                       # head
    pygame.draw.polygon(s, BONE, [(22, 12), (16, 0), (26, 8)])      # horns
    pygame.draw.polygon(s, BONE, [(42, 12), (48, 0), (38, 8)])
    pygame.draw.circle(s, EYES, (27, 14), 3)                        # eyes
    pygame.draw.circle(s, EYES, (37, 14), 3)
    pygame.draw.rect(s, (40, 12, 12), (27, 21, 10, 4))              # mouth
    pygame.draw.rect(s, BONE, (28, 21, 2, 2))                       # teeth
    pygame.draw.rect(s, BONE, (34, 21, 2, 2))
    return s


def make_imp_dead_surface():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (110, 20, 20), (8, 50, 48, 12))          # puddle
    pygame.draw.ellipse(s, (80, 14, 14), (16, 53, 24, 7))
    pygame.draw.polygon(s, (230, 220, 200), [(44, 54), (50, 46), (48, 56)])
    return s


def make_gun_surface(flash):
    s = pygame.Surface((128, 128), pygame.SRCALPHA)
    GRAY  = (70, 70, 78)
    LIGHT = (105, 105, 115)
    HAND  = (196, 150, 110)
    if flash:  # muzzle star behind the barrel tip
        pts = []
        for i in range(10):
            r = 24 if i % 2 == 0 else 9
            a = i * math.pi / 5
            pts.append((64 + r * math.sin(a), 24 + r * math.cos(a)))
        pygame.draw.polygon(s, (255, 230, 90), pts)
        pygame.draw.circle(s, (255, 255, 220), (64, 24), 7)
    pygame.draw.rect(s, GRAY, (56, 34, 16, 50))                     # barrel
    pygame.draw.rect(s, LIGHT, (53, 30, 22, 12))                    # muzzle
    pygame.draw.polygon(s, GRAY, [(48, 84), (80, 84), (94, 128), (34, 128)])
    pygame.draw.polygon(s, LIGHT, [(56, 84), (72, 84), (80, 128), (48, 128)])
    pygame.draw.ellipse(s, HAND, (28, 100, 30, 28))                 # hands
    pygame.draw.ellipse(s, HAND, (70, 100, 30, 28))
    return s


def make_text_texture(ctx, text, px, color):
    font = pygame.font.SysFont('impact,arialblack,arial', px, bold=True)
    surf = font.render(text, True, color)
    return surface_to_texture(ctx, surf), surf.get_size()


# Unit billboard quad: 1 wide, 1 tall, base at y=0, facing +z (lesson 039).
SPRITE_VERTS = np.array([
    -0.5, 0.0, 0.0,  0.0, 0.0,
     0.5, 0.0, 0.0,  1.0, 0.0,
     0.5, 1.0, 0.0,  1.0, 1.0,
    -0.5, 0.0, 0.0,  0.0, 0.0,
     0.5, 1.0, 0.0,  1.0, 1.0,
    -0.5, 1.0, 0.0,  0.0, 1.0,
], dtype='f4')

# Unit HUD quad in 2D, centered on the origin; placed via u_pos / u_scale.
HUD_VERTS = np.array([
    -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5,  1.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5, -0.5,  0.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.0, 1.0,
], dtype='f4')


class Enemy:
    SPEED  = 1.8
    RADIUS = 0.45
    SIGHT  = 14.0
    REACH  = 1.3   # closer than this and it claws the player

    def __init__(self, x, z):
        self.pos   = glm.vec2(x, z)
        self.alive = True


class Scene:
    PLAYER_RADIUS = 0.4
    PLAYER_SPEED  = 5.0
    FIRE_COOLDOWN = 0.35
    HIT_RADIUS    = 0.5   # how forgiving the hit-scan is
    CLAW_DAMAGE   = 15

    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.world_program = self.ctx.program(
            vertex_shader=load_shader('shaders/world.vert'),
            fragment_shader=load_shader('shaders/world.frag'),
        )
        self.sprite_program = self.ctx.program(
            vertex_shader=load_shader('shaders/sprite.vert'),
            fragment_shader=load_shader('shaders/sprite.frag'),
        )
        self.hud_program = self.ctx.program(
            vertex_shader=load_shader('shaders/hud.vert'),
            fragment_shader=load_shader('shaders/hud.frag'),
        )

        # --- world geometry: one static VBO per surface kind --------------
        walls, floor, ceiling = build_world_mesh()
        self.world_vaos = []  # (vao, tint)
        for verts, tint in ((walls,   (1.0, 1.0, 1.0)),
                            (floor,   (0.45, 0.45, 0.50)),
                            (ceiling, (0.22, 0.22, 0.28))):
            vbo = self.ctx.buffer(verts)
            vao = self.ctx.vertex_array(
                self.world_program,
                [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')])
            self.world_vaos.append((vao, tint))

        self.wall_texture = load_texture(self.ctx, '../images/wall.jpg')

        # --- sprite + HUD quads --------------------------------------------
        sprite_vbo = self.ctx.buffer(SPRITE_VERTS)
        self.sprite_vao = self.ctx.vertex_array(
            self.sprite_program, [(sprite_vbo, '3f 2f', 'in_position', 'in_uv')])

        hud_vbo = self.ctx.buffer(HUD_VERTS)
        self.hud_vao = self.ctx.vertex_array(
            self.hud_program, [(hud_vbo, '2f 2f', 'in_position', 'in_uv')])

        # --- procedural textures -------------------------------------------
        self.imp_texture      = surface_to_texture(self.ctx, make_imp_surface())
        self.imp_dead_texture = surface_to_texture(self.ctx, make_imp_dead_surface())
        self.gun_texture      = surface_to_texture(self.ctx, make_gun_surface(False))
        self.gun_fire_texture = surface_to_texture(self.ctx, make_gun_surface(True))
        self.died_texture, self.died_size = make_text_texture(
            self.ctx, "YOU DIED", 72, (200, 30, 30))
        self.win_texture, self.win_size = make_text_texture(
            self.ctx, "ALL DEMONS SLAIN", 56, (255, 210, 80))

        # --- camera + lighting ---------------------------------------------
        projection = glm.perspective(glm.radians(60.0), 800.0 / 600.0, 0.1, 100.0)
        for prog in (self.world_program, self.sprite_program):
            prog['projection'].write(projection)
            prog['light.cut_off']       = math.cos(math.radians(14.0))
            prog['light.outer_cut_off'] = math.cos(math.radians(22.0))
            prog['light.ambient']       = (0.12, 0.12, 0.14)
            prog['light.diffuse']       = (1.0, 0.95, 0.85)
            prog['light.constant']      = 1.0
            prog['light.linear']        = 0.09
            prog['light.quadratic']     = 0.032

        # --- game state from the map ----------------------------------------
        self.enemies = []
        self.player_pos = glm.vec2(CELL * 1.5, CELL * 1.5)
        for r, row in enumerate(MAP):
            for c, ch in enumerate(row):
                center = glm.vec2((c + 0.5) * CELL, (r + 0.5) * CELL)
                if ch == 'P':
                    self.player_pos = center
                elif ch == 'E':
                    self.enemies.append(Enemy(center.x, center.y))

        self.yaw         = 0.0    # degrees; 0 looks toward +x
        self.sensitivity = 0.12
        self.hp          = 100
        self.dead        = False
        self.won         = False
        self.fire_cd     = 0.0    # time until the next shot is allowed
        self.flash_timer = 0.0    # muzzle flash visibility
        self.hurt_timer  = 0.0    # red screen flash decay
        self.hurt_cd     = 0.0    # invulnerability window between claws
        self.bob_phase   = 0.0    # gun bobbing while walking

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    # ------------------------------------------------------------------ input
    def front(self):
        return glm.vec3(math.cos(glm.radians(self.yaw)), 0.0,
                        math.sin(glm.radians(self.yaw)))

    def handle_mouse(self, dx):
        # Yaw only — classic Doom had no vertical look either.
        self.yaw += dx * self.sensitivity

    def shoot(self):
        if self.dead or self.fire_cd > 0.0:
            return
        self.fire_cd     = self.FIRE_COOLDOWN
        self.flash_timer = 0.07

        f = self.front()
        direction = glm.vec2(f.x, f.z)
        origin    = glm.vec2(self.player_pos)

        # Hit-scan part 1: march along the ray until a wall cell stops it.
        wall_dist = 0.0
        p = glm.vec2(origin)
        while wall_dist < 60.0 and not is_wall_at(p.x, p.y):
            p += direction * 0.05
            wall_dist += 0.05

        # Hit-scan part 2: nearest enemy whose center lies close enough to
        # the ray, in front of us, and not behind the wall we hit.
        target = None
        best   = wall_dist
        for e in self.enemies:
            if not e.alive:
                continue
            to_e = e.pos - origin
            proj = glm.dot(to_e, direction)          # distance along the ray
            if 0.0 < proj < best:
                perp = glm.length(to_e - direction * proj)
                if perp < self.HIT_RADIUS:
                    target, best = e, proj
        if target is not None:
            target.alive = False
            if all(not e.alive for e in self.enemies):
                self.won = True

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.fire_cd     = max(0.0, self.fire_cd - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        self.hurt_timer  = max(0.0, self.hurt_timer - dt)
        self.hurt_cd     = max(0.0, self.hurt_cd - dt)

        if self.dead:
            return

        # Player movement on the XZ plane (lesson 026), with wall sliding.
        keys  = pygame.key.get_pressed()
        f     = self.front()
        fwd   = glm.vec2(f.x, f.z)
        right = glm.vec2(-fwd.y, fwd.x)
        move  = glm.vec2(0.0, 0.0)
        if keys[pygame.K_w]: move += fwd
        if keys[pygame.K_s]: move -= fwd
        if keys[pygame.K_a]: move -= right
        if keys[pygame.K_d]: move += right
        if glm.length(move) > 0.0:
            move = glm.normalize(move) * self.PLAYER_SPEED * dt
            try_move(self.player_pos, move, self.PLAYER_RADIUS)
            self.bob_phase += dt * 9.0

        # Enemy "AI": see player -> walk at them; touch player -> claw.
        for e in self.enemies:
            if not e.alive:
                continue
            to_p = self.player_pos - e.pos
            dist = glm.length(to_p)
            if dist < Enemy.REACH:
                if self.hurt_cd <= 0.0:
                    self.hp        -= self.CLAW_DAMAGE
                    self.hurt_cd    = 0.8
                    self.hurt_timer = 0.5
                    if self.hp <= 0:
                        self.hp   = 0
                        self.dead = True
            elif dist < Enemy.SIGHT and line_of_sight(e.pos, self.player_pos):
                step = glm.normalize(to_p) * Enemy.SPEED * dt
                try_move(e.pos, step, Enemy.RADIUS)

    # ----------------------------------------------------------------- render
    def draw_hud_quad(self, pos, scale, color, texture=None):
        self.hud_program['u_pos']      = pos
        self.hud_program['u_scale']    = scale
        self.hud_program['u_color']    = color
        self.hud_program['u_textured'] = texture is not None
        if texture is not None:
            texture.use(location=0)
        self.hud_vao.render()

    def render(self, dt):
        self.update(dt)

        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.disable(moderngl.BLEND)

        eye   = glm.vec3(self.player_pos.x, EYE, self.player_pos.y)
        front = self.front()
        view  = glm.lookAt(eye, eye + front, glm.vec3(0.0, 1.0, 0.0))
        for prog in (self.world_program, self.sprite_program):
            prog['view'].write(view)
            prog['light.position']  = tuple(eye)    # flashlight = camera (037)
            prog['light.direction'] = tuple(front)

        # --- pass 1: maze ---------------------------------------------------
        self.wall_texture.use(location=0)
        for vao, tint in self.world_vaos:
            self.world_program['u_tint'] = tint
            vao.render()

        # --- pass 2: enemy billboards ----------------------------------------
        # Each sprite is rotated about Y to face the camera (lesson 021's
        # transforms + lesson 025's camera). Discard handles the cutout, so
        # draw order between sprites does not matter (lesson 039).
        for e in self.enemies:
            to_cam = eye - glm.vec3(e.pos.x, 0.0, e.pos.y)
            angle  = math.atan2(to_cam.x, to_cam.z)
            model  = glm.translate(glm.mat4(1.0), glm.vec3(e.pos.x, 0.0, e.pos.y))
            model  = glm.rotate(model, angle, glm.vec3(0.0, 1.0, 0.0))
            model  = glm.scale(model, glm.vec3(1.5, 1.9, 1.0))
            self.sprite_program['model'].write(model)
            tex = self.imp_texture if e.alive else self.imp_dead_texture
            tex.use(location=0)
            self.sprite_vao.render()

        # --- pass 3: HUD overlay (lesson 040: alpha blending) ----------------
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        # pistol with walk bob; swap in the muzzle-flash frame while firing
        bob = abs(math.sin(self.bob_phase)) * 0.04
        gun = self.gun_fire_texture if self.flash_timer > 0.0 else self.gun_texture
        self.draw_hud_quad((0.08, -0.575 - bob), (0.64, 0.85),
                           (1.0, 1.0, 1.0, 1.0), gun)

        # crosshair
        self.draw_hud_quad((0.0, 0.0), (0.045, 0.007), (0.9, 0.9, 0.9, 0.8))
        self.draw_hud_quad((0.0, 0.0), (0.005, 0.060), (0.9, 0.9, 0.9, 0.8))

        # health bar (background + fill anchored to its left edge)
        frac = self.hp / 100.0
        self.draw_hud_quad((-0.62, -0.88), (0.64, 0.07), (0.15, 0.04, 0.04, 0.85))
        if frac > 0.0:
            width = 0.62 * frac
            self.draw_hud_quad((-0.93 + width / 2.0, -0.88), (width, 0.05),
                               (0.85, 0.12, 0.12, 0.9))

        # red damage flash (constant overlay once dead)
        alpha = 0.45 if self.dead else min(self.hurt_timer, 0.5)
        if alpha > 0.0:
            self.draw_hud_quad((0.0, 0.0), (2.0, 2.0), (0.7, 0.0, 0.0, alpha))

        # end-state banner
        if self.dead or self.won:
            tex, (w, h) = ((self.died_texture, self.died_size) if self.dead
                           else (self.win_texture, self.win_size))
            self.draw_hud_quad((0.0, 0.15), (w / 400.0, h / 300.0),
                               (1.0, 1.0, 1.0, 1.0), tex)


scene = Scene()
clock = pygame.time.Clock()

while True:
    # Clamp dt so a dragged window doesn't teleport enemies through walls.
    dt = min(clock.tick(60) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            scene.handle_mouse(event.rel[0])
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            scene.shoot()

    scene.render(dt)
    pygame.display.flip()
