"""
tittle : Practice for python with Tetris
author : Jang Yun Jae
last modified: 2020.07.02


"""

import wx
import random


### 클래스 선언 부분 ###

##테트리스 클래스 생성
class Tetris(wx.Frame):

    ##생성자
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, size=(180, 380),  ## 창크기를 180x380으로 설정 및 각종 설정
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
        self.nextPuece = Shape()
        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

        self.isStarted = False
        self.isPaused = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)  ## 그림그리기 이벤트 묶기
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  ## 키를 눌렀을때 이벤트
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=Board.ID_TIMER)  ## 타이머 묶기

    ## 모양의 좌표
    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]  ## y좌표 x 보드의 너비 + x좌표

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
        if self.isPaused:  ## 만약 self.isPaused가 참이라면 반환값 없음  << ?? 맞는 표현인가?
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0  ##
        self.clearBoard()

        self.newPiece()
        self.timer.Start(Board.Speed)

    ## 정지 함수
    def pause(self):
        if not self.isPaused:  ## 만약 self.isPaused가 아니 라면 반환값 없음  << ?? 맞는 표현인가?
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
        if not self.inStarted or self.curPieve.shape() == Tetrominoes.NoShape:
            event.Skip()
            return
        keycode = event.GetKeyCode()

        if keycode == ord('P') or keycode == ord('p'):      ## P,p 를 눌렀을때
            self.pause()                                    ## pause
            return

        if self.isPaused:                                   ##
            return

        elif keycode == wx.WXK_LEFT:                                    ## Alt + 왼쪽 방향키 눌럴을때
            self.tryMove(self.curPiece, self.curX - 1, self.curY)       ## x축으로 -1 만큼움직인다.

        elif keycode == wx.WXK_RIGHT:                                   ## Alt + 오른쪽 방향키 눌럴을때
            self.tryMove(self.curPiece, self.curX + 1, self.curY)       ## x축으로 +1 만큼 움직인다.

        elif keycode == wx.WXK_DOWN:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)

        elif keycode == wx. WXK_UP:
            self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif keycode == wx.WXK_SPACE:
            self.dropDown()

        elif keycode == ord('D') or keycode == ord('d'):
            self.oneLineDown()

        else:
            event.Skip()

        def OnTimer(self, event):
            if event.Getld() == Board.ID_TIMER:
                if self.isWaitingAfterLine:
                    self.isWaitingAfterLine = False
                    self.newPiece()
                else:
                    self.oneLineDown()

            else:
                event.Skip()





## 메인 부분 ##

def main():
    app = wx.App()
    ex = Tetris(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

