#!/usr/bin/env python  
# -*- coding:utf-8 -*- 

""" 
@version: v1.0 
@author: Harp
@contact: liutao25@baidu.com 
@software: PyCharm 
@file: MySnake.py 
@time: 2018/1/15 0015 23:40 

游戏是基于PyGame框架制作的，程序核心逻辑如下：

游戏界面分辨率是640*480，蛇和食物都是由1个或多个20*20像素的正方形块儿（为了方便，下文用点表示20*20像素的正方形块儿）组成，这样共有32*24个点，使用pygame.draw.rect来绘制每一个点；
初始化时蛇的长度是3，食物是1个点，蛇初始的移动的方向是右，用一个数组代表蛇，数组的每个元素是蛇每个点的坐标，因此数组的第一个坐标是蛇尾，最后一个坐标是蛇头；
游戏开始后，根据蛇的当前移动方向，将蛇运动方向的前方的那个点append到蛇数组的末位，再把蛇尾去掉，蛇的坐标数组就相当于往前挪了一位；
如果蛇吃到了食物，即蛇头的坐标等于食物的坐标，那么在第2点中蛇尾就不用去掉，就产生了蛇长度增加的效果；食物被吃掉后，随机在空的位置（不能与蛇的身体重合）再生成一个；
通过PyGame的event监控按键，改变蛇的方向，例如当蛇向右时，下一次改变方向只能向上或者向下；
当蛇撞上自身或墙壁，游戏结束，蛇头装上自身，那么蛇坐标数组里就有和舌头坐标重复的数据，撞上墙壁则是蛇头坐标超过了边界，都很好判断；
其他细节：做了个开始的欢迎界面；食物的颜色随机生成；吃到实物的时候有声音提示等。

https://segmentfault.com/a/1190000013583165
https://github.com/Harpsichord1207/MySnake/tree/master



ienlaw 2019年1月31日
主要添加ai,使用a*算法寻找食物

"""


import pygame
from os import path
from sys import exit
from time import sleep
from random import choice
from itertools import product
from pygame.locals import QUIT, KEYDOWN
screen = None



def direction_check(moving_direction, change_direction): #移动方向检查 实际上相对于蛇头的移动只有左右两个方向
    directions = [['up', 'down'], ['left', 'right']]
    if moving_direction in directions[0] and change_direction in directions[1]:
        return change_direction
    elif moving_direction in directions[1] and change_direction in directions[0]:
        return change_direction
    return moving_direction




