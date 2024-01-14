"""
make_move - make_move
first_row - first_row
last_row - last_row
first_col - first_col
last_col - last_col
"""

import random

FigureDefinedScore = {"K": 0, "Q": 10, "N": 3, "R": 5, "P": 1, "B": 3}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMoveMinMax(gs, validMoves):
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.white_to_move)
    return nextMove


def findMoveMinMax(gs, validMoves, depth, white_to_move):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if white_to_move:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)

            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.make_move_back()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.get_valid_moves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)

            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.make_move_back()
        return minScore


def scoreBoard(gs):
    if gs.checkMate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += FigureDefinedScore[square[1]]
            elif square[0] == "b":
                score -= FigureDefinedScore[square[1]]
    return score


def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.white_to_move else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.make_move(playerMove)
        opponentMoves = gs.get_valid_moves()
        if gs.checkMate:
            score = -turnMultiplier * CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.make_move(opponentMove)
                gs.get_valid_moves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = scoreMaterial(gs.board) * -turnMultiplier
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.make_move_back()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.make_move_back()
    return bestPlayerMove


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += FigureDefinedScore[square[1]]
            elif square[0] == "b":
                score -= FigureDefinedScore[square[1]]
    return score


class GameState:
    def __init__(self):
        self.process_castlew = False
        self.process_castleb = False
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {
            "P": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }
        self.white_to_move = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        # self.currentCasltingRight = CastlingRights(True, True, True, True)
        # self.castleRightsLog = [
        #     CastlingRights(
        #         self.currentCasltingRight.wks,
        #         self.currentCasltingRight.bks,
        #         self.currentCasltingRight.wqs,
        #         self.currentCasltingRight.bqs,
        #     )
        # ]

    def make_move(self, move):
        self.board[move.first_row][move.first_col] = "--"
        self.board[move.last_row][move.last_col] = move.pieceMove
        self.movelog.append(move)
        self.white_to_move = not self.white_to_move

        if move.pieceMove == "wK":
            self.whiteKingLocation = (move.last_row, move.last_col)
        elif move.pieceMove == "bK":
            self.blackKingLocation = (move.last_row, move.last_col)

        if move.isPawnPromotion:
            self.board[move.last_row][move.last_col] = move.pieceMove[0] + "Q"

        if move.isEnpassantMove:
            self.board[move.first_row][move.last_col] = "--"

        if move.pieceMove[1] == "P" and abs(move.first_row - move.last_row) == 2:
            self.enpassantPossible = (
                (move.first_row + move.last_row) // 2,
                move.last_col,
            )
        else:
            self.enpassantPossible = ()

        # * Castle Move
        if move.isCastleMove:
            if (move.last_col - move.first_col) == 2:
                self.board[move.last_row][move.last_col - 1] = self.board[
                    move.last_row
                ][move.last_col + 1]
                self.board[move.last_row][move.last_col + 1] = "--"
            else:
                self.board[move.last_row][move.last_col + 1] = self.board[
                    move.last_row
                ][move.last_col - 2]
                self.board[move.last_row][move.last_col - 2] = "--"

        # self.updateCastlRights(move)
        # self.castleRightsLog.append(
        #     CastlingRights(
        #         self.currentCasltingRight.wks,
        #         self.currentCasltingRight.bks,
        #         self.currentCasltingRight.wqs,
        #         self.currentCasltingRight.bqs,
        #     )
        # )

    def make_move_back(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.first_row][move.first_col] = move.pieceMove
            self.board[move.last_row][move.last_col] = move.pieceCaptured
            self.white_to_move = not self.white_to_move

            if move.pieceMove == "wK":
                self.whiteKingLocation = (move.first_row, move.first_col)
            if move.pieceMove == "bK":
                self.blackKingLocation = (move.first_row, move.first_col)

            if move.isEnpassantMove:
                self.board[move.last_row][move.last_col] = "--"
                self.board[move.first_row][move.last_col] = move.pieceCaptured
                self.enpassantPossible = (move.last_row, move.last_col)

            if move.pieceMove[1] == "P" and abs(move.first_row - move.last_row) == 2:
                self.enpassantPossible = ()

            # self.castleRightsLog.pop()
            # self.currentCasltingRight = self.castleRightsLog[-1]

            if move.isCastleMove:
                if (move.last_col - move.first_col) == 2:
                    self.board[move.last_row][move.last_col + 1] = self.board[
                        move.last_row
                    ][move.last_col - 1]
                    self.board[move.last_row][move.last_col - 1] = "--"
                else:
                    self.board[move.last_row][move.last_col - 2] = self.board[
                        move.last_row
                    ][move.last_col + 1]
                    self.board[move.last_row][move.last_col + 1] = "--"
            self.checkMate = False
            self.staleMate = False

    def get_valid_moves(self):

        tempEmpassantPossible = self.enpassantPossible

        # tempCastleRight = CastlingRights(
        #     self.currentCasltingRight.wks,
        #     self.currentCasltingRight.bks,
        #     self.currentCasltingRight.wqs,
        #     self.currentCasltingRight.bqs,
        # )

        moves = self.getAllPossibleMoves()

        if self.white_to_move:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves
            )
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves
            )

        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.inCheckf():

                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.make_move_back()
        if len(moves) == 0:
            if self.inCheckf():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.staleMate = False
            self.checkMate = False

        self.enpassantPossible = tempEmpassantPossible

        return moves

    def inCheckf(self):
        if self.white_to_move:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    def squareUnderAttack(self, r, c):
        self.white_to_move = not self.white_to_move
        oppoenentsMoves = self.getAllPossibleMoves()
        self.white_to_move = not self.white_to_move
        for move in oppoenentsMoves:
            if move.last_row == r and move.last_col == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (
                    turn == "b" and not self.white_to_move
                ):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)

        return moves

    def getPawnMoves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True)
                    )

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True)
                    )

        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True)
                    )

            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True)
                    )

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                last_row = r + d[0] * i
                last_col = c + d[1] * i
                if 0 <= last_row < 8 and 0 <= last_col < 8:
                    endPiece = self.board[last_row][last_col]
                    if endPiece == "--":
                        moves.append(Move((r, c), (last_row, last_col), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (last_row, last_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return 0
        else:
            self.getKingSideCaslteMoves(r, c, moves)
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = (
            (0, -1),
            (0, 1),
            (0, 0),
            (1, 0),
            (1, -1),
            (1, 1),
            (-1, 0),
            (-1, 1),
            (-1, -1),
        )
        allColor = "w" if self.white_to_move else "b"
        for m in kingMoves:
            last_row = r + m[0]
            last_col = c + m[1]
            if 0 <= last_row < 8 and 0 <= last_col < 8:
                endPiece = self.board[last_row][last_col]
                if endPiece[0] != allColor:
                    moves.append(Move((r, c), (last_row, last_col), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                last_row = r + d[0] * i
                last_col = c + d[1] * i
                if 0 <= last_row < 8 and 0 <= last_col < 8:
                    endPiece = self.board[last_row][last_col]
                    if endPiece == "--":
                        moves.append(Move((r, c), (last_row, last_col), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (last_row, last_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenSideCastleMoves(self, row, col, moves):
        if (row == 7 or row == 0) and col == 4:
            if (
                self.board[row][col - 1] == "--"
                and self.board[row][col - 2] == "--"
                and self.board[row][col - 3] == "--"
                and not self.squareUnderAttack(row, col - 1)
                and not self.squareUnderAttack(
                    row, col - 2
                )):
                moves.append(
                    Move((row, col), (row, col - 2), self.board, isCastleMove=True)
                )

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingSideCaslteMoves(self, r, c, moves):
        if r in (7, 0) and c == 4:
            if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
                if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(
                    r, c + 2
                ):
                    moves.append(
                        Move((r, c), (r, c + 2), self.board, isCastleMove=True)
                    )

    def getKnightMoves(self, r, c, moves):
        knightMoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        allColor = "w" if self.white_to_move else "b"
        for m in knightMoves:
            last_row = r + m[0]
            last_col = c + m[1]
            if 0 <= last_row < 8 and 0 <= last_col < 8:
                endPiece = self.board[last_row][last_col]
                if endPiece[0] != allColor:
                    moves.append(Move((r, c), (last_row, last_col), self.board))


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(
        self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False
    ):
        self.first_row = startSq[0]
        self.first_col = startSq[1]
        self.last_row = endSq[0]
        self.last_col = endSq[1]
        self.pieceMove = board[self.first_row][self.first_col]
        self.pieceCaptured = board[self.last_row][self.last_col]
        self.moveID = (
            self.first_row * 1000
            + self.first_col * 100
            + self.last_row * 10
            + self.last_col
        )

        self.isPawnPromotion = (self.pieceMove == "wP" and self.last_row == 0) or (
            self.pieceMove == "bP" and self.last_row == 7
        )

        self.isEnpassantMove = isEnpassantMove

        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMove == "bP" else "bP"
        self.isCastleMove = isCastleMove
    
    def getRankedFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return str(self.moveID)

    def getChessNotation(self):
        return self.getRankedFile(self.first_row, self.first_col) + self.getRankedFile(
            self.last_row, self.last_col
        )