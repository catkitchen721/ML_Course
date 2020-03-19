"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    ball_prev = [0, 0]
    m = [0, 0] # slope
    n = 1 # future steps
    fp = 0 # point of fall (x cord)
    new_start = [0, 0] # if ball will hit the wall, create new start point
    GAME_W = 200
    GAME_H = 500
    BALL_R = 5
    BALL_SPEED = ((7, -7), (7, 7), (-7, 7), (-7, -7))
    BOARD_W = 40
    BOARD_H = 5
    BOARD_START = (75, 400)
    BOARD_SPEED = ((5, 0), (-5, 0))
    BRICK_W = 25
    BRICK_H = 10

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if ball_served:
            m[0] = scene_info.ball[0] - ball_prev[0]
            m[1] = scene_info.ball[1] - ball_prev[1]
            if m[1] > 0:
                new_start[0] = scene_info.ball[0]
                new_start[1] = scene_info.ball[1]
                while True:
                    n = (BOARD_START[1] - new_start[1]) / m[1]
                    fp = int(new_start[0] + n * m[0])
                    if (fp >= 0 and fp <= GAME_W):
                        break
                    if (m[0] > 0): # hit right side
                        n = abs((GAME_W - new_start[0]) / m[0])
                        new_start[1] = int(new_start[1] + n * m[1])
                        new_start[0] = GAME_W
                    else:          # hit left side
                        n = abs((0 - new_start[0]) / m[0])
                        new_start[1] = int(new_start[1] + n * m[1])
                        new_start[0] = 0
                    m[0] = -m[0]
        ball_prev[0] = scene_info.ball[0]
        ball_prev[1] = scene_info.ball[1]
        fp -= (BOARD_W / 2)

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            ball_served = True
        else:
            if fp < scene_info.platform[0]:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
