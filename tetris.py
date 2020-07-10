"""
tittle : Practice for python(Pycharm) with Tetris
author : Jang Yun Jae (mealsOrder)
last modified: 2020.07.10


"""

import wx
import random


### 클래스 선언 부분 ###

##테트리스 클래스 생성
class Tetris(wx.Frame):

    ##생성자
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(180, 380), ## 창크기를 180x380으로 설정 및 각종 설정
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.initFrame()  ## 프레임 생성 매서드 실행

    ##프레임 초기화 및 생성 매서드
    def initFrame(self):
        self.statusbar = self.CreateStatusBar()  ## 상태 표시줄 생성
        self.statusbar.SetStatusText('0')  ## 상태 표시줄에 나타날 텍스트
        self.board = Board(self)  ## 보드 생성
        self.board.SetFocus()  ##
        self.board.start()  ## 보드 시작?

        self.SetTitle("Tetris Game")  ## 프레임 제목 설정
        self.Centre()  ## ??(뭔가 중심과 관련되어있을 것같음)


##보드 클래스 생성
class Board(wx.Panel):
    ##보드 기본설정(변수선언)
    BoardWidth = 10
    BoardHeight = 22
    Speed = 300
    ID_TIMER = 1

    ##생성자
    def __init__(self, *args, **kw):  ## 가변매개변수 사용
        super(Board, self).__init__(*args, **kw)

        self.initBoard()

    ##보드 초기화 및 생성 매서드
    def initBoard(self):

        self.timer = wx.Timer(self, Board.ID_TIMER)  ## 타이머 설정
        self.isWaitingAfterLine = False
        self.curPiece = Shape()
        self.nextPiece = Shape()
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

        self.isStarted = False
        self.isPaused = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)  ## 그림그리기 이벤트 묶기
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  ## 키를 눌렀을때 이벤트
        self.Bind(wx.EVT_TIMER, self.OnTimer, id = Board.ID_TIMER)  ## 타이머 묶기

        self.clearBoard()

    ## 모양의 좌표
    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x] ## y좌표 x 보드의 너비 + x좌표

    ## 모양설정 및 모양의 좌표 설정
    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    ## 사각블럭 폭
    def squareWidth(self):
        return self.GetClientSize().GetWidth() // Board.BoardWidth  ## // 연산자 >> 나눈것의 몫만 취함(정수형)

    ## 사각블럭 높이
    def squareHeight(self):

        return self.GetClientSize().GetHeight() // Board.BoardHeight



    ## 시작 함수
    def start(self):

        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()

        self.newPiece()
        self.timer.Start(Board.Speed)


    ## 정지 함수
    def pause(self):

        if not self.isStarted:
            return

        self.isPaused = not self.isPaused
        statusbar = self.GetParent().statusbar

        if self.isPaused:
            self.timer.Stop()
            statusbar.SetStatusText('paused')
        else:
            self.timer.Start(Board.Speed)
            statusbar.SetStatusText(str(self.numLinesRemoved))

        self.Refresh()

    ## 보드 초기화 함수
    def clearBoard(self):
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoes.NoShape)


    ## 그림 그리는 함수
    def OnPaint(self, event):

        dc = wx.PaintDC(self)

        size = self.GetClientSize()
        boardTop = size.GetHeight() - Board.BoardHeight * self.squareHeight()

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):

                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != Tetrominoes.NoShape:
                    self.drawSquare(dc,
                        0 + j * self.squareWidth(),
                        boardTop + i * self.squareHeight(), shape)

        if self.curPiece.shape() != Tetrominoes.NoShape:

            for i in range(4):

                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)

                self.drawSquare(dc, 0 + x * self.squareWidth(),
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight(),
                    self.curPiece.shape())


    ## 키보드 눌렀을때 동작하는 함수
    def OnKeyDown(self, event):

        if not self.isStarted or self.curPiece.shape() == Tetrominoes.NoShape:
            event.Skip()
            return

        keycode = event.GetKeyCode()

        if keycode == ord('P') or keycode == ord('p'):
            self.pause()
            return

        ## R or r 누르면 다시 시작
        if keycode == ord('R') or keycode == ord('r'):
            self.initBoard()
            self.start()
            return

        if self.isPaused:
            return

        elif keycode == wx.WXK_LEFT:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif keycode == wx.WXK_RIGHT:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif keycode == wx.WXK_DOWN:
            self.tryMove(self.curPiece.rotatedRight(), self.curX, self.curY)

        elif keycode == wx.WXK_UP:
            self.tryMove(self.curPiece.rotatedLeft(), self.curX, self.curY)

        elif keycode == wx.WXK_SPACE:
            self.dropDown()

        elif keycode == ord('D') or keycode == ord('d'):
            self.oneLineDown()

        else:
            event.Skip()



    ## 타이머 함수
    def OnTimer(self, event):
        if event.GetId() == Board.ID_TIMER:
            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()

            else:
                self.oneLineDown()

        else:
            event.Skip()

    ## 드롭다운 함수( 바로내리기 함수)
    def dropDown(self):
        newY = self.curY

        while newY > 0:
            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break
            newY -= 1

        self.pieceDropped()

     ## 한줄씩만 내리기 함수
    def oneLineDown(self):

        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()


    def pieceDropped(self):

        for i in range(4):

            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()                  ## 꽉찬 줄 지우기

        if not self.isWaitingAfterLine:
            self.newPiece()

    ## 꽉찬 줄 지우기 함수
    def removeFullLines(self):

        numFullLines = 0

        statusbar = self.GetParent().statusbar

        rowsToRemove = []

        for i in range(Board.BoardHeight):
            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoes.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:
            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

            numFullLines = numFullLines + len(rowsToRemove)

            if numFullLines > 0:

                self.numLinesRemoved = self.numLinesRemoved + numFullLines
                statusbar.SetStatusText(str(self.numLinesRemoved))
                self.isWaitingAfterLine = True
                self.curPiece.setShape(Tetrominoes.NoShape)
                self.Refresh()


    ## 새로운 조각 나오게 하는 함수
    def newPiece(self):

        self.curPiece = self.nextPiece
        statusbar = self.GetParent().statusbar
        self.nextPiece.setRandomShape()

        self.curX = Board.BoardWidth // 2 + 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoes.NoShape)
            self.timer.Stop()
            self.isStarted = False
            statusbar.SetStatusText('Game over')


    ## 블럭을 움직이게 하는 함수
    def tryMove(self, newPiece, newX, newY):

        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoes.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.Refresh()

        return True

    ## 블럭을 그리는 함수(블럭 색상, 밝기 정보 포함)
    def drawSquare(self, dc, x, y, shape):

        colors = ['#000000', '#CC6666', '#66CC66', '#6666CC',
                  '#CCCC66', '#CC66CC', '#66CCCC', '#DAAA00']

        light = ['#000000', '#F89FAB', '#79FC79', '#7979FC',
                 '#FCFC79', '#FC79FC', '#79FCFC', '#FCC600']

        dark = ['#000000', '#803C3B', '#3B803B', '#3B3B80',
                 '#80803B', '#803B80', '#3B8080', '#806200']

        pen = wx.Pen(light[shape])
        pen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(pen)

        dc.DrawLine(x, y + self.squareHeight() - 1, x, y)
        dc.DrawLine(x, y, x + self.squareWidth() - 1, y)

        darkpen = wx.Pen(dark[shape])
        darkpen.SetCap(wx.CAP_PROJECTING)
        dc.SetPen(darkpen)

        dc.DrawLine(x + 1, y + self.squareHeight() - 1,
            x + self.squareWidth() - 1, y + self.squareHeight() - 1)
        dc.DrawLine(x + self.squareWidth() - 1,
        y + self.squareHeight() - 1, x + self.squareWidth() - 1, y + 1)

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(colors[shape]))
        dc.DrawRectangle(x + 1, y + 1, self.squareWidth() - 2,
        self.squareHeight() - 2)




## Tetrominoes 클래스 선언
class Tetrominoes(object):

    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


## Shape클래스 선언
class Shape(object):

    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )


    ## 생성자
    def __init__(self):
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoes.NoShape

        self.setShape(Tetrominoes.NoShape)

    ## shape 함수
    def shape(self):
        return self.pieceShape

    ## shape
    def setShape(self, shape):

        table = Shape.coordsTable[shape]
        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):

        self.setShape(random.randint(1, 7))



    def x(self, index):

        return self.coords[index][0]

    def y(self, index):

        return self.coords[index][1]

    def setX(self, index, x):

        self.coords[index][0] = x

    def setY(self, index, y):

        self.coords[index][1] = y

    def minX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):

        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):

        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):

        m = self.coords[0][1]

        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotatedLeft(self):
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotatedRight(self):
        if self.pieceShape == Tetrominoes.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):
            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result

## 메인 부분 ##
def main():
    app = wx.App()
    ex = Tetris(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

