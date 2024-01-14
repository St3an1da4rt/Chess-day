import pygame
import Chess_game

WIDTH = 512
HEIGHT = 512
Count_place_in_row = 8
SQUARE_SIZE = HEIGHT // Count_place_in_row
MAX_FPS = 15
images = {}

def loadimages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        images[piece] = pygame.transform.scale(
            pygame.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE)
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 50, HEIGHT + 100))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("#deff66"))
    gamestate = Chess_game.GameState()

    validMoves = gamestate.get_valid_moves()
    move_made = False
    last_ray = 1

    loadimages()
    running = True
    sqSelected = ()
    playerClicks = []

    gameOver = False
    playerOne = True
    playerTwo = False
    while running:
        isHumanTrun = (gamestate.white_to_move and playerOne) or (
            not gamestate.white_to_move and playerTwo
        )
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTrun:
                    location = pygame.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if (
                        20 <= location[0] <= 160
                        and HEIGHT + 60 <= location[1] <= HEIGHT + 90
                    ):
                        gamestate = Chess_game.GameState()
                        validMoves = gamestate.get_valid_moves()
                        sqSelected = ()
                        playerClicks = []
                        move_made = False
                        gameOver = False
                    elif (
                        180 <= location[0] <= 280
                        and HEIGHT + 60 <= location[1] <= HEIGHT + 90
                    ):
                        gamestate.make_move_back()
                        move_made = True
                    elif (
                        320 <= location[0] <= 440
                        and HEIGHT + 60 <= location[1] <= HEIGHT + 90
                        and isHumanTrun
                    ):
                        AIMove = Chess_game.findBestMoveMinMax(gamestate, validMoves)
                        func_raies = lambda ray: (4 - len(str(ray))) * "0" + str(ray)
                        ray = func_raies(AIMove)

                        join_formater = {0: "a",
                                         1: "b",
                                         2: "c",
                                         3: "d",
                                         4: "e",
                                         5: "f",
                                         6: "g",
                                         7: "h"
                                    }
                        text_best_move = f'{join_formater[int(ray[1])]}{int(ray[0]) + 1} {join_formater[int(ray[3])]}{int(ray[2]) + 1}'
                        read_move_best_for_white(screen, text_best_move)

                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        if row < 8 and col < 8:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = Chess_game.Move(
                            playerClicks[0], playerClicks[1], gamestate.board
                        )
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gamestate.make_move(validMoves[i])
                                move_made = True
                                sqSelected = ()
                                playerClicks = []
                        if not move_made:
                            playerClicks = [sqSelected]

        if not gameOver and not isHumanTrun:
            AIMove = Chess_game.findBestMoveMinMax(gamestate, validMoves)
            func_raies = lambda ray: (4 - len(str(ray))) * "0" + str(ray)
            last_ray_com, ray_com = func_raies(last_ray), func_raies(AIMove)
            bul = last_ray_com[2:] == ray_com[:2] or last_ray_com[:2] == ray_com[2:]
            if bul:
                validMoves.remove(AIMove)
                AIMove = Chess_game.findBestMoveMinMax(gamestate, validMoves)
            if AIMove is None:
                AIMove = Chess_game.findRandomMove(validMoves)
                if AIMove is None:
                    moves = gamestate.getAllPossibleMoves()
                    AIMove = Chess_game.findRandomMove(moves)
            last_ray = AIMove
            gamestate.make_move(AIMove)
            move_made = True

        if move_made:
            validMoves = gamestate.get_valid_moves()
            move_made = False
        drawGameState(screen, gamestate, validMoves, sqSelected)

        if gamestate.checkMate:
            gameOver = True
            if gamestate.white_to_move:
                drawText(screen, "Чёрные победили!")
            else:
                drawText(screen, "Белые  победили!")
        if gamestate.staleMate:
            gameOver = True
            drawText(screen, "Ничья!")

        clock.tick(MAX_FPS)
        pygame.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightsquare(screen, gs, validMoves, sqSelected)
    drawButtons(screen)
    drawPieces(screen, gs.board)


def highlightsquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ("w" if gs.white_to_move else "b"):
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color("blue"))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            s.fill(pygame.Color("yellow"))
            for move in validMoves:
                if move.first_row == row and move.first_col == col:
                    screen.blit(s, (move.last_col * SQUARE_SIZE, move.last_row * SQUARE_SIZE))