class Snake:

    colors = list(product([0, 64, 128, 192, 255], repeat=3))[1:-1]

    def __init__(self):#初始化
        self.map = {(x, y): 0 for x in range(32) for y in range(24)}
        
        self.body = [[x*20,100] for x in range(30)]
        self.head = [580, 100] #蛇头 数据
        
        # self.body = [[100, 100], [120, 100], [140, 100]] #蛇身体 数据
        # self.head = [140, 100] #蛇头 数据
        
        self.food = [] #食物
        self.food_color = [] #食物颜色
        self.moving_direction = 'right' #移动方向
        self.speed = 30 #设置一秒钟刷新的次数
        self.generate_food()
        self.game_started = False
        self.path_list = []
        self.gameover = False
        self.gamestart = True

    def check_game_status(self, head=6): #检查状态
    
        if head==6:
            head = self.head
    
        if self.body.count(head) > 1: # 吃到身体判断
            return True
        if head[0] < 0 or head[0] > 620 or head[1] < 0 or head[1] > 460: #撞墙判断
            return True
        return False

    def move_head(self, head=6, moving_direction=6): #移动蛇头
        
        
        if head==6:
            head = self.head
        
        if moving_direction==6:
            moving_direction = self.moving_direction
        
        moves = {
            'right': (20, 0),
            'up': (0, -20),
            'down': (0, 20),
            'left': (-20, 0)
        }
        step = moves[moving_direction]
        head[0] += step[0] #x坐标
        head[1] += step[1] #y坐标

    def generate_food(self): #生成食物
        
        # if len(self.body) // 16 > 4:# 通过蛇身长度来调整速度
            # self.speed = len(self.body) // 16
        # else:
            # self.speed
            
            
        for seg in self.body:
            x, y = seg
            self.map[x//20, y//20] = 1
        empty_pos = [pos for pos in self.map.keys() if not self.map[pos]]
        for pos in self.map.keys():
            self.map[pos] = 0

        
        
        result = choice(empty_pos)
        self.food_color = list(choice(self.colors))
        self.food = [result[0]*20, result[1]*20]

    def finding_food(self):
        '''贪吃蛇ai        
        x.a* 寻路
            在找到食物后，要还能到达蛇尾，否则向空旷区域移动
        
        '''

        
        if len(self.body)>88:
            self.path_list=self.A_path(self.head,[self.food,self.body[0]])
        else:
            self.path_list=self.A_path(self.head,[self.food])# self.body[0] 在找到食物后，要还能到达蛇尾
            
        # self.path_list=self.A_path(self.head,[self.food],free_d=True)
        # print(len(self.path_list),self.path_list)            
        if self.path_list:#path_list不为空
            self.moving_direction = direction_check(self.moving_direction,self.path_list.pop())            
        else:#否则向空旷区域移动
            self.path_list=self.A_path(self.head,[self.food],free_d=True)
            if self.path_list:#path_list不为空
                self.moving_direction = direction_check(self.moving_direction,self.path_list.pop())

            
                
    def A_path(self, a, b_list, free_d=False):
        '''
        A*算法
        搜索区域（The Search Area）：图中的搜索区域被划分为了简单的二维数组，数组每个元素对应一个小方格，当然我们也可以将区域等分成是五角星，矩形等，通常将一个单位的中心点称之为搜索区域节点（Node）。　　
        开放列表(Open List)：我们将路径规划过程中待检测的节点存放于Open List中，而已检测过的格子则存放于Close List中。
        父节点（parent）：在路径规划中用于回溯的节点，开发时可考虑为双向链表结构中的父结点指针。
        路径排序（Path Sorting）：具体往哪个节点移动由以下公式确定：F(n) = G + H 。G代表的是从初始位置A沿着已生成的路径到指定待检测格子的移动开销。H指定待测格子到目标节点B的估计移动开销。
        启发函数（Heuristics Function）：H为启发函数，也被认为是一种试探，由于在找到唯一路径前，我们不确定在前面会出现什么障碍物，因此用了一种计算H的算法，具体根据实际场景决定。在我们简化的模型中，H采用的是传统的曼哈顿距离（Manhattan Distance），也就是横纵向走的距离之和。
        
        
        总结：
        1.把起点加入 open list.
        2.重复如下过程：
            a.遍历open list ，查找F值最小的节点，把它作为当前要处理的节点，然后移到close list中
            b.对当前方格的 8 个相邻方格一一进行检查，如果它是不可抵达的或者它在close list中，忽略它。否则，做如下操作：
                如果它不在open list中，把它加入open list，并且把当前方格设置为它的父亲
                如果它已经在open list中，检查这条路径 ( 即经由当前方格到达它那里 ) 是否更近。如果更近，把它的父亲设置为当前方格，并重新计算它的G和F值。
                如果你的open list是按F值排序的话，改变后你可能需要重新排序。
            c.遇到下面情况停止搜索：
                把终点加入到了 open list 中，此时路径已经找到了，或者
                查找终点失败，并且open list 是空的，此时没有路径。
        3.从终点开始，每个方格沿着父节点移动直至起点，形成路径
        
        F(n) = G + H
        G代表的是从初始位置A沿着已生成的路径到指定待检测格子的移动开销。
        H指定待测格子到目标节点B的估计移动开销。        
        D代表方向 right,left,up,down
        
        a是起点
        b_list是终点 为一个列表提供多个目标节点 [[x,y],[x,y]]
        
        具体实现：
            普通a* 寻找蛇头到达食物最短路径
            反向a* 寻找蛇头到达食物最长路径 模式
            多目标点寻路
                这里先寻找食物再从食物找到蛇尾路径
        
        '''
        
        open_list = []  #待检查列表 内容项解释[x,y,f,g,h,d,father] 
        close_list = [] #内容项同open_list 
        
        #将开始点添加到open_list中
        open_list.append(a_data(x=a[0],y=a[1]))
        # open_list+=get_passage(close_list)

        for b in b_list:
            
            #判断终点已经在close_list中，或open_list为空 结束循环
            while not [b[0],b[1]] in [[i.x,i.y] for i in close_list] and open_list:
                if free_d:
                    #前往空旷区域
                    open_list.sort(reverse = True,key=lambda x:x.f)
                else:
                    # 按照open_list中f排序
                    open_list.sort(key=lambda x:x.f)
                #取出open_list中f最小的值到close_list
                close_list.append(open_list.pop(0))
                
                
                #将开始点周围可通行的点添加到open_list中
                for net_data in get_passage(close_list):
                    if not self.check_game_status([net_data.x,net_data.y]) and not [net_data.x,net_data.y] in [[i.x,i.y] for i in close_list] and not [net_data.x,net_data.y] in self.body[1:]: #判断不是障碍物并且不在close_list中,不在身体障碍物中
                        for open_data in open_list:                            
                            if open_data.x==net_data.x and open_data.y==net_data.y:#判断是否已在open_list中
                                #更新open_list中的f,g,h值
                                if open_data.g > net_data.g:     
                                    open_data.father = net_data.father                                    
                                    net_data.update(b)
                                    break #open_list中已有，不再添加 else不会执行
                        else:
                            #更新net_data中的f,g,h值然后添加到open_list
                            net_data.update(b)
                            open_list.append(net_data)
                    
                if free_d:
                    path_list = [] #从终点返回到起点生成路径结果列表
                    current_point = close_list[-1]
                    while current_point.father != None: #循环判断 当前点父节点不为None则继续循环
                        path_list.append(current_point.d)
                        current_point=current_point.father
                    if len(path_list) > 50:#前往空旷区域 
                        break
            if free_d:
                path_list = [] #从终点返回到起点生成路径结果列表
                current_point = close_list[-1]
                while current_point.father != None: #循环判断 当前点父节点不为None则继续循环
                    path_list.append(current_point.d)
                    current_point=current_point.father
                    #画出close_list路径
                    pygame.draw.rect(screen, self.colors[14], [current_point.x+1, current_point.y+1, 18, 18], 1)
                pygame.display.update()
                if path_list:
                    return [path_list[-1]] #返回第一步操作
                else:
                    return []
                            

                            
            
            #清理close_list 只保留前段路径
            if [close_list[-1].x,close_list[-1].y] == [b[0],b[1]]:
                test_list = [] #从终点返回到起点生成路径结果列表
                current_point = close_list[-1]
                current_point.update(b)
                open_list = []
                open_list.append(current_point)#插入到open_list开头
                current_point=current_point.father
                while current_point.father != None: #循环判断 当前点父节点不为None则继续循环
                    test_list.insert(0,current_point) #插入到列表头部
                    current_point=current_point.father                    
                    
                if test_list:
                    close_list = test_list #更新close_list
            else:#没有找到路径
                #没有找到食物
                if len(b_list)>1:
                    if b == b_list[0]:
                        open_list = []
                        close_list = [] 
                        open_list.append(a_data(x=a[0],y=a[1]))
                        
                    #没有找到蛇尾
                    if b == b_list[-1]:
                        return []
                else:
                    return []
                    
        #补回最后一点
        close_list.append(open_list.pop(0))

        if [close_list[-1].x,close_list[-1].y] == [b_list[-1][0],b_list[-1][1]]:#如果close_list最后一个是终点则生成路径
            path_list = [] #从终点返回到起点生成路径结果列表
            current_point = close_list[-1]
            while current_point.father != None: #循环判断 当前点父节点不为None则继续循环
                path_list.append(current_point.d)
                current_point=current_point.father
                #画出close_list路径
                pygame.draw.rect(screen, [0, 0, 0], [current_point.x+1, current_point.y+1, 18, 18], 1)
            pygame.display.update()
            if path_list:
                return [path_list[-1]] #返回第一步操作
            else:
                return []
        else:
            return []
            
            

        
def get_passage(close_list):
    '''获取一个坐标周边的坐标和方向并检查'''
    moves = {
        'right': (20, 0),
        'up': (0, -20),
        'down': (0, 20),
        'left': (-20, 0)
        }
    test_list = []

    for i in moves:
        test_list.append(a_data(x=close_list[-1].x+moves[i][0],y=close_list[-1].y+moves[i][1],d=i,father=close_list[-1]))
        
    return test_list
        
        
        
class a_data:
    def __init__(self,x=0,y=0,f=0,g=0,h=0,d=0,father=None):
        self.x = x
        self.y = y
        self.f = f
        self.g = g
        self.h = h
        self.d = d
        self.father = father
        
    def update(self,b):
        '''更新f,g,h值'''        
        #g 等于上一个点的g加一
        self.g=self.father.g+1

        #h 等于 当前点到终点的 曼哈顿距离
        self.h = abs(self.x-b[0])+abs(self.y-b[1])
        
        #f 等于 g+h
        self.f = self.g + self.h
        
        
                
def main():
    
    global screen

    key_direction_dict = {
        119: 'up',  # W
        115: 'down',  # S
        97: 'left',  # A
        100: 'right',  # D
        273: 'up',  # UP
        274: 'down',  # DOWN
        276: 'left',  # LEFT
        275: 'right',  # RIGHT
    }

    fps_clock = pygame.time.Clock()
    pygame.init()
    pygame.mixer.init()
    snake = Snake()
    sound = False
    if path.exists('eat.wav'):
        sound_wav = pygame.mixer.Sound("eat.wav")
        sound = True
    title_font = pygame.font.SysFont('SimHei', 32) #使用黑体字体
    welcome_words = title_font.render('欢迎来到贪吃蛇', True, (0, 0, 0), (255, 255, 255))
    tips_font = pygame.font.SysFont('SimHei', 24) #使用黑体字体
    start_game_words = tips_font.render('鼠标点击这里启动游戏', True, (0, 0, 0), (255, 255, 255))
    close_game_words = tips_font.render('按ESC退出游戏', True, (0, 0, 0), (255, 255, 255))
    gameover_words = title_font.render('GAME OVER', True, (205, 92, 92), (255, 255, 255))
    win_words = title_font.render('蛇够长了,你赢了!', True, (0, 0, 205), (255, 255, 255))
    screen = pygame.display.set_mode((640, 480+24), 0, 32)
    pygame.display.set_caption('My Snake 贪吃蛇')
    new_direction = snake.moving_direction
    
    while 1: #游戏主循环
        for event in pygame.event.get():#按键消息处理循环
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == 27: #key=esc 退出游戏
                    exit()
                if snake.game_started and event.key in key_direction_dict:
                    direction = key_direction_dict[event.key]
                    new_direction = direction_check(snake.moving_direction, direction)
                    
            elif snake.gameover and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 0 <= x <= 640 and 0 <= y <= 480+24: #鼠标点击 指定范围 等待结束
                    snake = Snake()
                    new_direction = snake.moving_direction
                    
            elif (not snake.game_started) and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 213 <= x <= 422 and 304 <= y <= 342: #鼠标点击 指定范围 开始游戏
                    snake.game_started = True
        
        
        if snake.game_started:
            # snake.moving_direction = new_direction  # 在这里赋值，而不是在event事件的循环中赋值，避免按键太快
            
            snake.finding_food()#自动找食物
            
            # new_direction = snake.moving_direction
            snake.move_head()
            # snake.body.append(snake.head[:])
            
            snake.body.append(list(snake.head)) #将蛇头的坐标列表复制并添加到蛇身列表中 蛇身+1
            if snake.head == snake.food: #蛇头吃食物判断
                if sound:
                    sound_wav.play()
                snake.generate_food()
                
                # snake.speed+=1 #蛇每吃到一个食物加快一秒刷新次数
            else:
                snake.body.pop(0) #蛇身-1
            
            #画出蛇 和 食物
            for seg in snake.body:
                pygame.draw.rect(screen, [0, 0, 0], [seg[0]+1, seg[1]+1, 18, 18], 0)
            pygame.draw.rect(screen, snake.food_color, [snake.food[0]+2, snake.food[1]+2, 16, 16], 0) #画出食物

            #画出蛇长度
            length = tips_font.render('得分:'+str(len(snake.body)), True, (0, 0, 0), (255, 255, 255))
            screen.blit(length, (0, 480))


            if snake.check_game_status():#蛇死了 画出游戏结束
                snake.gameover = True
                snake.game_started = False
                
            elif len(snake.body) == 512:
                screen.blit(win_words, (33, 210))
                pygame.display.update()
                snake = Snake()
                new_direction = snake.moving_direction
                sleep(3)
        elif snake.gameover: #游戏结束初始化数据
            #画出蛇 和 食物
            for seg in snake.body:
                pygame.draw.rect(screen, [0, 0, 0], [seg[0]+1, seg[1]+1, 18, 18], 0)
            pygame.draw.rect(screen, snake.food_color, [snake.food[0]+2, snake.food[1]+2, 16, 16], 0) #画出食物

            #画出蛇长度
            length = tips_font.render('得分:'+str(len(snake.body)), True, (0, 0, 0), (255, 255, 255))
            screen.blit(length, (0, 480))
        
            screen.blit(gameover_words, (241, 310))
            #画出蛇长度
            length = tips_font.render('得分:'+str(len(snake.body)), True, (0, 0, 0), (255, 255, 255))
            screen.blit(length, (241, 250))
        


                
        elif snake.gamestart:#画出开始界面
            screen.blit(welcome_words, (188, 100))
            screen.blit(start_game_words, (213, 304))
            pygame.draw.rect(screen, [0, 0, 0], [213, 304, start_game_words.get_width(),start_game_words.get_height()], 1)
            screen.blit(close_game_words, (233, 350))
        
        pygame.display.update()
        fps_clock.tick(snake.speed)
        screen.fill((255, 255, 255)) #全屏画白 清空

if __name__ == '__main__':
    main()
