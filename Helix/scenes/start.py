"""
Helix: Flight Test (c) 2021 Andrew Hong
This code is licensed under MIT license (see LICENSE for details)
"""
import sys
import pygame

from Helix.SakuyaEngine.entity import load_entity_json
from Helix.SakuyaEngine.scene import Scene
from Helix.SakuyaEngine.math import Vector
from Helix.SakuyaEngine.particles import Particles
from Helix.SakuyaEngine.waves import load_wave_file
from Helix.SakuyaEngine.errors import SceneNotActiveError
from Helix.SakuyaEngine.lights import spotlight
from Helix.SakuyaEngine.text import text2

from Helix.wavemanager import HelixWaves
from Helix.buttons import KEYBOARD, NS_CONTROLLER
from Helix.playercontroller import PlayerController
from Helix.const import *

class Start(Scene):
    def on_awake(self) -> None:
        win_size = self.client.original_window_size
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            print(f"Console Controller Detected! [{self.joystick.get_name()}]")
        
        # Load sounds
        pygame.mixer.init()
        pygame.mixer.set_num_channels(64)
        self.laser_1 = pygame.mixer.Sound("Helix\\audio\\laser-1.mp3")

        self.wave_manager = HelixWaves(30000)
        self.wave_manager.spawn_points = [
            Vector(int(win_size.x * 1/5), int(win_size.y * 1/4)),
            Vector(int(win_size.x * 1/3), int(win_size.y * 1/7)),
            Vector(int(win_size.x * 1/2), int(win_size.y * 1/7)),
            Vector(int(win_size.x * 2/3), int(win_size.y * 1/7)),
            Vector(int(win_size.x * 4/5), int(win_size.y * 1/4))
        ]

        self.player_entity = load_entity_json("Helix\\data\\entity\\helix.json")
        self.player_entity.position = Vector(win_size.x/2, win_size.y/2)
        self.player_entity.controller = PlayerController()
        self.player_entity.anim_set("idle_anim")
        player_rect = self.player_entity.rect
        self.player_entity.particle_systems = [
            Particles(
                Vector(0, 2),
                colors = [
                    (249, 199, 63),
                    (255, 224, 70),
                    (255, 78, 65)
                ],
                offset = Vector(
                    player_rect.width/2,
                    player_rect.height * 1/4
                ),
                particles_num = 20,
                spread = 1,
                lifetime = 1000
            )
        ]

        self.entities.append(self.player_entity)

        self.wave_manager.entities = [
            load_entity_json("Helix\\data\\entity\\ado.json")
        ]

        load_wave_file("Helix\waves\w1.wave", self.wave_manager, self)

    def input(self) -> None:
        controller = self.player_entity.controller
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == KEYBOARD["left"]:
                    controller.is_moving_left = True
                if event.key == KEYBOARD["right"]:
                    controller.is_moving_right = True
                if event.key == KEYBOARD["up"]:
                    controller.is_moving_up = True
                if event.key == KEYBOARD["down"]:
                    controller.is_moving_down = True
                if event.key == KEYBOARD["A"]:
                    controller.is_shooting = True
            if event.type == pygame.KEYUP:
                if event.key == KEYBOARD["left"]:
                    controller.is_moving_left = False
                    self.player_entity.velocity.x = 0
                if event.key == KEYBOARD["right"]:
                    controller.is_moving_right = False
                    self.player_entity.velocity.x = 0
                if event.key == KEYBOARD["up"]:
                    controller.is_moving_up = False
                    self.player_entity.velocity.y = 0
                if event.key == KEYBOARD["down"]:
                    controller.is_moving_down = False
                    self.player_entity.velocity.y = 0
                if event.key == KEYBOARD["A"]:
                    controller.is_shooting = False

            if event.type == pygame.JOYBUTTONDOWN:
                if self.joystick.get_button(NS_CONTROLLER["left"]) == 1:
                    controller.is_moving_left = True
                if self.joystick.get_button(NS_CONTROLLER["right"]) == 1:
                    controller.is_moving_right = True
                if self.joystick.get_button(NS_CONTROLLER["up"]) == 1:
                    controller.is_moving_up = True
                if self.joystick.get_button(NS_CONTROLLER["down"]) == 1:
                    controller.is_moving_down = True
                if self.joystick.get_button(NS_CONTROLLER["A"]) == 1:
                    controller.is_shooting = True

            if event.type == pygame.JOYBUTTONUP:
                if self.joystick.get_button(NS_CONTROLLER["left"]) == 0:
                    controller.is_moving_left = False
                    self.player_entity.velocity.x = 0
                if self.joystick.get_button(NS_CONTROLLER["right"]) == 0:
                    controller.is_moving_right = False
                    self.player_entity.velocity.x = 0
                if self.joystick.get_button(NS_CONTROLLER["up"]) == 0:
                    controller.is_moving_up = False
                    self.player_entity.velocity.y = 0
                if self.joystick.get_button(NS_CONTROLLER["down"]) == 0:
                    controller.is_moving_down = False
                    self.player_entity.velocity.y = 0
                if self.joystick.get_button(NS_CONTROLLER["A"]) == 0:
                    controller.is_shooting = False

    def update(self) -> None:
        self.input()
        controller = self.player_entity.controller

        self.client.screen.fill((100, 118, 236))

        # Player shooting
        if controller.is_shooting:
            bs = self.player_entity.bullet_spawners[0]
            if bs.can_shoot:
                self.bullets.append(bs.shoot_with_firerate(-90))
                pygame.mixer.Sound.play(self.laser_1)
        
        # Render Player Particles
        for ps in self.player_entity.particle_systems:
            ps.render(self.client.screen)

        # Test for collisions
        collided = self.test_collisions(self.player_entity)
        for c in collided:
            if "enemy_bullet" in c.tags:
                try:
                    self.client.replace_scene("Start", "Death")
                except SceneNotActiveError:
                    pass
                self.bullets.remove(c)

        for b in self.bullets:
            self.client.screen.blit(b.sprite, b.position.to_list())
            spotlight(self.client.screen, b.position + b.center_offset, (20, 0, 20), 10)
            #pygame.draw.rect(self.client.screen, (0, 255, 0), b.custom_hitbox, 1)

        for e in self.entities:
            # Update health
            # TODO: Optimize this. This is the main reason why the game is capped at 30fps.
            if "enemy" in e.tags:
                collided = self.test_collisions(e)
                for c in collided:
                    if "player_bullet" in c.tags:
                        e.current_health -= c.damage
                        self.bullets.remove(c)

                        if e.current_health <= 0:
                            e._is_destroyed = True

            # Draw
            self.client.screen.blit(e.sprite, e.position.to_list())
            # TODO: Implement this in Entity
            if e.draw_healthbar:
                bar_length = e.rect.width * 0.7
                bar_pos = e.position + e.healthbar_position_offset + e.center_offset - Vector(bar_length / 2 - 1, e.rect.height * (2 / 3))
                display_hp = (e.healthbar.display_health / e._max_health) * bar_length
                pygame.draw.rect(self.client.screen, (0, 230, 0), pygame.Rect(
                    bar_pos.x, bar_pos.y, display_hp, 1
                ))
                pygame.draw.rect(self.client.screen, (0, 190, 0), pygame.Rect(
                    bar_pos.x, bar_pos.y + 1, display_hp, 1
                ))

        # for sp in self.wave_manager.spawn_points: self.client.screen.set_at(sp.to_list(), (255,255,255))
        # for e in self.entities: pygame.draw.rect(self.client.screen, (0, 255, 0), e.custom_hitbox, 1)

        for p in self.particle_systems:
            p.render(self.client.screen)
            p.update(self.client.delta_time)

        self.event_system.update()
        self.advance_frame(self.client.delta_time)

        fps = text2(f"fps: {int(self.client.pg_clock.get_fps())}", 10, font5x3, (0, 255, 0))
        object_count = text2(f"object count: {len(self.entities)}", 10, font5x3, (0, 255, 0))
        bullet_count = text2(f"bullet count: {len(self.bullets)}", 10, font5x3, (0, 255, 0))
        self.client.screen.blit(fps, (0, 0))
        self.client.screen.blit(object_count, (0, 10))
        self.client.screen.blit(bullet_count, (0, 20))