def drawBoard(screen):
    colors = [pygame.Color("#FFFF77"), pygame.Color("#77FF77")]
    mat = ["a", "b", "c", "d", "e", "f", "g", "h"]
    pygame.draw.rect(surface=screen,
                     color=pygame.Color("#cdee55"),
                     rect=pygame.Rect(0, HEIGHT, 562, 50))
    pygame.draw.rect(surface=screen,
                     color=pygame.Color("#cdee55"),
                     rect=pygame.Rect(WIDTH, 0, 50, 562))
    for row in range(Count_place_in_row):
        for col in range(Count_place_in_row):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )
        screen.blit(
            pygame.font.SysFont("Calibri", 32).render(str(row + 1), True, color=pygame.Color("#9a9833")),
            (528, row * SQUARE_SIZE + SQUARE_SIZE // 2 - 16),
        )
        screen.blit(
            pygame.font.SysFont("Calibri", 32).render(mat[row], True, color=pygame.Color("#9a9833")),
            (row * SQUARE_SIZE + SQUARE_SIZE // 2 - 10, 518),
        )


def drawButtons(screen):
    button_replay = pygame.Rect(20, HEIGHT + 60, 140, 30)
    pygame.draw.rect(surface=screen, color=pygame.Color("#FFFF77"), rect=button_replay)
    pygame.draw.rect(screen, (100, 100, 100), button_replay, 2)
    screen.blit(
        pygame.font.SysFont("Calibri", 20).render("Играть снова", True, (0, 0, 0)),
        (30, HEIGHT + 65),
    )
    button_game_back = pygame.Rect(180, HEIGHT + 60, 120, 30)
    pygame.draw.rect(
        surface=screen, color=pygame.Color("#FFFF77"), rect=button_game_back
    )
    pygame.draw.rect(screen, (100, 100, 100), button_game_back, 2)
    screen.blit(
        pygame.font.SysFont("Calibri", 20).render("Шаг назад", True, (0, 0, 0)),
        (190, HEIGHT + 65),
    )
    button_best_move = pygame.Rect(320, HEIGHT + 60, 120, 30)
    pygame.draw.rect(surface=screen, color=pygame.Color("#FFFF77"), rect=button_best_move)
    pygame.draw.rect(screen, (100, 100, 100), button_best_move, 2)
    screen.blit(
        pygame.font.SysFont("Calibri", 20).render("Подсказка", True, (0, 0, 0)),
        (330, HEIGHT + 65),
    )


def drawMoves(screen, moves):
    for row in range(Count_place_in_row):
        for col in range(Count_place_in_row):
            for move in moves:
                if move.last_row == row and move.last_col == col:
                    pygame.draw.rect(
                        screen,
                        pygame.Color("red"),
                        pygame.Rect(
                            col * SQUARE_SIZE + 15,
                            row * SQUARE_SIZE + 15,
                            SQUARE_SIZE - 30,
                            SQUARE_SIZE - 30,
                        ),
                    )


def drawPieces(screen, board):
    for row in range(Count_place_in_row):
        for col in range(Count_place_in_row):
            piece = board[row][col]
            if piece != "--":
                screen.blit(
                    images[piece],
                    pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )

def read_move_best_for_white(screen, text):
    button_best_move_text = pygame.Rect(460, HEIGHT + 60, 80, 30)
    pygame.draw.rect(surface=screen, color=pygame.Color("#FFFF77"), rect=button_best_move_text)
    pygame.draw.rect(screen, (100, 100, 100), button_best_move_text, 2)
    font = pygame.font.SysFont("Calibri", 18, False, False)
    textObject = font.render(text, 0, (0, 0, 0))
    screen.blit(textObject, (480, HEIGHT + 65))

def drawText(screen, text):
    pygame.draw.rect(
        screen, pygame.Color("#deff44"), (WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
    )
    pygame.draw.rect(
        screen, (0, 0, 0), (WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200), 3
    )
    font = pygame.font.SysFont("Calibri", 32, True, False)
    textObject = font.render(text, 0, pygame.Color("#a200ff"))
    screen.blit(textObject, (WIDTH // 2 - 130, HEIGHT // 2 - 10))


if __name__ == "__main__":
    main()