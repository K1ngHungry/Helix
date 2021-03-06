"""
Helix: Flight Test (c) 2021 Andrew Hong
This code is licensed under MIT license (see LICENSE for details)
"""
from Helix.SakuyaEngine.controllers import BaseController

class PlayerController(BaseController):
    def __init__(self) -> None:
        super().__init__()
        self.is_shooting = False